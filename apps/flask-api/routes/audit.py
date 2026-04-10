"""
Audit Log API Routes for KIU Admission Portal
Provides endpoints for viewing and searching audit logs
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from models import db, AuditLog, User
from routes.auth import get_current_user

audit_bp = Blueprint("audit", __name__)


def check_admin_access():
    """Verify user is admin"""
    user, error = get_current_user()
    if error:
        return None, (jsonify({"error": "Unauthorized", "message": error}), 401)
    if user.role != "admin":
        return None, (jsonify({"error": "Forbidden", "message": "Admin access required"}), 403)
    return user, None


@audit_bp.route("", methods=["GET"])
def list_audit_logs():
    """Get audit logs with filtering and pagination"""
    user, error = check_admin_access()
    if error:
        return error
    
    # Query parameters
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("perPage", 50, type=int), 100)
    
    # Filters
    action = request.args.get("action")
    entity_type = request.args.get("entityType")
    entity_id = request.args.get("entityId", type=int)
    user_id = request.args.get("userId", type=int)
    status = request.args.get("status")
    days = request.args.get("days", 30, type=int)
    
    # Build query
    query = AuditLog.query
    
    # Apply date filter
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AuditLog.timestamp >= cutoff)
    
    # Apply other filters
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if status:
        query = query.filter(AuditLog.status == status)
    
    # Order by timestamp descending
    query = query.order_by(desc(AuditLog.timestamp))
    
    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "logs": [log.to_dict() for log in paginated.items],
        "total": paginated.total,
        "page": page,
        "perPage": per_page,
        "pages": paginated.pages,
        "filters": {
            "action": action,
            "entityType": entity_type,
            "entityId": entity_id,
            "userId": user_id,
            "status": status,
            "days": days
        }
    }), 200


@audit_bp.route("/<int:log_id>", methods=["GET"])
def get_audit_log(log_id):
    """Get detailed view of a single audit log entry"""
    user, error = check_admin_access()
    if error:
        return error
    
    log = AuditLog.query.get_or_404(log_id)
    
    return jsonify(log.to_dict()), 200


@audit_bp.route("/summary", methods=["GET"])
def get_audit_summary():
    """Get summary statistics of audit logs"""
    user, error = check_admin_access()
    if error:
        return error
    
    days = request.args.get("days", 30, type=int)
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Total logs
    total_logs = AuditLog.query.filter(AuditLog.timestamp >= cutoff).count()
    
    # By action
    action_stats = db.session.query(
        AuditLog.action,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.timestamp >= cutoff
    ).group_by(AuditLog.action).all()
    
    # By status
    status_stats = db.session.query(
        AuditLog.status,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.timestamp >= cutoff
    ).group_by(AuditLog.status).all()
    
    # By entity type
    entity_stats = db.session.query(
        AuditLog.entity_type,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.timestamp >= cutoff
    ).group_by(AuditLog.entity_type).all()
    
    # Most active users
    top_users = db.session.query(
        AuditLog.user_id,
        AuditLog.user_email,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.timestamp >= cutoff,
        AuditLog.user_id.isnot(None)
    ).group_by(
        AuditLog.user_id,
        AuditLog.user_email
    ).order_by(
        desc(func.count(AuditLog.id))
    ).limit(10).all()
    
    # Recent security events
    security_events = AuditLog.query.filter(
        AuditLog.timestamp >= cutoff,
        AuditLog.action.like("security_%")
    ).count()
    
    # Failed actions
    failed_count = AuditLog.query.filter(
        AuditLog.timestamp >= cutoff,
        AuditLog.status == "failed"
    ).count()
    
    return jsonify({
        "period": f"Last {days} days",
        "total_logs": total_logs,
        "by_action": {action: count for action, count in action_stats},
        "by_status": {status: count for status, count in status_stats},
        "by_entity_type": {entity: count for entity, count in entity_stats},
        "top_users": [
            {"user_id": uid, "email": email, "action_count": count}
            for uid, email, count in top_users
        ],
        "security_events": security_events,
        "failed_actions": failed_count
    }), 200


@audit_bp.route("/actions", methods=["GET"])
def get_unique_actions():
    """Get list of unique action types for filtering"""
    user, error = check_admin_access()
    if error:
        return error
    
    actions = db.session.query(AuditLog.action).distinct().all()
    entity_types = db.session.query(AuditLog.entity_type).distinct().all()
    
    return jsonify({
        "actions": sorted([a[0] for a in actions]),
        "entityTypes": sorted([e[0] for e in entity_types])
    }), 200


@audit_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_audit_trail(user_id):
    """Get audit trail for a specific user"""
    admin_user, error = check_admin_access()
    if error:
        return error
    
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("perPage", 50, type=int), 100)
    days = request.args.get("days", 30, type=int)
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Get logs where this user performed actions
    performed_logs = AuditLog.query.filter(
        AuditLog.user_id == user_id,
        AuditLog.timestamp >= cutoff
    ).order_by(desc(AuditLog.timestamp)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get logs where this user was affected
    affected_logs = AuditLog.query.filter(
        AuditLog.entity_type == "user",
        AuditLog.entity_id == user_id,
        AuditLog.timestamp >= cutoff
    ).order_by(desc(AuditLog.timestamp)).limit(20).all()
    
    target_user = User.query.get(user_id)
    
    return jsonify({
        "user": target_user.to_dict() if target_user else None,
        "actions_performed": {
            "logs": [log.to_dict() for log in performed_logs.items],
            "total": performed_logs.total,
            "page": page,
            "perPage": per_page,
            "pages": performed_logs.pages
        },
        "actions_affecting_user": [log.to_dict() for log in affected_logs],
        "summary": {
            "total_actions": performed_logs.total,
            "actions_affecting_them": len(affected_logs)
        }
    }), 200


@audit_bp.route("/entity/<entity_type>/<int:entity_id>", methods=["GET"])
def get_entity_audit_trail(entity_type, entity_id):
    """Get audit trail for a specific entity"""
    user, error = check_admin_access()
    if error:
        return error
    
    days = request.args.get("days", 90, type=int)
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    logs = AuditLog.query.filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id,
        AuditLog.timestamp >= cutoff
    ).order_by(desc(AuditLog.timestamp)).all()
    
    return jsonify({
        "entity_type": entity_type,
        "entity_id": entity_id,
        "period": f"Last {days} days",
        "logs": [log.to_dict() for log in logs],
        "total_changes": len(logs)
    }), 200


@audit_bp.route("/export", methods=["POST"])
def export_audit_logs():
    """Export audit logs to CSV"""
    import csv
    import io
    from flask import Response
    
    user, error = check_admin_access()
    if error:
        return error
    
    data = request.get_json() or {}
    days = data.get("days", 30)
    action_filter = data.get("action")
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = AuditLog.query.filter(AuditLog.timestamp >= cutoff)
    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
    
    logs = query.order_by(desc(AuditLog.timestamp)).all()
    
    # Prepare CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "ID", "Timestamp", "User ID", "User Email", "User Role",
        "IP Address", "Action", "Entity Type", "Entity ID",
        "Description", "Status", "Changes", "Request ID"
    ])
    
    # Data rows
    for log in logs:
        writer.writerow([
            log.id,
            log.timestamp.isoformat() if log.timestamp else "",
            log.user_id or "",
            log.user_email or "",
            log.user_role or "",
            log.ip_address or "",
            log.action,
            log.entity_type,
            log.entity_id or "",
            log.description or "",
            log.status,
            json.dumps(log.changes) if log.changes else "",
            log.request_id or ""
        ])
    
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return response
