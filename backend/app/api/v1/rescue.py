"""Rescue Planner endpoints."""
import uuid
from datetime import datetime, date, timedelta, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from app.core.database import get_db
from app.services.analytics import evaluate_rescue_intervention, compute_loan_emi

router = APIRouter()


class InterventionRequest(BaseModel):
    intervention_type: str
    params: dict = {}


class SimulationRequest(BaseModel):
    interventions: List[InterventionRequest]
    simulation_name: Optional[str] = None
    forecast_days: int = 42
    minimum_reserve: float = 100_000


class LoanSimulatorRequest(BaseModel):
    principal: float
    annual_rate_pct: float = 12.0
    tenure_months: int = 12


@router.post("/{business_id}/rescue-simulations")
async def run_rescue_simulation(business_id: str, req: SimulationRequest):
    db = get_db()
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    # Get latest forecast schedule
    forecast_run = db.forecast_runs.find_one(
        {"business_id": business_id}, sort=[("created_at", -1)]
    )
    if not forecast_run:
        raise HTTPException(400, "Run a cash forecast first before simulating interventions.")

    daily_schedule = forecast_run.get("daily_schedule", [])
    current_cash = forecast_run.get("current_cash", 480_000)

    results = []
    for intervention in req.interventions:
        result = evaluate_rescue_intervention(
            intervention_type=intervention.intervention_type,
            params=intervention.params,
            current_cash=current_cash,
            daily_schedule=daily_schedule,
            minimum_reserve=req.minimum_reserve,
        )
        results.append(result)

    # Rank by runway improvement
    results_sorted = sorted(results, key=lambda r: r.get("runway_improvement_days", 0), reverse=True)

    sim_id = f"SIM-{uuid.uuid4().hex[:10].upper()}"
    sim_doc = {
        "sim_id": sim_id,
        "business_id": business_id,
        "simulation_name": req.simulation_name or f"Simulation {sim_id}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "baseline_runway": results[0].get("original_runway_days") if results else 0,
        "interventions": results_sorted,
        "combined_impact": _compute_combined_impact(results_sorted, current_cash, daily_schedule, req.minimum_reserve),
        "forecast_days": req.forecast_days,
        "is_demo": biz.get("is_demo", False),
    }

    db.rescue_simulations.update_one(
        {"sim_id": sim_id},
        {"$set": sim_doc},
        upsert=True,
    )

    return sim_doc


def _compute_combined_impact(results, current_cash, daily_schedule, minimum_reserve):
    if not results:
        return {}
    total_cash_impact = sum(r.get("impact_cash", 0) for r in results)
    total_cost = sum(r.get("cost", 0) for r in results)

    from app.services.analytics import compute_runway_days
    new_current = current_cash + total_cash_impact
    new_schedule = []
    running = new_current
    for day in daily_schedule:
        running = running + day["inflow"] - day["outflow"]
        new_schedule.append({**day, "closing_balance": round(running, 2)})

    new_runway = compute_runway_days(new_schedule, minimum_reserve)
    original_runway = compute_runway_days(daily_schedule, minimum_reserve)

    return {
        "total_cash_impact": round(total_cash_impact, 2),
        "total_cost": round(total_cost, 2),
        "net_benefit": round(total_cash_impact - total_cost, 2),
        "original_runway": original_runway,
        "combined_runway": new_runway,
        "runway_improvement": new_runway - original_runway,
        "disclaimer": "Combined simulation assumes all interventions are fully executed. Actual outcomes depend on counterparty agreement and operational feasibility.",
    }


@router.post("/{business_id}/rescue-simulations/loan")
async def loan_simulator(business_id: str, req: LoanSimulatorRequest):
    db = get_db()
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    if req.principal <= 0 or req.annual_rate_pct <= 0 or req.tenure_months <= 0:
        raise HTTPException(400, "Invalid loan parameters")

    emi_data = compute_loan_emi(req.principal, req.annual_rate_pct, req.tenure_months)

    # Debt service impact
    forecast_run = db.forecast_runs.find_one(
        {"business_id": business_id}, sort=[("created_at", -1)]
    )
    current_cash = forecast_run.get("current_cash", 480_000) if forecast_run else 480_000
    cash_after_disbursement = current_cash + req.principal

    risk_assessment = db.risk_assessments.find_one(
        {"business_id": business_id}, sort=[("created_at", -1)]
    )
    existing_emi = 0
    if risk_assessment:
        obligations = list(db.obligations.find({"business_id": business_id}, {"_id": 0}))
        existing_emi = sum(o.get("amount", 0) for o in obligations if o.get("type") == "emi")

    total_monthly_emi = existing_emi + emi_data["monthly_emi"]

    return {
        **emi_data,
        "current_cash": round(current_cash, 2),
        "cash_after_disbursement": round(cash_after_disbursement, 2),
        "existing_monthly_emi": round(existing_emi, 2),
        "total_monthly_emi_after": round(total_monthly_emi, 2),
        "affordability_note": (
            "Monthly EMI appears manageable given projected income"
            if total_monthly_emi < 1_00_000
            else "Total monthly EMI is elevated — review cash flow impact carefully"
        ),
        "disclaimer": (
            "This is an illustrative repayment model. "
            "Actual loan rates, processing fees, and terms depend on the lender. "
            "Never borrow more than your projected cash flow can service comfortably."
        ),
    }
