from flask import Blueprint, request, jsonify
from models import db, Notification, User, AdmissionApplication, OpportunityApplication
from routes.auth import get_current_user

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("", methods=["GET"])
def list_notifications():
    """Get all notifications for the current user."""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("perPage", 20, type=int), 100)
    unread_only = request.args.get("unreadOnly", "false").lower() == "true"

    query = Notification.query.filter_by(user_id=user.id)
    if unread_only:
        query = query.filter_by(is_read=False)

    paginated = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "notifications": [n.to_dict() for n in paginated.items],
        "total": paginated.total,
        "unreadCount": Notification.query.filter_by(user_id=user.id, is_read=False).count(),
        "page": page,
        "perPage": per_page,
        "pages": paginated.pages,
    }), 200


@notifications_bp.route("/<int:notification_id>/read", methods=["PATCH"])
def mark_as_read(notification_id):
    """Mark a notification as read."""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    notification = db.session.get(Notification, notification_id)
    if not notification:
        return jsonify({"error": "Not found", "message": "Notification not found"}), 404

    if notification.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    notification.is_read = True
    db.session.commit()

    return jsonify(notification.to_dict()), 200


@notifications_bp.route("/read-all", methods=["PATCH"])
def mark_all_as_read():
    """Mark all notifications as read for the current user."""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    Notification.query.filter_by(user_id=user.id, is_read=False).update({"is_read": True})
    db.session.commit()

    return jsonify({"message": "All notifications marked as read"}), 200


@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
def delete_notification(notification_id):
    """Delete a notification."""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    notification = db.session.get(Notification, notification_id)
    if not notification:
        return jsonify({"error": "Not found", "message": "Notification not found"}), 404

    if notification.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(notification)
    db.session.commit()

    return "", 204


def create_notification(user_id, title, message, notification_type, link=None):
    """Helper function to create a notification."""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def notify_application_status_change(application):
    """Send notification when admission application status changes."""
    status_messages = {
        "under_review": "Your application is now under review by our admissions team.",
        "accepted": "Congratulations! Your application has been accepted. Please check your dashboard for next steps.",
        "rejected": "We regret to inform you that your application was not successful. You may apply again next intake.",
        "waitlisted": "Your application has been waitlisted. We will contact you if a spot becomes available.",
    }
    
    message = status_messages.get(application.status, f"Your application status has been updated to: {application.status}")
    
    create_notification(
        user_id=application.user_id,
        title=f"Application Update: {application.application_number}",
        message=message,
        notification_type="application_status",
        link=f"/dashboard",
    )


def notify_new_opportunity(opportunity):
    """Send notification to all finalists about a new opportunity."""
    from models import FinalistProfile
    
    finalists = FinalistProfile.query.filter_by(is_finalist=True).all()
    
    for finalist in finalists:
        create_notification(
            user_id=finalist.user_id,
            title=f"New {opportunity.type.title()}: {opportunity.title}",
            message=f"{opportunity.organization} has posted a new {opportunity.type}. Apply before {opportunity.application_deadline.strftime('%B %d, %Y')}.",
            notification_type="new_opportunity",
            link=f"/career/opportunities",
        )


def notify_opportunity_application_status(application):
    """Send notification when opportunity application status changes."""
    status_messages = {
        "shortlisted": "You have been shortlisted for this opportunity. The employer may contact you soon.",
        "interview_scheduled": "An interview has been scheduled. Check your email for details.",
        "accepted": "Congratulations! Your application has been accepted. The employer will contact you with next steps.",
        "rejected": "Your application was not successful this time. Keep applying to other opportunities!",
    }
    
    message = status_messages.get(application.status, f"Your application status has been updated to: {application.status}")
    
    create_notification(
        user_id=application.user_id,
        title=f"Application Update: {application.opportunity.title}",
        message=message,
        notification_type="application_status",
        link=f"/career/applications",
    )