"""Alerts Centre endpoints."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db

router = APIRouter()

ALERT_TEMPLATES = {
    "CASH_SHORTFALL": {
        "en": "Your projected cash balance may fall below your reserve of ₹{reserve:,.0f} on {date}. {customer_name} has ₹{outstanding:,.0f} outstanding. Consider requesting an earlier payment.",
        "hi": "आपका अनुमानित नकद शेष {date} को आपके आरक्षित ₹{reserve:,.0f} से नीचे जा सकता है। {customer_name} का ₹{outstanding:,.0f} बकाया है। जल्दी भुगतान का अनुरोध करें।",
        "kn": "ನಿಮ್ಮ ಅಂದಾಜು ನಗದು ಶಿಲ್ಕು {date} ರಂದು ₹{reserve:,.0f} ರ ಮೀಸಲು ಮಿತಿಗಿಂತ ಕಡಿಮೆಯಾಗಬಹುದು। {customer_name} ₹{outstanding:,.0f} ಬಾಕಿ ಇದೆ।",
    },
    "OVERDUE_INVOICE": {
        "en": "Invoice {invoice_id} from {customer_name} for ₹{amount:,.0f} is {days_overdue} days overdue.",
        "hi": "चालान {invoice_id} {customer_name} से ₹{amount:,.0f} के लिए {days_overdue} दिन बकाया है।",
        "kn": "ಇನ್‌ವಾಯ್ಸ್ {invoice_id} {customer_name} ನಿಂದ ₹{amount:,.0f} ಗಾಗಿ {days_overdue} ದಿನಗಳು ಬಾಕಿ ಇದೆ।",
    },
    "RECONCILIATION_FINDING": {
        "en": "A {severity} reconciliation issue was detected: {description}. Review in Truth Check.",
        "hi": "एक {severity} सुलह समस्या पाई गई: {description}। ट्रुथ चेक में समीक्षा करें।",
        "kn": "ಒಂದು {severity} ಸಮನ್ವಯ ಸಮಸ್ಯೆ ಪತ್ತೆಯಾಯಿತು: {description}। ಟ್ರೂತ್ ಚೆಕ್‌ನಲ್ಲಿ ಪರಿಶೀಲಿಸಿ।",
    },
}


class AlertPreviewRequest(BaseModel):
    alert_type: str
    language: str = "en"
    params: dict = {}


@router.get("/{business_id}/alerts")
async def list_alerts(
    business_id: str,
    is_read: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_db()
    query = {"business_id": business_id}
    if is_read is not None:
        query["is_read"] = is_read

    skip = (page - 1) * limit
    alerts = list(db.alerts.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit))
    total = db.alerts.count_documents(query)
    unread = db.alerts.count_documents({"business_id": business_id, "is_read": False})

    return {"alerts": alerts, "total": total, "unread": unread, "page": page, "limit": limit}


@router.post("/{business_id}/alerts/{alert_id}/read")
async def mark_alert_read(business_id: str, alert_id: str):
    db = get_db()
    result = db.alerts.update_one(
        {"business_id": business_id, "alert_id": alert_id},
        {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, f"Alert {alert_id} not found")
    return {"status": "ok"}


@router.post("/{business_id}/alerts/preview")
async def preview_alert(business_id: str, req: AlertPreviewRequest):
    template = ALERT_TEMPLATES.get(req.alert_type)
    if not template:
        raise HTTPException(400, f"Unknown alert type: {req.alert_type}")

    lang = req.language if req.language in template else "en"
    text_template = template[lang]

    try:
        text = text_template.format(**req.params)
    except KeyError as e:
        raise HTTPException(400, f"Missing parameter in alert template: {e}")

    # Try AWS Translate if enabled
    translate_info = {"translated": False, "service": "none"}
    if req.language != "en" and __import__("app.core.config", fromlist=["settings"]).settings.TRANSLATE_ENABLED:
        try:
            import boto3
            translate = boto3.client("translate", region_name=__import__("app.core.config", fromlist=["settings"]).settings.AWS_REGION)
            lang_code = {"hi": "hi", "kn": "kn"}.get(req.language, "en")
            result = translate.translate_text(Text=text, SourceLanguageCode="en", TargetLanguageCode=lang_code)
            text = result["TranslatedText"]
            translate_info = {"translated": True, "service": "AWS_Translate"}
        except Exception:
            translate_info = {"translated": False, "service": "template_fallback"}

    return {
        "alert_type": req.alert_type,
        "language": req.language,
        "text": text,
        "translate_info": translate_info,
        "polly_available": __import__("app.core.config", fromlist=["settings"]).settings.POLLY_ENABLED,
        "delivery_channels": ["in_app"],
        "whatsapp_available": False,
        "whatsapp_note": "WhatsApp delivery requires Meta Business approval. Not configured in this deployment.",
    }


@router.post("/{business_id}/alerts/generate")
async def generate_alerts(business_id: str):
    """Auto-generate alerts from current system state."""
    db = get_db()
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    alerts_generated = []
    forecast = db.forecast_runs.find_one({"business_id": business_id}, sort=[("created_at", -1)])
    findings = list(db.reconciliation_findings.find(
        {"business_id": business_id, "status": "OPEN", "severity": "HIGH"}, {"_id": 0}
    ).limit(3))

    if forecast and forecast.get("shortfall_probability", 0) > 0.30:
        alert_id = f"ALERT-{uuid.uuid4().hex[:8].upper()}"
        alert = {
            "alert_id": alert_id,
            "business_id": business_id,
            "alert_type": "CASH_SHORTFALL",
            "severity": "HIGH" if forecast.get("shortfall_probability", 0) > 0.50 else "MEDIUM",
            "title": "Cash shortfall risk detected",
            "message_en": f"Projected shortfall in {forecast.get('runway_days', '?')} days. Shortfall probability: {forecast.get('shortfall_probability', 0):.0%}.",
            "message_hi": f"अनुमानित कमी {forecast.get('runway_days', '?')} दिनों में। कमी संभावना: {forecast.get('shortfall_probability', 0):.0%}।",
            "triggering_date": forecast.get("earliest_shortfall_date"),
            "evidence_refs": [f"FCAST-{forecast.get('run_id', '')}"],
            "suggested_action": "Open Rescue Planner to evaluate interventions.",
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "delivery_status": "in_app",
            "is_demo": biz.get("is_demo", False),
        }
        db.alerts.update_one(
            {"alert_id": alert_id},
            {"$set": alert},
            upsert=True,
        )
        alerts_generated.append(alert)

    for finding in findings:
        alert_id = f"ALERT-{uuid.uuid4().hex[:8].upper()}"
        alert = {
            "alert_id": alert_id,
            "business_id": business_id,
            "alert_type": "RECONCILIATION_FINDING",
            "severity": finding.get("severity", "MEDIUM"),
            "title": f"Reconciliation issue: {finding.get('finding_type', '')}",
            "message_en": finding.get("explanation", "A reconciliation issue requires your attention."),
            "message_hi": "एक सुलह समस्या आपके ध्यान की आवश्यकता है।",
            "evidence_refs": [finding.get("finding_id", "")],
            "suggested_action": finding.get("recommended_action", "Review in Truth Check."),
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "delivery_status": "in_app",
            "is_demo": biz.get("is_demo", False),
        }
        db.alerts.update_one({"alert_id": alert_id}, {"$set": alert}, upsert=True)
        alerts_generated.append(alert)

    return {"alerts_generated": len(alerts_generated), "alerts": alerts_generated}
