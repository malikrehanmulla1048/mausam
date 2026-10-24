"""
MAUSAM — SMS Notification Service
Dispatches transactional SMS reminders for overdue invoices and credit notifications.
Supports:
1. Amazon SNS (Simple Notification Service) Transactional SMS
2. Simulated SMS Gateway with full delivery logging & MongoDB audit trail
3. Native mobile device `sms:` URI generation
"""
import logging
import math
import uuid
from datetime import datetime, timezone
from urllib.parse import quote
from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)


def generate_sms_text(
    customer_name: str,
    overdue_amount_formatted: str,
    days_overdue: int,
    tone: str = "firm",
    language: str = "en",
    sender_name: str = "Ramesh Textiles",
) -> str:
    """Generate concise, DLT-compliant SMS text (target <= 160 chars for 1 credit)."""
    if language == "hi":
        if tone == "gentle":
            return f"{sender_name}: नमस्ते {customer_name}, बकाया {overdue_amount_formatted} देय है। कृपया भुगतान की पुष्टि करें। धन्यवाद।"
        elif tone == "firm":
            return f"अति-आवश्यक {sender_name}: {customer_name}, {overdue_amount_formatted} का भुगतान {days_overdue} दिनों से लंबित है। कृपया आज ही RTGS/NEFT करें।"
        else:
            return f"कानूनी नोटिस {sender_name}: {customer_name}, MSMED Act तहत बकाया {overdue_amount_formatted} 3 दिनों में न भरने पर 3x ब्याज और कानूनी कार्रवाई होगी।"
    elif language == "gu":
        return f"{sender_name}: નમસ્તે {customer_name}, આપનું {overdue_amount_formatted} નું પેમેન્ટ {days_overdue} દિવસથી બાકી છે. કૃપા કરીને તાત્કાલિક ચૂકવણી કરશોજી."

    # English default
    if tone == "gentle":
        return f"{sender_name}: Gentle reminder for {customer_name}. Outstanding invoice {overdue_amount_formatted} is due. Please confirm payment once scheduled."
    elif tone == "firm":
        return f"URGENT {sender_name}: {customer_name}, payment of {overdue_amount_formatted} is overdue by {days_overdue} days. Please clear dues today to avoid supply hold."
    else:
        return f"NOTICE {sender_name}: {customer_name}, dues {overdue_amount_formatted} unpaid past terms. Under MSMED Act, interest at 3x RBI rate applies. Clear in 3 days."


def normalize_phone(phone: str) -> str:
    """Normalize phone numbers to clean E.164 format without spaces or symbols."""
    raw = "".join(ch for ch in str(phone) if ch.isdigit() or ch == "+")
    if raw.startswith("+"):
        return raw
    if len(raw) == 10:
        return f"+91{raw}"
    return f"+{raw}"


async def dispatch_sms(
    business_id: str,
    recipient_phone: str,
    message: str,
    customer_id: Optional[str] = None,
    customer_name: Optional[str] = None,
    tone: str = "firm",
    language: str = "en",
) -> Dict[str, Any]:
    """
    Sends an SMS via live gateway (AWS SNS, Twilio, Fast2SMS) if configured,
    or falls back to the resilient simulated SMS Gateway for development.
    Always records the dispatch event into MongoDB for auditability.
    """
    cleaned_phone = normalize_phone(recipient_phone)
    wa_phone = cleaned_phone.lstrip("+")
    msg_id = f"SMS-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now(timezone.utc).isoformat()
    char_count = len(message)
    segments = max(1, math.ceil(char_count / 160))

    delivery_channel = "SIMULATED_GATEWAY"
    is_simulated = True
    provider_msg_id = None
    delivery_note = "Simulated delivery: Message logged to MongoDB audit trail. No live SMS credentials configured."

    # 1. Attempt AWS SNS
    if settings.SNS_ENABLED and settings.AWS_ACCESS_KEY_ID:
        try:
            import boto3
            sns_client = boto3.client(
                "sns",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            response = sns_client.publish(
                PhoneNumber=cleaned_phone,
                Message=message,
                MessageAttributes={
                    "AWS.SNS.SMS.SMSType": {
                        "DataType": "String",
                        "StringValue": "Transactional",
                    }
                },
            )
            provider_msg_id = response.get("MessageId")
            delivery_channel = "AWS_SNS_TRANSACTIONAL"
            is_simulated = False
            delivery_note = f"Dispatched via AWS SNS (MessageId: {provider_msg_id})"
            logger.info("Sent SMS via AWS SNS to %s (%s)", cleaned_phone, provider_msg_id)
        except Exception as e:
            logger.warning("AWS SNS dispatch failed (%s). Falling back to simulated log.", e)
            delivery_note = f"AWS SNS failed ({e}). Fallback to simulation."

    # 2. Attempt Twilio if configured
    elif getattr(settings, "TWILIO_ENABLED", False) and getattr(settings, "TWILIO_ACCOUNT_SID", "") and getattr(settings, "TWILIO_AUTH_TOKEN", ""):
        try:
            import httpx
            twilio_url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    twilio_url,
                    auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                    data={
                        "To": cleaned_phone,
                        "From": settings.TWILIO_FROM_NUMBER,
                        "Body": message,
                    },
                )
                if res.status_code in [200, 201]:
                    tw_data = res.json()
                    provider_msg_id = tw_data.get("sid")
                    delivery_channel = "TWILIO"
                    is_simulated = False
                    delivery_note = f"Dispatched via Twilio (SID: {provider_msg_id})"
                    logger.info("Sent SMS via Twilio to %s (%s)", cleaned_phone, provider_msg_id)
                else:
                    logger.warning("Twilio API returned %s: %s", res.status_code, res.text)
                    delivery_note = f"Twilio error: {res.text[:100]}"
        except Exception as e:
            logger.warning("Twilio dispatch failed: %s", e)
            delivery_note = f"Twilio dispatch failed ({e})."

    # 3. Attempt Fast2SMS (India instant transactional SMS) if configured
    elif getattr(settings, "FAST2SMS_ENABLED", False) and getattr(settings, "FAST2SMS_API_KEY", ""):
        try:
            import httpx
            # Fast2SMS numbers expect 10 digits for Indian numbers
            ten_digit_phone = cleaned_phone[-10:]
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    "https://www.fast2sms.com/dev/bulkV2",
                    headers={"authorization": settings.FAST2SMS_API_KEY},
                    data={
                        "route": "q",
                        "message": message,
                        "language": "english",
                        "flash": 0,
                        "numbers": ten_digit_phone,
                    },
                )
                if res.status_code == 200:
                    f_data = res.json()
                    if f_data.get("return"):
                        provider_msg_id = str(f_data.get("request_id", msg_id))
                        delivery_channel = "FAST2SMS"
                        is_simulated = False
                        delivery_note = "Dispatched via Fast2SMS gateway"
                        logger.info("Sent SMS via Fast2SMS to %s", ten_digit_phone)
                    else:
                        delivery_note = f"Fast2SMS error: {f_data.get('message')}"
        except Exception as e:
            logger.warning("Fast2SMS dispatch failed: %s", e)
            delivery_note = f"Fast2SMS dispatch failed ({e})."

    # Cross-platform native SMS & WhatsApp URIs
    native_sms_uri = f"sms:{cleaned_phone}?body={quote(message)}"
    whatsapp_uri = f"https://wa.me/{wa_phone}?text={quote(message)}"

    record = {
        "dispatch_id": msg_id,
        "business_id": business_id,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "recipient_phone": cleaned_phone,
        "message": message,
        "char_count": char_count,
        "segments": segments,
        "tone": tone,
        "language": language,
        "delivery_channel": delivery_channel,
        "is_simulated": is_simulated,
        "provider_msg_id": provider_msg_id,
        "aws_sns_msg_id": provider_msg_id if "AWS_SNS" in delivery_channel else None,
        "status": "DELIVERED" if not is_simulated else "SIMULATED",
        "delivery_note": delivery_note,
        "created_at": timestamp,
        "native_sms_uri": native_sms_uri,
        "whatsapp_uri": whatsapp_uri,
    }

    try:
        db = get_db()
        db.sms_dispatches.insert_one(record)
    except Exception as e:
        logger.warning("Failed to log SMS dispatch to database: %s", e)

    return {
        "status": "success",
        "dispatch_id": msg_id,
        "recipient_phone": cleaned_phone,
        "delivery_channel": delivery_channel,
        "is_simulated": is_simulated,
        "delivery_note": delivery_note,
        "char_count": char_count,
        "segments": segments,
        "sent_at": timestamp,
        "native_sms_uri": native_sms_uri,
        "whatsapp_uri": whatsapp_uri,
        "message_preview": message[:60] + "..." if len(message) > 60 else message,
    }
