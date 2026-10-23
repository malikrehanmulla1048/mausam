"""Cash Mausam forecast endpoints."""
import uuid
from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.services.analytics import (
    build_daily_cash_schedule, monte_carlo_forecast,
    compute_runway_days, classify_weather
)

router = APIRouter()


class ForecastRunRequest(BaseModel):
    forecast_days: int = 42
    n_simulations: int = 500
    minimum_reserve: float = 100_000
    custom_inflows: Optional[list] = None
    custom_outflows: Optional[list] = None


@router.get("/{business_id}/cash-forecast")
async def get_latest_forecast(business_id: str):
    db = get_db()
    run = db.forecast_runs.find_one(
        {"business_id": business_id}, {"_id": 0}, sort=[("created_at", -1)]
    )
    if not run:
        raise HTTPException(404, "No forecast found. Run POST /forecast/run first.")
    return run


@router.post("/{business_id}/forecast/run")
async def run_forecast(business_id: str, req: ForecastRunRequest):
    db = get_db()

    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    # Determine current cash
    recent_txn = db.bank_transactions.find_one(
        {"business_id": business_id}, sort=[("date", -1)]
    )
    current_cash = recent_txn.get("balance_after", biz.get("opening_cash", 480_000)) if recent_txn else biz.get("opening_cash", 480_000)

    today = date.today()
    forecast_end = today + timedelta(days=req.forecast_days)

    # Expected inflows: outstanding invoices with predicted payment dates
    predictions = list(db.payment_predictions.find(
        {"business_id": business_id}, {"_id": 0}
    ))
    pred_map = {p["invoice_id"]: p for p in predictions}

    outstanding = list(db.invoices.find(
        {"business_id": business_id, "status": "OUTSTANDING"}, {"_id": 0}
    ))

    expected_inflows = []
    for inv in outstanding:
        inv_id = inv["invoice_id"]
        pred = pred_map.get(inv_id)
        if pred:
            pay_date_str = pred.get("predicted_payment_date", inv.get("due_date", ""))
        else:
            pay_date_str = inv.get("due_date", "")

        if not pay_date_str:
            continue
        pay_date = date.fromisoformat(pay_date_str)
        if today <= pay_date <= forecast_end:
            expected_inflows.append({
                "date": pay_date_str,
                "amount": inv.get("total_amount", 0),
                "source": "invoice_collection",
                "customer_id": inv.get("customer_id"),
                "customer_name": inv.get("customer_name"),
                "invoice_id": inv_id,
            })

    # Expected outflows: upcoming obligations
    obligations = list(db.obligations.find({"business_id": business_id}, {"_id": 0}))
    expected_outflows = []

    for obl in obligations:
        for month_offset in range(2):  # next 2 months
            obl_month = today.month + month_offset
            obl_year = today.year + (obl_month - 1) // 12
            obl_month = ((obl_month - 1) % 12) + 1
            day = min(obl.get("day_of_month", 1), 28)
            try:
                obl_date = date(obl_year, obl_month, day)
            except ValueError:
                obl_date = date(obl_year, obl_month, 28)

            if today <= obl_date <= forecast_end:
                amount = obl.get("amount", 0)
                if obl.get("type") == "tax":
                    # Estimate GST from recent turnover
                    amount = 45_000  # demo estimate
                if amount > 0:
                    expected_outflows.append({
                        "date": obl_date.isoformat(),
                        "amount": amount,
                        "category": obl.get("type", "other"),
                        "description": obl.get("name", ""),
                        "obligation_id": obl.get("obligation_id"),
                    })

    # Add custom overrides
    if req.custom_inflows:
        expected_inflows.extend(req.custom_inflows)
    if req.custom_outflows:
        expected_outflows.extend(req.custom_outflows)

    # Build daily schedule
    daily_schedule = build_daily_cash_schedule(
        current_cash=current_cash,
        forecast_days=req.forecast_days,
        expected_inflows=expected_inflows,
        expected_outflows=expected_outflows,
        minimum_reserve=req.minimum_reserve,
    )

    # Monte Carlo
    mc = monte_carlo_forecast(
        current_cash=current_cash,
        base_daily_schedule=daily_schedule,
        n_simulations=req.n_simulations,
        minimum_reserve=req.minimum_reserve,
    )

    runway_days = compute_runway_days(daily_schedule, req.minimum_reserve)
    shortfall_prob = mc["shortfall_probability"]
    weather = classify_weather(shortfall_prob, runway_days)

    # Earliest shortfall date
    earliest_shortfall_date = None
    for day in daily_schedule:
        if day["closing_balance"] < req.minimum_reserve:
            earliest_shortfall_date = day["date"]
            break

    total_inflow = sum(inf["amount"] for inf in expected_inflows)
    total_outflow = sum(out["amount"] for out in expected_outflows)

    run_id = f"FCAST-{uuid.uuid4().hex[:12].upper()}"
    run_doc = {
        "run_id": run_id,
        "business_id": business_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "forecast_days": req.forecast_days,
        "current_cash": round(current_cash, 2),
        "minimum_reserve": req.minimum_reserve,
        "runway_days": runway_days,
        "weather": weather,
        "shortfall_probability": shortfall_prob,
        "earliest_shortfall_date": earliest_shortfall_date,
        "total_expected_inflow": round(total_inflow, 2),
        "total_expected_outflow": round(total_outflow, 2),
        "daily_schedule": daily_schedule,
        "monte_carlo": mc,
        "expected_inflows": expected_inflows,
        "expected_outflows": expected_outflows,
        "model": "deterministic_baseline_with_monte_carlo",
        "is_demo": biz.get("is_demo", False),
    }

    # Upsert latest forecast
    db.forecast_runs.update_one(
        {"business_id": business_id, "run_id": run_id},
        {"$set": run_doc},
        upsert=True,
    )

    return run_doc
