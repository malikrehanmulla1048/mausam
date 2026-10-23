"""
MAUSAM — Health Passport Service
Digital financial health report with cryptographic signing.
"""
import hashlib
import hmac
import json
import uuid
import base64
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings


def canonical_payload(data: dict) -> bytes:
    """Produce a stable, canonical UTF-8 JSON representation for signing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def dev_sign(payload_bytes: bytes, key: str) -> str:
    """
    DEVELOPMENT-ONLY signing using HMAC-SHA256.
    NOT an AWS KMS signature. Clearly labelled.
    """
    mac = hmac.new(key.encode("utf-8"), payload_bytes, digestmod=hashlib.sha256)
    return base64.urlsafe_b64encode(mac.digest()).decode("utf-8")


def dev_verify(payload_bytes: bytes, signature: str, key: str) -> bool:
    """Verify a dev HMAC-SHA256 signature."""
    try:
        expected = dev_sign(payload_bytes, key)
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False


def generate_passport(
    business_data: dict,
    risk_assessment: dict,
    forecast: dict,
    findings: list[dict],
    valid_days: int = 30,
) -> dict:
    """
    Generate a Health Passport with cryptographic signing.
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=valid_days)
    public_id = str(uuid.uuid4()).replace("-", "")[:24]
    passport_id = f"PASS-{uuid.uuid4().hex[:12].upper()}"

    # Signed payload — only summary data, never full bank statements
    signed_payload = {
        "passport_id": passport_id,
        "public_id": public_id,
        "business_name": business_data.get("business_name", ""),
        "gstn_masked": business_data.get("gstn", "")[:8] + "****" if business_data.get("gstn") else "",
        "generated_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "readiness_score": risk_assessment.get("score", 0),
        "readiness_band": risk_assessment.get("band", ""),
        "runway_days": forecast.get("runway_days", 0),
        "shortfall_probability": forecast.get("shortfall_probability", 0),
        "open_high_findings": len([f for f in findings if f.get("severity") == "HIGH" and f.get("status") != "RESOLVED"]),
        "data_period_start": business_data.get("data_period_start", ""),
        "data_period_end": business_data.get("data_period_end", ""),
        "schema_version": "1.0",
        "is_demo": business_data.get("is_demo", True),
    }

    payload_bytes = canonical_payload(signed_payload)
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()

    if settings.KMS_SIGNING_ENABLED:
        # TODO: KMS signing integration
        signing_method = "AWS_KMS"
        signature = "KMS_SIGNATURE_PLACEHOLDER"
        key_id = settings.KMS_KEY_ID
    else:
        signing_method = "DEV_HMAC_SHA256"
        signature = dev_sign(payload_bytes, settings.DEV_SIGNING_KEY)
        key_id = "dev-key-v1"

    passport = {
        "passport_id": passport_id,
        "public_id": public_id,
        "business_id": business_data.get("business_id", ""),
        "business_name": business_data.get("business_name", ""),
        "generated_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "valid_days": valid_days,
        "status": "ACTIVE",
        "revoked": False,
        "revoked_at": None,
        "revocation_reason": None,

        # Score summary
        "readiness_score": risk_assessment.get("score", 0),
        "readiness_band": risk_assessment.get("band", ""),
        "score_disclaimer": risk_assessment.get("disclaimer", ""),
        "score_components": risk_assessment.get("components", {}),

        # Cash flow summary
        "runway_days": forecast.get("runway_days", 0),
        "shortfall_probability": forecast.get("shortfall_probability", 0),
        "weather": forecast.get("weather", ""),
        "current_cash": forecast.get("current_cash", 0),

        # Reconciliation summary
        "total_findings": len(findings),
        "open_high_findings": signed_payload["open_high_findings"],
        "open_medium_findings": len([f for f in findings if f.get("severity") == "MEDIUM" and f.get("status") != "RESOLVED"]),

        # Data provenance
        "data_sources": ["bank_statements", "invoices", "gst_summaries"],
        "data_period_start": business_data.get("data_period_start", ""),
        "data_period_end": business_data.get("data_period_end", ""),
        "is_demo": business_data.get("is_demo", True),
        "demo_label": "SYNTHETIC DEMONSTRATION DATA" if business_data.get("is_demo") else None,

        # Signature
        "signed_payload": signed_payload,
        "payload_hash": payload_hash,
        "signature": signature,
        "signing_method": signing_method,
        "signing_key_id": key_id,
        "signing_label": (
            "⚠️ Development HMAC-SHA256 — Not an AWS KMS signature"
            if signing_method == "DEV_HMAC_SHA256"
            else "AWS KMS Asymmetric Signature"
        ),

        # Sharing
        "share_links": [],
        "access_history": [],
    }

    return passport


def verify_passport(passport: dict) -> dict:
    """
    Verify the cryptographic signature of a passport.
    Returns verification result with clear status labels.
    """
    now = datetime.now(timezone.utc)

    if passport.get("revoked"):
        return {
            "status": "REVOKED",
            "label": "Report Revoked",
            "message": f"This report was revoked on {passport.get('revoked_at')}.",
            "verified": False,
        }

    expires_at = datetime.fromisoformat(passport["expires_at"])
    if now > expires_at:
        return {
            "status": "EXPIRED",
            "label": "Report Expired",
            "message": f"This report expired on {expires_at.strftime('%d %B %Y')}.",
            "verified": False,
        }

    signed_payload = passport.get("signed_payload", {})
    payload_bytes = canonical_payload(signed_payload)
    signature = passport.get("signature", "")
    signing_method = passport.get("signing_method", "")
    expected_hash = passport.get("payload_hash", "")

    # Verify payload hash
    actual_hash = hashlib.sha256(payload_bytes).hexdigest()
    if actual_hash != expected_hash:
        return {
            "status": "INVALID",
            "label": "Signature Invalid — Report Modified",
            "message": "The report content does not match its original signed state. This report may have been tampered with.",
            "verified": False,
        }

    # Verify signature
    if signing_method == "DEV_HMAC_SHA256":
        sig_valid = dev_verify(payload_bytes, signature, settings.DEV_SIGNING_KEY)
    elif signing_method == "AWS_KMS":
        # TODO: KMS verification
        sig_valid = False
    else:
        sig_valid = False

    if not sig_valid:
        return {
            "status": "INVALID",
            "label": "Signature Invalid",
            "message": "The cryptographic signature could not be verified.",
            "verified": False,
        }

    return {
        "status": "VALID",
        "label": "Signature Valid",
        "message": (
            "The signed content of this report has not been altered since it was generated. "
            "Signature validity does not certify the truthfulness of the underlying source data."
        ),
        "verified": True,
        "signing_method": signing_method,
        "signing_label": passport.get("signing_label", ""),
        "generated_at": passport.get("generated_at"),
        "expires_at": passport.get("expires_at"),
        "is_demo": passport.get("is_demo", False),
    }
