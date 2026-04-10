"""
Enhanced Audit Logging Utility for KIU Admission Portal
Provides comprehensive audit trail functionality
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from flask import request, g, has_request_context
from models import db, AuditLog, User

logger = logging.getLogger(__name__)


def get_client_ip() -> str:
    """Get client IP address from request"""
    if not has_request_context():
        return None
    
    # Check for forwarded IP (behind proxy)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    
    return request.remote_addr


def get_user_agent() -> str:
    """Get user agent from request"""
    if not has_request_context():
        return None
    return request.headers.get('User-Agent', '')


def get_request_id() -> str:
    """Get request ID for correlation"""
    if has_request_context():
        return getattr(g, 'request_id', None)
    return None


def compute_diff(old_values: Dict, new_values: Dict) -> Dict:
    """Compute the difference between old and new values"""
    if not old_values or not new_values:
        return {}
    
    diff = {}
    all_keys = set(old_values.keys()) | set(new_values.keys())
    
    for key in all_keys:
        old_val = old_values.get(key)
        new_val = new_values.get(key)
        
        if old_val != new_val:
            diff[key] = {
                "from": old_val,
                "to": new_val
            }
    
    return diff


def log_audit(
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    old_values: Optional[Dict] = None,
    new_values: Optional[Dict] = None,
    description: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    user: Optional[User] = None,
    ip_address: Optional[str] = None,
    session_id: Optional[str] = None
) -> Optional[AuditLog]:
    """
    Create a comprehensive audit log entry
    
    Args:
        action: The action performed (e.g., 'user_login', 'application_created')
        entity_type: Type of entity affected (e.g., 'user', 'application')
        entity_id: ID of the affected entity
        old_values: Previous state (for updates)
        new_values: New state
        description: Human-readable description
        status: success, failed, or warning
        error_message: Error details if status is failed
        user: User object performing the action
        ip_address: Client IP address
        session_id: Session identifier
    
    Returns:
        Created AuditLog instance or None if logging failed
    """
    try:
        # Get values from request context if not provided
        if user is None and has_request_context():
            from routes.auth import get_current_user
            user, _ = get_current_user()
        
        if ip_address is None:
            ip_address = get_client_ip()
        
        # Compute changes
        changes = compute_diff(old_values or {}, new_values or {})
        
        # Create audit log entry
        audit_entry = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            user_role=user.role if user else None,
            ip_address=ip_address,
            user_agent=get_user_agent(),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            changes=changes if changes else None,
            description=description,
            status=status,
            error_message=error_message,
            request_id=get_request_id(),
            session_id=session_id
        )
        
        db.session.add(audit_entry)
        db.session.commit()
        
        return audit_entry
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        db.session.rollback()
        return None


# Convenience functions for common audit actions

def log_user_login(user: User, success: bool = True, error_message: str = None):
    """Log user login attempt"""
    return log_audit(
        action="user_login",
        entity_type="user",
        entity_id=user.id,
        description=f"User {user.email} login {'successful' if success else 'failed'}",
        status="success" if success else "failed",
        error_message=error_message,
        user=user if success else None
    )


def log_user_logout(user: User):
    """Log user logout"""
    return log_audit(
        action="user_logout",
        entity_type="user",
        entity_id=user.id,
        description=f"User {user.email} logged out",
        user=user
    )


def log_user_created(user: User, created_by: User = None):
    """Log user account creation"""
    return log_audit(
        action="user_created",
        entity_type="user",
        entity_id=user.id,
        new_values=user.to_dict(),
        description=f"User account created: {user.email}",
        user=created_by
    )


def log_user_updated(user: User, old_values: Dict, changes: Dict, updated_by: User = None):
    """Log user account update"""
    return log_audit(
        action="user_updated",
        entity_type="user",
        entity_id=user.id,
        old_values=old_values,
        new_values=user.to_dict(),
        description=f"User account updated: {user.email}. Changes: {', '.join(changes.keys())}",
        user=updated_by
    )


def log_user_deleted(user_id: int, user_email: str, deleted_by: User):
    """Log user account deletion"""
    return log_audit(
        action="user_deleted",
        entity_type="user",
        entity_id=user_id,
        description=f"User account deleted: {user_email}",
        user=deleted_by
    )


def log_application_created(application, created_by: User = None):
    """Log admission application creation"""
    return log_audit(
        action="application_created",
        entity_type="application",
        entity_id=application.id,
        new_values=application.to_dict(),
        description=f"Application created: {application.application_number}",
        user=created_by or application.user
    )


def log_application_updated(application, old_values: Dict, updated_by: User):
    """Log admission application update"""
    return log_audit(
        action="application_updated",
        entity_type="application",
        entity_id=application.id,
        old_values=old_values,
        new_values=application.to_dict(),
        description=f"Application updated: {application.application_number}",
        user=updated_by
    )


def log_application_status_changed(application, old_status: str, changed_by: User):
    """Log application status change"""
    return log_audit(
        action="application_status_changed",
        entity_type="application",
        entity_id=application.id,
        old_values={"status": old_status},
        new_values={"status": application.status},
        description=f"Application {application.application_number} status changed from '{old_status}' to '{application.status}'",
        user=changed_by
    )


def log_payment_initiated(payment, initiated_by: User = None):
    """Log payment initiation"""
    return log_audit(
        action="payment_initiated",
        entity_type="payment",
        entity_id=payment.id,
        new_values=payment.to_dict(),
        description=f"Payment initiated: {payment.reference} for UGX {payment.amount:,}",
        user=initiated_by or payment.user
    )


def log_payment_completed(payment, old_status: str = "pending"):
    """Log successful payment"""
    return log_audit(
        action="payment_completed",
        entity_type="payment",
        entity_id=payment.id,
        old_values={"status": old_status},
        new_values=payment.to_dict(),
        description=f"Payment completed: {payment.reference}",
        user=payment.user
    )


def log_payment_failed(payment, error_message: str):
    """Log failed payment"""
    return log_audit(
        action="payment_failed",
        entity_type="payment",
        entity_id=payment.id,
        description=f"Payment failed: {payment.reference}",
        status="failed",
        error_message=error_message,
        user=payment.user
    )


def log_bulk_operation(operation: str, entity_type: str, affected_ids: list, performed_by: User, details: Dict = None):
    """Log bulk operation"""
    return log_audit(
        action=f"bulk_{operation}",
        entity_type=entity_type,
        description=f"Bulk {operation} on {len(affected_ids)} {entity_type}(s)",
        new_values={
            "affected_ids": affected_ids,
            "count": len(affected_ids),
            "details": details
        },
        user=performed_by
    )


def log_data_export(entity_type: str, record_count: int, exported_by: User, filters: Dict = None):
    """Log data export"""
    return log_audit(
        action="data_export",
        entity_type=entity_type,
        description=f"Exported {record_count} {entity_type} records",
        new_values={
            "record_count": record_count,
            "filters": filters
        },
        user=exported_by
    )


def log_security_event(event_type: str, description: str, severity: str = "warning", user: User = None, details: Dict = None):
    """Log security-related events"""
    return log_audit(
        action=f"security_{event_type}",
        entity_type="security",
        description=description,
        status=severity,  # info, warning, critical
        new_values=details,
        user=user
    )


def log_api_error(endpoint: str, error_message: str, user: User = None, request_data: Dict = None):
    """Log API error"""
    return log_audit(
        action="api_error",
        entity_type="api",
        description=f"API error on {endpoint}",
        status="failed",
        error_message=error_message,
        new_values={"endpoint": endpoint, "request_data": request_data},
        user=user
    )


def get_audit_summary(user_id: int = None, days: int = 30) -> Dict:
    """Get summary of audit logs for dashboard"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = AuditLog.query.filter(AuditLog.timestamp >= cutoff)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    total = query.count()
    
    # Action breakdown
    actions = db.session.query(
        AuditLog.action,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.timestamp >= cutoff
    )
    
    if user_id:
        actions = actions.filter(AuditLog.user_id == user_id)
    
    actions = actions.group_by(AuditLog.action).all()
    
    # Status breakdown
    statuses = db.session.query(
        AuditLog.status,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.timestamp >= cutoff
    )
    
    if user_id:
        statuses = statuses.filter(AuditLog.user_id == user_id)
    
    statuses = statuses.group_by(AuditLog.status).all()
    
    return {
        "total_logs": total,
        "period_days": days,
        "by_action": {action: count for action, count in actions},
        "by_status": {status: count for status, count in statuses}
    }
