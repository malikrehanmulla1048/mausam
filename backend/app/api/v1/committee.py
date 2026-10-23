"""AI Credit Committee endpoints."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.core.database import get_db
from app.core.config import settings
from app.services.committee import build_evidence_bundle, run_deterministic_committee, run_bedrock_committee

router = APIRouter()


@router.post("/{business_id}/committee/run")
async def run_committee(business_id: str):
    db = get_db()
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    # Gather backend data for evidence bundle
    forecast = db.forecast_runs.find_one(
        {"business_id": business_id}, sort=[("created_at", -1)]
    ) or {}
    risk = db.risk_assessments.find_one(
        {"business_id": business_id}, sort=[("created_at", -1)]
    ) or {}

    top_findings = list(db.reconciliation_findings.find(
        {"business_id": business_id, "severity": "HIGH", "status": {"$in": ["OPEN", "REVIEWING"]}},
        {"_id": 0}
    ).limit(5))

    business_data = {
        "overview": {
            "current_cash": forecast.get("current_cash", 0),
            "total_outstanding": risk.get("total_outstanding", 0),
        },
        "forecast": {
            "runway_days": forecast.get("runway_days", 0),
            "shortfall_probability": forecast.get("shortfall_probability", 0),
            "min_balance_p50": forecast.get("monte_carlo", {}).get("min_balance_p50", 0) if forecast.get("monte_carlo") else 0,
        },
        "risk_assessment": {
            "score": risk.get("score", 0),
            "top_customer_pct": risk.get("top_customer_pct", 0),
            "overdue_amount": risk.get("overdue_amount", 0),
            "sharma_avg_delay": risk.get("sharma_avg_delay", 30),
            "reconciliation_health": risk.get("reconciliation_health", 70),
        },
        "top_findings": top_findings,
    }

    evidence_bundle = build_evidence_bundle(business_data)
    business_name = biz.get("business_name", business_id)

    # Use Bedrock if enabled, else deterministic
    if settings.BEDROCK_ENABLED:
        try:
            import boto3
            bedrock_client = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)
            result = run_bedrock_committee(evidence_bundle, business_name, bedrock_client, settings.BEDROCK_MODEL_ID)
        except Exception as e:
            result = run_deterministic_committee(evidence_bundle, business_name)
            result["bedrock_error"] = str(e)
    else:
        result = run_deterministic_committee(evidence_bundle, business_name)

    session_id = f"SESS-{uuid.uuid4().hex[:10].upper()}"
    session_doc = {
        "session_id": session_id,
        "business_id": business_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence_bundle": evidence_bundle,
        **result,
        "is_demo": biz.get("is_demo", False),
    }

    db.committee_sessions.update_one(
        {"session_id": session_id},
        {"$set": session_doc},
        upsert=True,
    )

    return {**session_doc, "session_id": session_id}


@router.get("/{business_id}/committee/latest")
async def get_latest_committee(business_id: str):
    db = get_db()
    session = db.committee_sessions.find_one(
        {"business_id": business_id}, {"_id": 0}, sort=[("created_at", -1)]
    )
    if not session:
        raise HTTPException(404, "No committee session found. Run POST /committee/run first.")
    return session
