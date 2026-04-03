from flask import Blueprint, request, jsonify, current_app
from models import db, Notification, User, AdmissionApplication, OpportunityApplication
from routes.auth import get_current_user
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

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


def send_email(to_email, subject, body_html, body_text=None):
    """
    Send email notification using SMTP.
    
    Uses environment variables for SMTP configuration:
    - SMTP_HOST: SMTP server hostname
    - SMTP_PORT: SMTP server port (default 587)
    - SMTP_USER: SMTP username/email
    - SMTP_PASSWORD: SMTP password
    - SMTP_FROM_EMAIL: Sender email address
    - SMTP_FROM_NAME: Sender name (default: KIU Admissions)
    """
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    from_email = os.environ.get("SMTP_FROM_EMAIL", smtp_user)
    from_name = os.environ.get("SMTP_FROM_NAME", "KIU Admissions")
    
    # Skip email if SMTP not configured
    if not all([smtp_host, smtp_user, smtp_password]):
        current_app.logger.warning("SMTP not configured, skipping email notification")
        return False
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email
        
        # Add plain text version
        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        
        # Add HTML version
        msg.attach(MIMEText(body_html, "html"))
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        
        current_app.logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def create_notification(user_id, title, message, notification_type, link=None, send_email_notification=True):
    """Helper function to create a notification and optionally send email."""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
    db.session.add(notification)
    db.session.commit()
    
    # Send email notification if enabled
    if send_email_notification:
        user = User.query.get(user_id)
        if user and user.email:
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #1a56db; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9fafb; }}
                    .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                    .button {{ display: inline-block; padding: 10px 20px; background-color: #1a56db; color: white; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>KIU Admission Portal</h1>
                    </div>
                    <div class="content">
                        <h2>{title}</h2>
                        <p>{message}</p>
                        {f'<p><a href="{link}" class="button">View Details</a></p>' if link else ''}
                    </div>
                    <div class="footer">
                        <p>This is an automated message from KIU Admission Portal.</p>
                        <p>&copy; {datetime.now().year} Kampala International University</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            email_text = f"{title}\n\n{message}\n\n{f'View details: {link}' if link else ''}\n\n---\nKIU Admission Portal"
            
            send_email(
                to_email=user.email,
                subject=f"KIU: {title}",
                body_html=email_html,
                body_text=email_text
            )
    
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