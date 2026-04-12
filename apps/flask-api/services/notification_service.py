"""
Notification Service
Integrates notifications with application status changes.
Uses existing Notification model - no external services.
"""
from datetime import datetime
from models import db, Notification, User, AdmissionApplication, OpportunityApplication


class NotificationService:
    """
    Simple notification system using database.
    No external APIs (email/SMS optional, disabled by default).
    """
    
    @staticmethod
    def create_notification(user_id: int, title: str, message: str, 
                            notification_type: str = 'general', link: str = None) -> Notification:
        """Create a notification for a user."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @classmethod
    def notify_admission_status_change(cls, application: AdmissionApplication, 
                                       old_status: str, new_status: str):
        """
        Notify applicant when admission application status changes.
        """
        status_messages = {
            'pending': 'Your application is pending review.',
            'under_review': 'Your application is now under review by admissions.',
            'interview_scheduled': 'You have been scheduled for an interview. Check your email for details.',
            'accepted': 'Congratulations! Your application has been accepted.',
            'rejected': 'We regret to inform you that your application was not successful.',
            'waitlisted': 'You have been placed on the waitlist.',
            'deferred': 'Your application has been deferred to the next intake.',
            'conditional_offer': 'You have received a conditional offer. Please review the requirements.',
            'enrolled': 'You have been successfully enrolled. Welcome to KIU!'
        }
        
        title = f"Application Status Update: {new_status.replace('_', ' ').title()}"
        message = status_messages.get(new_status, f'Your application status has been updated to {new_status}.')
        
        link = f"/applicant/application/{application.id}"
        
        cls.create_notification(
            user_id=application.user_id,
            title=title,
            message=message,
            notification_type='application_status',
            link=link
        )
    
    @classmethod
    def notify_opportunity_status_change(cls, application: OpportunityApplication,
                                         old_status: str, new_status: str):
        """
        Notify finalist when opportunity application status changes.
        """
        opportunity = application.opportunity
        
        status_messages = {
            'applied': 'Your application has been submitted.',
            'under_review': f'Your application for {opportunity.title} is under review.',
            'shortlisted': f'Congratulations! You have been shortlisted for {opportunity.title}.',
            'interview': f'You have been invited for an interview for {opportunity.title}.',
            'offered': f'Congratulations! You have received an offer for {opportunity.title}.',
            'rejected': f'Your application for {opportunity.title} was not successful.',
            'withdrawn': 'You have withdrawn your application.',
            'accepted': f'You have accepted the offer for {opportunity.title}!'
        }
        
        title = f"Opportunity Update: {opportunity.organization}"
        message = status_messages.get(new_status, f'Your application status: {new_status}')
        
        link = f"/finalist/opportunities/{application.id}"
        
        cls.create_notification(
            user_id=application.user_id,
            title=title,
            message=message,
            notification_type='opportunity_status',
            link=link
        )
    
    @classmethod
    def notify_new_opportunity(cls, opportunity, target_finalist_ids: list = None):
        """
        Notify finalists about a new opportunity.
        If target_finalist_ids provided, notify only those; otherwise notify all finalists.
        """
        title = f"New Opportunity: {opportunity.title}"
        message = f"{opportunity.organization} is hiring for {opportunity.title}. Apply before {opportunity.application_deadline}!"
        link = f"/finalist/opportunities/{opportunity.id}"
        
        if target_finalist_ids:
            for finalist_id in target_finalist_ids:
                cls.create_notification(
                    user_id=finalist_id,
                    title=title,
                    message=message,
                    notification_type='new_opportunity',
                    link=link
                )
        else:
            # Notify all users with finalist role
            finalists = User.query.filter_by(role='finalist').all()
            for finalist in finalists:
                cls.create_notification(
                    user_id=finalist.id,
                    title=title,
                    message=message,
                    notification_type='new_opportunity',
                    link=link
                )
    
    @classmethod
    def get_unread_count(cls, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    @classmethod
    def mark_as_read(cls, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read (verifies ownership)."""
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
