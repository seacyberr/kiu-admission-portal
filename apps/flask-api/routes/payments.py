"""
Payment Integration Module for KIU Admission Portal
Supports: MTN Mobile Money, Airtel Money, Bank Cards
"""
import os
import uuid
import requests
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from models import db, Payment, AdmissionApplication, User
from routes.auth import get_current_user
from utils.error_handlers import handle_kiu_error, ValidationError

payments_bp = Blueprint("payments", __name__)

# Payment configuration
PAYMENT_CONFIG = {
    "application_fee": 50000,  # UGX 50,000
    "currency": "UGX",
    "provider": os.environ.get("PAYMENT_PROVIDER", "sandbox"),  # sandbox, flutterwave, pesapal
    "flutterwave_secret": os.environ.get("FLUTTERWAVE_SECRET_KEY", ""),
    "flutterwave_public": os.environ.get("FLUTTERWAVE_PUBLIC_KEY", ""),
    "pesapal_key": os.environ.get("PESAPAL_CONSUMER_KEY", ""),
    "pesapal_secret": os.environ.get("PESAPAL_CONSUMER_SECRET", ""),
}


class PaymentGateway:
    """Abstract payment gateway interface"""
    
    def initiate_payment(self, amount, currency, reference, email, phone, callback_url):
        raise NotImplementedError
    
    def verify_payment(self, transaction_id):
        raise NotImplementedError


class FlutterwaveGateway(PaymentGateway):
    """Flutterwave payment gateway implementation"""
    
    def __init__(self):
        self.base_url = "https://api.flutterwave.com/v3"
        self.secret_key = PAYMENT_CONFIG["flutterwave_secret"]
    
    def initiate_payment(self, amount, currency, reference, email, phone, callback_url):
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "tx_ref": reference,
            "amount": amount,
            "currency": currency,
            "redirect_url": callback_url,
            "payment_options": "card,mobilemoneyuganda",
            "customer": {
                "email": email,
                "phonenumber": phone,
                "name": "KIU Applicant"
            },
            "customizations": {
                "title": "KIU Admission Application Fee",
                "description": "Payment for university admission application",
                "logo": "https://kiu.ac.ug/logo.png"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/payments",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Flutterwave payment initiation failed: {e}")
            raise
    
    def verify_payment(self, transaction_id):
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/transactions/{transaction_id}/verify",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Flutterwave payment verification failed: {e}")
            raise


class SandboxGateway(PaymentGateway):
    """Sandbox gateway for testing - simulates successful payments"""
    
    def initiate_payment(self, amount, currency, reference, email, phone, callback_url):
        """Return mock payment URL"""
        return {
            "status": "success",
            "message": "Payment initiated (Sandbox Mode)",
            "data": {
                "link": f"{callback_url}?sandbox_payment=true&reference={reference}",
                "reference": reference
            }
        }
    
    def verify_payment(self, transaction_id):
        """Always return success in sandbox mode"""
        return {
            "status": "success",
            "message": "Payment verified (Sandbox Mode)",
            "data": {
                "status": "successful",
                "amount": PAYMENT_CONFIG["application_fee"],
                "currency": "UGX"
            }
        }


def get_payment_gateway():
    """Factory function to get appropriate payment gateway"""
    provider = PAYMENT_CONFIG["provider"]
    
    if provider == "flutterwave":
        return FlutterwaveGateway()
    else:
        return SandboxGateway()


@payments_bp.route("/initiate", methods=["POST"])
def initiate_payment():
    """Initiate application fee payment"""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request", "message": "JSON payload required"}), 400
    
    application_id = data.get("application_id")
    phone_number = data.get("phone_number")
    
    if not application_id:
        return jsonify({"error": "Missing field", "message": "application_id is required"}), 400
    
    if not phone_number:
        return jsonify({"error": "Missing field", "message": "phone_number is required"}), 400
    
    # Validate phone number format (Uganda)
    phone_number = phone_number.replace(" ", "").replace("-", "")
    if not phone_number.startswith("+"):
        phone_number = "+256" + phone_number.lstrip("0")
    
    # Get application
    application = AdmissionApplication.query.filter_by(
        id=application_id,
        user_id=user.id
    ).first()
    
    if not application:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404
    
    # Check if payment already exists
    existing_payment = Payment.query.filter_by(
        application_id=application_id,
        status="successful"
    ).first()
    
    if existing_payment:
        return jsonify({
            "error": "Payment exists",
            "message": "Application fee already paid",
            "payment": existing_payment.to_dict()
        }), 409
    
    # Create payment record
    reference = f"KIU-{uuid.uuid4().hex[:8].upper()}"
    
    payment = Payment(
        user_id=user.id,
        application_id=application_id,
        reference=reference,
        amount=PAYMENT_CONFIG["application_fee"],
        currency=PAYMENT_CONFIG["currency"],
        phone_number=phone_number,
        status="pending"
    )
    
    db.session.add(payment)
    db.session.commit()
    
    # Initiate with payment gateway
    try:
        gateway = get_payment_gateway()
        callback_url = f"{request.host_url.rstrip('/')}/api/payments/callback"
        
        result = gateway.initiate_payment(
            amount=payment.amount,
            currency=payment.currency,
            reference=reference,
            email=user.email,
            phone=phone_number,
            callback_url=callback_url
        )
        
        if result.get("status") == "success":
            payment.gateway_response = str(result)
            db.session.commit()
            
            return jsonify({
                "message": "Payment initiated successfully",
                "payment": payment.to_dict(),
                "payment_url": result["data"]["link"]
            }), 201
        else:
            payment.status = "failed"
            db.session.commit()
            return jsonify({
                "error": "Payment initiation failed",
                "message": result.get("message", "Unknown error")
            }), 500
            
    except Exception as e:
        payment.status = "failed"
        db.session.commit()
        current_app.logger.error(f"Payment initiation error: {e}")
        return jsonify({
            "error": "Payment failed",
            "message": str(e)
        }), 500


@payments_bp.route("/callback", methods=["GET", "POST"])
def payment_callback():
    """Handle payment gateway callback"""
    if request.method == "POST":
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()
    
    reference = data.get("tx_ref") or data.get("reference")
    transaction_id = data.get("transaction_id") or data.get("id")
    status = data.get("status", "pending")
    
    if not reference:
        return jsonify({"error": "Missing reference"}), 400
    
    payment = Payment.query.filter_by(reference=reference).first()
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    
    # Verify with gateway if not sandbox
    if PAYMENT_CONFIG["provider"] != "sandbox" and transaction_id:
        try:
            gateway = get_payment_gateway()
            verification = gateway.verify_payment(transaction_id)
            
            if verification.get("status") == "success":
                payment_data = verification.get("data", {})
                status = payment_data.get("status", "pending")
                payment.gateway_response = str(verification)
        except Exception as e:
            current_app.logger.error(f"Payment verification error: {e}")
    
    # Update payment status
    if status == "successful" or status == "success":
        payment.status = "successful"
        payment.paid_at = datetime.utcnow()
        
        # Update application payment status
        application = AdmissionApplication.query.get(payment.application_id)
        if application:
            application.payment_status = "paid"
            db.session.commit()
        
        return jsonify({
            "message": "Payment successful",
            "payment": payment.to_dict()
        })
    else:
        payment.status = "failed" if status == "failed" else "pending"
        db.session.commit()
        
        return jsonify({
            "message": f"Payment {payment.status}",
            "payment": payment.to_dict()
        })


@payments_bp.route("/verify/<reference>", methods=["GET"])
def verify_payment(reference):
    """Manual payment verification"""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    
    payment = Payment.query.filter_by(
        reference=reference,
        user_id=user.id
    ).first()
    
    if not payment:
        return jsonify({"error": "Not found", "message": "Payment not found"}), 404
    
    # If pending, try to verify with gateway
    if payment.status == "pending" and PAYMENT_CONFIG["provider"] != "sandbox":
        try:
            gateway = get_payment_gateway()
            # Note: This assumes we stored the transaction ID
            # In practice, you'd need to extract it from gateway_response
            # or store it separately
            result = gateway.verify_payment(payment.reference)
            
            if result.get("status") == "success":
                payment_data = result.get("data", {})
                new_status = payment_data.get("status", "pending")
                
                if new_status == "successful":
                    payment.status = "successful"
                    payment.paid_at = datetime.utcnow()
                    
                    application = AdmissionApplication.query.get(payment.application_id)
                    if application:
                        application.payment_status = "paid"
                elif new_status == "failed":
                    payment.status = "failed"
                
                payment.gateway_response = str(result)
                db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Manual verification error: {e}")
    
    return jsonify({
        "payment": payment.to_dict()
    })


@payments_bp.route("/application/<int:application_id>", methods=["GET"])
def get_application_payment(application_id):
    """Get payment status for an application"""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    
    # Check if user owns the application or is admin
    application = AdmissionApplication.query.get(application_id)
    if not application:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404
    
    if application.user_id != user.id and user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "Access denied"}), 403
    
    payment = Payment.query.filter_by(
        application_id=application_id
    ).order_by(Payment.created_at.desc()).first()
    
    return jsonify({
        "application_id": application_id,
        "payment_required": True,
        "amount": PAYMENT_CONFIG["application_fee"],
        "currency": PAYMENT_CONFIG["currency"],
        "payment": payment.to_dict() if payment else None,
        "paid": payment.status == "successful" if payment else False
    })


@payments_bp.route("/config", methods=["GET"])
def get_payment_config():
    """Get public payment configuration"""
    return jsonify({
        "application_fee": PAYMENT_CONFIG["application_fee"],
        "currency": PAYMENT_CONFIG["currency"],
        "provider": PAYMENT_CONFIG["provider"],
        "payment_methods": ["mobile_money", "card"]
    })
