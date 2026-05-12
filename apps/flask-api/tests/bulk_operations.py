"""
Bulk Operations Module for Admin
Allows administrators to perform bulk actions on applications, users, etc.
"""
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from models import (
    db, AdmissionApplication, User, Notification, 
    ApplicationStatusHistory, Program
)
from routes.auth import get_current_user
from utils.error_handlers import ValidationError
from utils.caching import invalidate_user_cache
from utils.api_response import success_response, bad_request, unauthorized, forbidden, not_found

bulk_ops_bp = Blueprint("bulk_operations", __name__)


def check_admin_access():
    """Verify user is admin"""
    user, error = get_current_user()
    if error:
        return None, unauthorized(error)
    if user.role != "admin":
        return None, forbidden("Admin access required")
    return user, None


@bulk_ops_bp.route("/applications/status", methods=["POST"])
def bulk_update_application_status():
    """Bulk update application status"""
    user, error = check_admin_access()
    if error:
        return error
    
    data = request.get_json()
    if not data:
        return bad_request("JSON payload required")
    
    application_ids = data.get("application_ids", [])
    new_status = data.get("status")
    notes = data.get("notes", "")
    notify_applicants = data.get("notify", True)
    
    if not application_ids:
        return bad_request("application_ids required", errors={"application_ids": "Required"})
    
    if not new_status:
        return bad_request("status required", errors={"status": "Required"})
    
    valid_statuses = ["pending", "under_review", "accepted", "rejected", "waitlisted", "deferred"]
    if new_status not in valid_statuses:
        return bad_request(
            f"Status must be one of: {', '.join(valid_statuses)}",
            errors={"status": "Invalid value"}
        )
    
    updated_count = 0
    failed_ids = []
    
    for app_id in application_ids:
        try:
            application = AdmissionApplication.query.get(app_id)
            if not application:
                failed_ids.append({"id": app_id, "reason": "Application not found"})
                continue
            
            old_status = application.status
            application.status = new_status
            
            # Add to status history
            history = ApplicationStatusHistory(
                application_id=app_id,
                status=new_status,
                notes=notes,
                changed_by_user_id=user.id
            )
            db.session.add(history)
            
            # Send notification if enabled
            if notify_applicants:
                notification = Notification(
                    user_id=application.user_id,
                    title="Application Status Updated",
                    message=f"Your application {application.application_number} status has been updated to: {new_status}",
                    notification_type="application_status",
                    link=f"/applications/{app_id}"
                )
                db.session.add(notification)
            
            updated_count += 1
            
        except Exception as e:
            failed_ids.append({"id": app_id, "reason": str(e)})
    
    db.session.commit()
    
    # Invalidate caches for affected users
    for app_id in application_ids:
        application = AdmissionApplication.query.get(app_id)
        if application:
            invalidate_user_cache(application.user_id)
    
    current_app.logger.info(f"Bulk status update: {updated_count} applications updated to {new_status} by admin {user.id}")
    
    return success_response({
        "updated_count": updated_count,
        "failed_count": len(failed_ids),
        "failed_ids": failed_ids
    }, message=f"Updated {updated_count} applications to status: {new_status}")


@bulk_ops_bp.route("/applications/payment-waiver", methods=["POST"])
def bulk_payment_waiver():
    """Bulk waive payment for selected applications"""
    user, error = check_admin_access()
    if error:
        return error
    
    data = request.get_json()
    if not data:
        return bad_request("JSON payload required")
    
    application_ids = data.get("application_ids", [])
    reason = data.get("reason", "")
    
    if not application_ids:
        return bad_request("application_ids required", errors={"application_ids": "Required"})
    
    waived_count = 0
    failed_ids = []
    
    for app_id in application_ids:
        try:
            application = AdmissionApplication.query.get(app_id)
            if not application:
                failed_ids.append({"id": app_id, "reason": "Application not found"})
                continue
            
            if application.payment_status == "waived":
                failed_ids.append({"id": app_id, "reason": "Payment already waived"})
                continue
            
            application.payment_status = "waived"
            
            # Send notification
            notification = Notification(
                user_id=application.user_id,
                title="Application Fee Waived",
                message=f"Your application fee has been waived. Reason: {reason or 'Administrative waiver'}",
                notification_type="general",
                link=f"/applications/{app_id}"
            )
            db.session.add(notification)
            
            waived_count += 1
            
        except Exception as e:
            failed_ids.append({"id": app_id, "reason": str(e)})
    
    db.session.commit()
    
    current_app.logger.info(f"Bulk payment waiver: {waived_count} applications by admin {user.id}")
    
    return success_response({
        "waived_count": waived_count,
        "failed_count": len(failed_ids),
        "failed_ids": failed_ids
    }, message=f"Waived payment for {waived_count} applications")


@bulk_ops_bp.route("/users/notify", methods=["POST"])
def bulk_notify_users():
    """Send bulk notification to users"""
    user, error = check_admin_access()
    if error:
        return error
    
    data = request.get_json()
    if not data:
        return bad_request("JSON payload required")
    
    title = data.get("title")
    message = data.get("message")
    user_ids = data.get("user_ids", [])
    role_filter = data.get("role")  # Optional: filter by role
    
    if not title or not message:
        return bad_request("title and message required", errors={"title": "Required" if not title else None, "message": "Required" if not message else None})
    
    # Determine target users
    target_users = []
    
    if user_ids:
        # Specific users
        target_users = User.query.filter(User.id.in_(user_ids)).all()
    elif role_filter:
        # All users with specific role
        target_users = User.query.filter_by(role=role_filter).all()
    else:
        return bad_request("user_ids or role required", errors={"filter": "Required"})
    
    notification_count = 0
    
    for target_user in target_users:
        try:
            notification = Notification(
                user_id=target_user.id,
                title=title,
                message=message,
                notification_type="general"
            )
            db.session.add(notification)
            notification_count += 1
            
            # Invalidate user cache to show new notification
            invalidate_user_cache(target_user.id)
            
        except Exception as e:
            current_app.logger.error(f"Failed to create notification for user {target_user.id}: {e}")
    
    db.session.commit()
    
    current_app.logger.info(f"Bulk notification: {notification_count} users notified by admin {user.id}")
    
    return success_response({
        "sent_count": notification_count,
        "title": title
    }, message=f"Notification sent to {notification_count} users")


@bulk_ops_bp.route("/applications/delete", methods=["POST"])
def bulk_delete_applications():
    """Bulk delete applications (soft delete - mark as deleted)"""
    user, error = check_admin_access()
    if error:
        return error
    
    data = request.get_json()
    if not data:
        return bad_request("JSON payload required")
    
    application_ids = data.get("application_ids", [])
    reason = data.get("reason", "")
    
    if not application_ids:
        return bad_request("application_ids required", errors={"application_ids": "Required"})
    
    deleted_count = 0
    failed_ids = []
    
    for app_id in application_ids:
        try:
            application = AdmissionApplication.query.get(app_id)
            if not application:
                failed_ids.append({"id": app_id, "reason": "Application not found"})
                continue
            
            # Soft delete - change status to deleted
            old_status = application.status
            application.status = "deleted"
            
            # Add to status history
            history = ApplicationStatusHistory(
                application_id=app_id,
                status="deleted",
                notes=f"Bulk deletion. Previous status: {old_status}. Reason: {reason}",
                changed_by_user_id=user.id
            )
            db.session.add(history)
            
            # Notify applicant
            notification = Notification(
                user_id=application.user_id,
                title="Application Deleted",
                message=f"Your application {application.application_number} has been deleted. Contact admissions office for more information.",
                notification_type="general"
            )
            db.session.add(notification)
            
            deleted_count += 1
            
        except Exception as e:
            failed_ids.append({"id": app_id, "reason": str(e)})
    
    db.session.commit()
    
    current_app.logger.info(f"Bulk delete: {deleted_count} applications deleted by admin {user.id}")
    
    return success_response({
        "deleted_count": deleted_count,
        "failed_count": len(failed_ids),
        "failed": failed_ids
    }, message=f"Deleted {deleted_count} applications")


@bulk_ops_bp.route("/programs/capacity-update", methods=["POST"])
def bulk_update_program_capacity():
    """Bulk update program capacity limits"""
    user, error = check_admin_access()
    if error:
        return error
    
    data = request.get_json()
    if not data:
        return bad_request("JSON payload required")
    
    updates = data.get("updates", [])  # List of {program_id, new_capacity}
    
    if not updates:
        return bad_request("updates array required", errors={"updates": "Required"})
    
    updated_count = 0
    failed_updates = []
    
    for update in updates:
        try:
            program_id = update.get("program_id")
            new_capacity = update.get("new_capacity")
            
            if not program_id or new_capacity is None:
                failed_updates.append({"update": update, "reason": "Missing program_id or new_capacity"})
                continue
            
            program = db.session.get(Program, program_id)
            if not program:
                failed_updates.append({"program_id": program_id, "reason": "Program not found"})
                continue
            
            old_capacity = program.available_slots
            program.available_slots = new_capacity
            updated_count += 1
            
            current_app.logger.info(
                f"Program {program_id} capacity updated: {old_capacity} -> {new_capacity} by admin {user.id}"
            )
            
        except Exception as e:
            failed_updates.append({"update": update, "reason": str(e)})
    
    db.session.commit()
    
    return success_response({
        "updated_count": updated_count,
        "failed_count": len(failed_updates),
        "failed": failed_updates
    }, message=f"Updated capacity for {updated_count} programs")


@bulk_ops_bp.route("/applications/assign-reviewer", methods=["POST"])
def bulk_assign_reviewer():
    """Bulk assign applications to reviewers"""
    user, error = check_admin_access()
    if error:
        return error
    
    data = request.get_json()
    if not data:
        return bad_request("JSON payload required")
    
    application_ids = data.get("application_ids", [])
    reviewer_id = data.get("reviewer_id")
    
    if not application_ids:
        return bad_request("application_ids required", errors={"application_ids": "Required"})
    
    if not reviewer_id:
        return bad_request("reviewer_id required", errors={"reviewer_id": "Required"})
    
    # Verify reviewer exists
    reviewer = User.query.get(reviewer_id)
    if not reviewer:
        return not_found("Reviewer not found")
    
    assigned_count = 0
    failed_ids = []
    
    for app_id in application_ids:
        try:
            application = AdmissionApplication.query.get(app_id)
            if not application:
                failed_ids.append({"id": app_id, "reason": "Application not found"})
                continue
            
            # Add status history entry for assignment
            history = ApplicationStatusHistory(
                application_id=app_id,
                status=application.status,  # Keep current status
                notes=f"Assigned to reviewer: {reviewer.first_name} {reviewer.last_name} ({reviewer.email})",
                changed_by_user_id=user.id
            )
            db.session.add(history)
            
            assigned_count += 1
            
        except Exception as e:
            failed_ids.append({"id": app_id, "reason": str(e)})
    
    db.session.commit()
    
    return success_response({
        "assigned_count": assigned_count,
        "failed_count": len(failed_ids),
        "failed": failed_ids,
        "reviewer": reviewer.to_dict()
    }, message=f"Assigned {assigned_count} applications to reviewer: {reviewer.first_name} {reviewer.last_name}")
