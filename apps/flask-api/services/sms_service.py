"""
SMS Notification Service for KIU Admission Portal
Supports: Twilio, Africa's Talking, and sandbox mode for testing
"""
import os
import logging
from typing import Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SMSService(ABC):
    """Abstract base class for SMS services"""
    
    @abstractmethod
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS to a single phone number"""
        pass
    
    @abstractmethod
    def send_bulk_sms(self, phone_numbers: List[str], message: str) -> dict:
        """Send SMS to multiple phone numbers"""
        pass


class TwilioService(SMSService):
    """Twilio SMS implementation"""
    
    def __init__(self):
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.from_number = os.environ.get("TWILIO_PHONE_NUMBER", "")
        
        try:
            from twilio.rest import Client
            self.client = Client(self.account_sid, self.auth_token) if self.account_sid and self.auth_token else None
        except ImportError:
            logger.warning("Twilio not installed. Run: pip install twilio")
            self.client = None
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS using Twilio"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            # Format phone number
            formatted_number = self._format_phone_number(phone_number)
            
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=formatted_number
            )
            
            logger.info(f"SMS sent via Twilio to {formatted_number}, SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Twilio SMS failed: {str(e)}")
            return False
    
    def send_bulk_sms(self, phone_numbers: List[str], message: str) -> dict:
        """Send bulk SMS using Twilio"""
        results = {"successful": [], "failed": []}
        
        for phone_number in phone_numbers:
            if self.send_sms(phone_number, message):
                results["successful"].append(phone_number)
            else:
                results["failed"].append(phone_number)
        
        return results
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for international format"""
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # If starts with 0, replace with +256 (Uganda)
        if phone.startswith("0"):
            phone = "+256" + phone[1:]
        
        # If doesn't start with +, assume Uganda and add +256
        if not phone.startswith("+"):
            phone = "+256" + phone
        
        return phone


class AfricasTalkingService(SMSService):
    """Africa's Talking SMS implementation"""
    
    def __init__(self):
        self.username = os.environ.get("AT_USERNAME", "")
        self.api_key = os.environ.get("AT_API_KEY", "")
        self.sender_id = os.environ.get("AT_SENDER_ID", "KIU-PORTAL")
        
        try:
            import africastalking
            if self.username and self.api_key:
                africastalking.initialize(self.username, self.api_key)
                self.sms = africastalking.SMS
            else:
                self.sms = None
        except ImportError:
            logger.warning("Africa's Talking SDK not installed. Run: pip install africastalking")
            self.sms = None
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS using Africa's Talking"""
        if not self.sms:
            logger.error("Africa's Talking not initialized")
            return False
        
        try:
            # Format phone number
            formatted_number = self._format_phone_number(phone_number)
            
            response = self.sms.send(
                message=message,
                recipients=[formatted_number],
                sender_id=self.sender_id
            )
            
            if response and response.get("SMSMessageData"):
                logger.info(f"SMS sent via Africa's Talking to {formatted_number}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Africa's Talking SMS failed: {str(e)}")
            return False
    
    def send_bulk_sms(self, phone_numbers: List[str], message: str) -> dict:
        """Send bulk SMS using Africa's Talking"""
        if not self.sms:
            return {"successful": [], "failed": phone_numbers}
        
        try:
            # Format all numbers
            formatted_numbers = [self._format_phone_number(p) for p in phone_numbers]
            
            response = self.sms.send(
                message=message,
                recipients=formatted_numbers,
                sender_id=self.sender_id
            )
            
            results = {"successful": [], "failed": []}
            
            if response and response.get("SMSMessageData"):
                recipients = response["SMSMessageData"].get("Recipients", [])
                for recipient in recipients:
                    if recipient.get("status") == "Success":
                        results["successful"].append(recipient.get("number"))
                    else:
                        results["failed"].append(recipient.get("number"))
            
            return results
            
        except Exception as e:
            logger.error(f"Africa's Talking bulk SMS failed: {str(e)}")
            return {"successful": [], "failed": phone_numbers}
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for Africa's Talking (no + prefix)"""
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Remove + if present
        if phone.startswith("+"):
            phone = phone[1:]
        
        # If starts with 0, replace with 256 (Uganda)
        if phone.startswith("0"):
            phone = "256" + phone[1:]
        
        return phone


class SandboxSMSService(SMSService):
    """Sandbox SMS service for testing - logs messages but doesn't send"""
    
    def __init__(self):
        self.sent_messages = []
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Log SMS instead of sending (for testing)"""
        formatted_number = self._format_phone_number(phone_number)
        
        log_entry = {
            "to": formatted_number,
            "message": message[:50] + "..." if len(message) > 50 else message,
            "status": "sent_sandbox"
        }
        
        self.sent_messages.append(log_entry)
        logger.info(f"[SANDBOX SMS] To: {formatted_number}, Message: {log_entry['message']}")
        
        return True
    
    def send_bulk_sms(self, phone_numbers: List[str], message: str) -> dict:
        """Log bulk SMS instead of sending"""
        results = {"successful": [], "failed": []}
        
        for phone_number in phone_numbers:
            if self.send_sms(phone_number, message):
                results["successful"].append(phone_number)
            else:
                results["failed"].append(phone_number)
        
        return results
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for display"""
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if phone.startswith("0"):
            phone = "+256" + phone[1:]
        elif not phone.startswith("+"):
            phone = "+256" + phone
        
        return phone
    
    def get_sent_messages(self) -> List[dict]:
        """Get all sent messages (for testing verification)"""
        return self.sent_messages


# SMS Service Factory
SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "sandbox").lower()

_sms_service: Optional[SMSService] = None


def get_sms_service() -> SMSService:
    """Get SMS service instance (singleton)"""
    global _sms_service
    
    if _sms_service is None:
        if SMS_PROVIDER == "twilio":
            _sms_service = TwilioService()
        elif SMS_PROVIDER == "africastalking":
            _sms_service = AfricasTalkingService()
        else:
            _sms_service = SandboxSMSService()
    
    return _sms_service


def send_notification_sms(phone_number: str, notification_type: str, **kwargs) -> bool:
    """Send templated notification SMS"""
    service = get_sms_service()
    
    # SMS templates
    templates = {
        "application_received": "KIU Admissions: Your application {ref} has been received. Check your email for details.",
        "application_status_update": "KIU Admissions: Your application {ref} status is now: {status}. Login to view details.",
        "payment_received": "KIU Admissions: Payment of UGX {amount} received for application {ref}. Thank you!",
        "payment_reminder": "KIU Admissions: Application fee of UGX 50,000 pending for {ref}. Pay via mobile money.",
        "interview_invitation": "KIU Admissions: You've been invited for an interview. Check your email for details.",
        "admission_offer": "KIU Admissions: Congratulations! Offer received for {program}. Check email for acceptance instructions.",
        "deadline_reminder": "KIU Admissions: Reminder: Application deadline approaching for {program}. Submit now!",
        "verification_code": "Your KIU Portal verification code is: {code}. Valid for 10 minutes.",
    }
    
    template = templates.get(notification_type, "KIU Admissions: You have a new notification. Login to view.")
    
    try:
        message = template.format(**kwargs)
        return service.send_sms(phone_number, message)
    except KeyError as e:
        logger.error(f"Missing template variable: {e}")
        return False


def notify_application_status_change_sms(application, old_status: str = None) -> bool:
    """Send SMS notification when application status changes"""
    user = application.user
    if not user or not user.phone:
        return False
    
    return send_notification_sms(
        phone_number=user.phone,
        notification_type="application_status_update",
        ref=application.application_number,
        status=application.status.replace("_", " ").title()
    )


def notify_payment_received_sms(payment) -> bool:
    """Send SMS notification when payment is received"""
    user = payment.user
    if not user or not user.phone:
        return False
    
    return send_notification_sms(
        phone_number=user.phone,
        notification_type="payment_received",
        amount=f"{payment.amount:,.0f}",
        ref=payment.application.application_number if payment.application else "N/A"
    )


def send_verification_code_sms(phone_number: str, code: str) -> bool:
    """Send SMS verification code"""
    return send_notification_sms(
        phone_number=phone_number,
        notification_type="verification_code",
        code=code
    )
