"""
Email Service - Handles all email operations
Separates email delivery from business logic
"""
import os
import hashlib
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

log = logging.getLogger(__name__)


class EmailService:
    """Service layer for email operations"""
    
    BREVO_SMTP_HOST = "smtp-relay.brevo.com"
    BREVO_SMTP_PORT = 587
    BREVO_SMTP_USER = os.environ.get("BREVO_SMTP_USER", "")
    BREVO_SMTP_KEY = os.environ.get("BREVO_SMTP_KEY", "")
    EMAIL_FROM = "KIU Portal <noreply@kiu.ac.ug>"
    
    @classmethod
    def send_otp_email(cls, to_email: str, otp: str, full_name: str = "") -> bool:
        """Send OTP verification email"""
        if not cls.BREVO_SMTP_KEY:
            log.warning("BREVO_SMTP_KEY not set — email not sent (see terminal for OTP)")
            return False
        
        greeting = f"Dear {full_name}," if full_name else "Hello,"
        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;
                    border:1px solid #e5e7eb;border-radius:12px;">
          <h2 style="color:#1e3a5f;text-align:center;">Kampala International University</h2>
          <p style="color:#374151;">{greeting}</p>
          <p style="color:#374151;">Your One-Time Password (OTP):</p>
          <div style="text-align:center;margin:32px 0;">
            <span style="font-size:40px;font-weight:bold;letter-spacing:12px;color:#1e3a5f;
                         background:#f0f4ff;padding:16px 32px;border-radius:8px;
                         display:inline-block;">{otp}</span>
          </div>
          <p style="color:#6b7280;font-size:14px;">
            Expires in <strong>10 minutes</strong>. Do not share it.
          </p>
        </div>
        """
        
        return cls._send_email(
            to_email=to_email,
            subject="Your KIU Portal Verification Code",
            html_body=html_body
        )
    
    @classmethod
    def _send_email(cls, to_email: str, subject: str, html_body: str) -> bool:
        """Internal method to send email via SMTP"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cls.EMAIL_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))
        
        try:
            with smtplib.SMTP(cls.BREVO_SMTP_HOST, cls.BREVO_SMTP_PORT, timeout=10) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(cls.BREVO_SMTP_USER, cls.BREVO_SMTP_KEY)
                smtp.sendmail(cls.EMAIL_FROM, to_email, msg.as_string())
            
            # Log with hashed email for privacy
            email_hash = hashlib.sha256(to_email.encode()).hexdigest()[:8]
            log.info("Email sent via Brevo - recipient_hash=%s", email_hash)
            return True
            
        except Exception as exc:
            email_hash = hashlib.sha256(to_email.encode()).hexdigest()[:8]
            log.error("Brevo email failed for recipient_hash=%s: %s", email_hash, exc)
            return False
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if email service is properly configured"""
        return bool(cls.BREVO_SMTP_KEY)


class EmailError(Exception):
    """Email-specific errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
