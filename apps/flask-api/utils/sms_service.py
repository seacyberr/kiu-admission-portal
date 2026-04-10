"""
SMS Notification Service for KIU Admission Portal
Supports: Africa's Talking (primary for Uganda), Twilio (alternative)
"""
import os
import logging
from datetime import datetime

try:
    import africastalking
except ImportError:
    africastalking = None

try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

log = logging.getLogger("kiu.sms")


class SMSService:
    """SMS service provider interface"""
    
    def __init__(self):
        self.provider = os.environ.get("SMS_PROVIDER", "none")  # africastalking, twilio, none
        self.sender_id = os.environ.get("SMS_SENDER_ID", "KIU-ADMS")
        
        # Africa's Talking configuration
        self.at_username = os.environ.get("AT_USERNAME", "")
        self.at_api_key = os.environ.get("AT_API_KEY", "")
        
        # Twilio configuration
        self.twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone_number = os.environ.get("TWILIO_PHONE_NUMBER", "")
        
        self._init_client()
    
    def _init_client(self):
        """Initialize SMS client based on provider"""
        if self.provider == "africastalking" and africastalking:
            if self.at_username and self.at_api_key:
                africastalking.initialize(self.at_username, self.at_api_key)
                self.sms_client = africastalking.SMS
                log.info("Africa's Talking SMS client initialized")
            else:
                log.warning("Africa's Talking credentials not configured")
                self.sms_client = None
        elif self.provider == "twilio" and TwilioClient:
            if self.twilio_account_sid and self.twilio_auth_token:
                self.sms_client = TwilioClient(
                    self.twilio_account_sid,
                    self.twilio_auth_token
                )
                log.info("Twilio SMS client initialized")
            else:
                log.warning("Twilio credentials not configured")
                self.sms_client = None
        else:
            self.sms_client = None
            if self.provider != "none":
                log.warning(f"SMS provider '{self.provider}' not available or dependencies not installed")
    
    def send_sms(self, phone_number, message):
        """
        Send SMS to a phone number
        
        Args:
            phone_number: Phone number in international format (e.g., +256771234567)
            message: SMS message content
            
        Returns:
            dict: {success: bool, message_id: str or None, error: str or None}
        """
        if not self.sms_client:
            log.warning("SMS client not initialized, logging message instead")
            self._log_message(phone_number, message)
            return {
                "success": True,  # Return success in dev mode
                "message_id": "logged",
                "error": None,
                "note": "SMS logged (provider not configured)"
            }
        
        # Normalize phone number
        phone_number = self._normalize_phone(phone_number)
        
        try:
            if self.provider == "africastalking":
                return self._send_africastalking(phone_number, message)
            elif self.provider == "twilio":
                return self._send_twilio(phone_number, message)
            else:
                return {
                    "success": False,
                    "message_id": None,
                    "error": f"Unknown provider: {self.provider}"
                }
        except Exception as e:
            log.error(f"SMS sending failed: {e}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    def _send_africastalking(self, phone_number, message):
        """Send SMS via Africa's Talking"""
        try:
            response = self.sms_client.send(
                message=message,
                recipients=[phone_number],
                sender=self.sender_id
            )
            
            # Parse response
            if response and response.get("SMSMessageData"):
                recipients = response["SMSMessageData"].get("Recipients", [])
                if recipients:
                    recipient = recipients[0]
                    status = recipient.get("status", "")
                    message_id = recipient.get("messageId", "")
                    
                    if status == "Success":
                        return {
                            "success": True,
                            "message_id": message_id,
                            "error": None
                        }
                    else:
                        return {
                            "success": False,
                            "message_id": None,
                            "error": f"SMS failed with status: {status}"
                        }
            
            return {
                "success": False,
                "message_id": None,
                "error": "Invalid response from Africa's Talking"
            }
            
        except Exception as e:
            log.error(f"Africa's Talking SMS error: {e}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    def _send_twilio(self, phone_number, message):
        """Send SMS via Twilio"""
        try:
            response = self.sms_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=phone_number
            )
            
            if response.sid:
                return {
                    "success": True,
                    "message_id": response.sid,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "message_id": None,
                    "error": "No message SID returned from Twilio"
                }
                
        except Exception as e:
            log.error(f"Twilio SMS error: {e}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    def _normalize_phone(self, phone_number):
        """Normalize phone number to international format"""
        # Remove spaces and dashes
        phone_number = phone_number.replace(" ", "").replace("-", "")
        
        # Handle Ugandan numbers
        if phone_number.startswith("0"):
            phone_number = "+256" + phone_number[1:]
        elif not phone_number.startswith("+"):
            phone_number = "+" + phone_number
        
        return phone_number
    
    def _log_message(self, phone_number, message):
        """Log message when SMS provider not configured (for development)"""
        log.info(f"[SMS LOG] To: {phone_number}, Message: {message[:50]}...")
    
    def send_application_status_notification(self, phone_number, application_number, status):
        """Send application status update notification"""
        message = f"KIU Admission Update: Your application {application_number} status has been updated to {status}. Login to view details."
        return self.send_sms(phone_number, message)
    
    def send_payment_confirmation(self, phone_number, amount, reference):
        """Send payment confirmation"""
        message = f"KIU Payment Confirmed: UGX {amount:,} received for Ref: {reference}. Thank you for your payment."
        return self.send_sms(phone_number, message)
    
    def send_otp(self, phone_number, otp_code):
        """Send OTP verification code"""
        message = f"Your KIU Admission Portal verification code is: {otp_code}. Valid for 10 minutes. Do not share this code."
        return self.send_sms(phone_number, message)
    
    def send_admission_offer(self, phone_number, program_name):
        """Send admission offer notification"""
        message = f"Congratulations! You've been offered admission to {program_name} at KIU. Please login to accept or decline the offer within 14 days."
        return self.send_sms(phone_number, message)
    
    def send_deadline_reminder(self, phone_number, application_number, days_remaining):
        """Send deadline reminder"""
        message = f"KIU Reminder: Your application {application_number} requires action. {days_remaining} days remaining. Please complete your application."
        return self.send_sms(phone_number, message)


# Singleton instance
_sms_service = None

def get_sms_service():
    """Get SMS service singleton"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service
