"""Businesses routes."""
from fastapi import APIRouter, HTTPException
from app.core.database import get_db

router = APIRouter()


@router.get("")
async def list_businesses():
    db = get_db()
    businesses = list(db.businesses.find({}, {"_id": 0}).limit(50))
    return {"businesses": businesses, "total": len(businesses)}


@router.get("/{business_id}")
async def get_business(business_id: str):
    db = get_db()
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")
    return biz


@router.get("/{business_id}/overview")
async def get_overview(business_id: str):
    db = get_db()
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    # Current month stats
    outstanding = list(db.invoices.find(
        {"business_id": business_id, "status": "OUTSTANDING"}, {"_id": 0}
    ))
    total_outstanding = sum(i.get("total_amount", 0) for i in outstanding)
    overdue = [i for i in outstanding if i.get("due_date", "") < "2025-11-15"]
    overdue_amount = sum(i.get("total_amount", 0) for i in overdue)

    recent_txns = list(db.bank_transactions.find(
        {"business_id": business_id}, {"_id": 0}
    ).sort("date", -1).limit(1))
    current_cash = recent_txns[0].get("balance_after", biz.get("opening_cash", 0)) if recent_txns else biz.get("opening_cash", 0)

    forecast_run = db.forecast_runs.find_one(
        {"business_id": business_id}, {"_id": 0}, sort=[("created_at", -1)]
    )
    risk_assessment = db.risk_assessments.find_one(
        {"business_id": business_id}, {"_id": 0}, sort=[("created_at", -1)]
    )
    unread_alerts = db.alerts.count_documents({"business_id": business_id, "is_read": False})

    return {
        "business_id": business_id,
        "business_name": biz.get("business_name"),
        "owner_name": biz.get("owner_name"),
        "current_cash": round(current_cash, 2),
        "total_outstanding": round(total_outstanding, 2),
        "overdue_amount": round(overdue_amount, 2),
        "overdue_count": len(overdue),
        "weather": forecast_run.get("weather", "cloudy") if forecast_run else "unknown",
        "runway_days": forecast_run.get("runway_days", None) if forecast_run else None,
        "shortfall_probability": forecast_run.get("shortfall_probability", None) if forecast_run else None,
        "readiness_score": risk_assessment.get("score", None) if risk_assessment else None,
        "readiness_band": risk_assessment.get("band", None) if risk_assessment else None,
        "unread_alerts": unread_alerts,
        "is_demo": biz.get("is_demo", False),
        "demo_label": biz.get("demo_label"),
    }
