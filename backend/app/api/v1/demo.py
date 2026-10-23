"""Demo management endpoints — seed, reset, run analysis."""
import sys
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.core.database import get_db, init_indexes

router = APIRouter()


@router.post("/{business_id}/demo/reset")
async def reset_demo(business_id: str):
    """Restore the demo dataset to its known starting state."""
    if business_id != "demo_ramesh_textiles":
        raise HTTPException(400, "Reset is only available for the demo business.")

    db = get_db()

    # Clear all demo data
    collections_to_clear = [
        "businesses", "customers", "suppliers", "obligations",
        "invoices", "bank_transactions", "gst_summaries", "payment_histories",
        "payment_predictions", "reconciliation_findings", "reconciliation_runs",
        "forecast_runs", "risk_assessments", "rescue_simulations",
        "committee_sessions", "alerts", "health_passports",
        "passport_access_logs",
    ]
    for coll in collections_to_clear:
        db[coll].delete_many({"business_id": business_id})

    # Re-seed
    await _seed_demo(db, business_id)

    return {
        "status": "reset_complete",
        "business_id": business_id,
        "reset_at": datetime.now(timezone.utc).isoformat(),
        "message": "Demo dataset has been restored to its known starting state.",
    }


@router.post("/{business_id}/demo/seed")
async def seed_demo(business_id: str):
    """Seed the demo dataset if not already present."""
    if business_id != "demo_ramesh_textiles":
        raise HTTPException(400, "Seed is only available for the demo business.")

    db = get_db()
    existing = db.businesses.find_one({"business_id": business_id})
    if existing:
        return {"status": "already_seeded", "message": "Demo data already exists. Use /demo/reset to restore."}

    await _seed_demo(db, business_id)
    return {"status": "seeded", "business_id": business_id, "seeded_at": datetime.now(timezone.utc).isoformat()}


@router.post("/{business_id}/demo/run-analysis")
async def run_full_analysis(business_id: str):
    """Run all analysis modules: forecast, reconciliation, risk, alerts."""
    from app.api.v1.forecast import run_forecast, ForecastRunRequest
    from app.api.v1.reconciliation import run_reconciliation
    from app.api.v1.risk import run_risk_assessment
    from app.api.v1.alerts import generate_alerts

    results = {}

    try:
        forecast = await run_forecast(business_id, ForecastRunRequest())
        results["forecast"] = {"status": "ok", "run_id": forecast.get("run_id"), "weather": forecast.get("weather")}
    except Exception as e:
        results["forecast"] = {"status": "error", "error": str(e)}

    try:
        recon = await run_reconciliation(business_id)
        results["reconciliation"] = {"status": "ok", "total_findings": recon.get("total_findings")}
    except Exception as e:
        results["reconciliation"] = {"status": "error", "error": str(e)}

    try:
        db = get_db()
        risk = await run_risk_assessment(business_id)
        results["risk"] = {"status": "ok", "score": risk.get("score"), "band": risk.get("band")}
    except Exception as e:
        results["risk"] = {"status": "error", "error": str(e)}

    try:
        alert_result = await generate_alerts(business_id)
        results["alerts"] = {"status": "ok", "generated": alert_result.get("alerts_generated")}
    except Exception as e:
        results["alerts"] = {"status": "error", "error": str(e)}

    return {
        "status": "complete",
        "business_id": business_id,
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }


async def _seed_demo(db, business_id: str):
    """Insert the synthetic demo dataset into MongoDB."""
    # Add scripts directory to path
    scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    try:
        from generate_demo_data import generate_dataset, CUSTOMERS, SUPPLIERS, OBLIGATIONS, BUSINESS_ID
    except ImportError:
        # Fallback: try direct path
        import importlib.util
        script_file = os.path.join(scripts_dir, "generate_demo_data.py")
        spec = importlib.util.spec_from_file_location("generate_demo_data", script_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        generate_dataset = mod.generate_dataset


    data = generate_dataset()

    # Insert business
    db.businesses.update_one(
        {"business_id": business_id},
        {"$set": data["business"]},
        upsert=True,
    )

    # Insert customers
    for cust in data["customers"]:
        db.customers.update_one(
            {"business_id": business_id, "customer_id": cust["customer_id"]},
            {"$set": {**cust, "business_id": business_id}},
            upsert=True,
        )

    # Insert suppliers
    for supp in data["suppliers"]:
        db.suppliers.update_one(
            {"business_id": business_id, "supplier_id": supp["supplier_id"]},
            {"$set": {**supp, "business_id": business_id}},
            upsert=True,
        )

    # Insert obligations
    for obl in data["obligations"]:
        db.obligations.update_one(
            {"business_id": business_id, "obligation_id": obl["obligation_id"]},
            {"$set": {**obl, "business_id": business_id}},
            upsert=True,
        )

    # Insert invoices (bulk)
    if data["invoices"]:
        for inv in data["invoices"]:
            db.invoices.update_one(
                {"business_id": business_id, "invoice_id": inv["invoice_id"]},
                {"$set": inv},
                upsert=True,
            )

    # Insert bank transactions
    if data["bank_transactions"]:
        for txn in data["bank_transactions"]:
            db.bank_transactions.update_one(
                {"business_id": business_id, "txn_id": txn["txn_id"]},
                {"$set": txn},
                upsert=True,
            )

    # Insert GST summaries
    for gst in data["gst_summaries"]:
        db.gst_summaries.update_one(
            {"business_id": business_id, "period_key": gst["period_key"]},
            {"$set": gst},
            upsert=True,
        )

    # Insert payment histories
    for ph in data["payment_histories"]:
        db.payment_histories.update_one(
            {"business_id": business_id, "invoice_id": ph["invoice_id"]},
            {"$set": ph},
            upsert=True,
        )

    # Insert payment predictions
    for pred in data["payment_predictions"]:
        db.payment_predictions.update_one(
            {"business_id": business_id, "invoice_id": pred["invoice_id"]},
            {"$set": pred},
            upsert=True,
        )

    # Store ground truth labels
    for label in data["ground_truth_labels"]:
        db.ground_truth_labels.update_one(
            {"label_id": label["label_id"]},
            {"$set": {**label, "business_id": business_id}},
            upsert=True,
        )

    init_indexes()
