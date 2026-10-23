"""Truth Check — Reconciliation endpoints."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.services.analytics import (
    find_paid_no_credit, find_duplicate_invoices,
    detect_gst_bank_discrepancy, detect_circular_transactions,
    detect_cash_deposit_spikes,
)

router = APIRouter()


class FindingUpdateRequest(BaseModel):
    status: str  # OPEN, REVIEWING, RESOLVED, DISMISSED
    resolution_note: Optional[str] = None


@router.post("/{business_id}/reconciliation/run")
async def run_reconciliation(business_id: str):
    db = get_db()
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    run_id = f"RECON-{uuid.uuid4().hex[:10].upper()}"

    # Fetch data
    invoices = list(db.invoices.find({"business_id": business_id}, {"_id": 0}))
    bank_txns = list(db.bank_transactions.find({"business_id": business_id}, {"_id": 0}))
    gst_summaries = list(db.gst_summaries.find({"business_id": business_id}, {"_id": 0}))

    bank_credits = [t for t in bank_txns if t["type"] == "CREDIT"]

    # Monthly bank credits aggregation
    monthly_bank_credits: dict[str, float] = {}
    for txn in bank_credits:
        period = txn["date"][:7]
        monthly_bank_credits[period] = monthly_bank_credits.get(period, 0) + txn.get("amount", 0)

    # Run all detectors
    all_findings = []

    paid_no_credit = find_paid_no_credit(invoices, bank_credits)
    for f in paid_no_credit:
        f["finding_id"] = f"RECON-{uuid.uuid4().hex[:8].upper()}"
        f["run_id"] = run_id
        f["business_id"] = business_id
        f["status"] = "OPEN"
        f["created_at"] = datetime.now(timezone.utc).isoformat()
        f["invoice_id"] = f.get("invoice_id")
        all_findings.append(f)

    duplicate_invoices = find_duplicate_invoices(invoices)
    for f in duplicate_invoices:
        f["finding_id"] = f"RECON-{uuid.uuid4().hex[:8].upper()}"
        f["run_id"] = run_id
        f["business_id"] = business_id
        f["status"] = "OPEN"
        f["created_at"] = datetime.now(timezone.utc).isoformat()
        f["invoice_id"] = f.get("invoice_id")
        all_findings.append(f)

    gst_discrepancies = detect_gst_bank_discrepancy(gst_summaries, monthly_bank_credits)
    for f in gst_discrepancies:
        f["finding_id"] = f"RECON-{uuid.uuid4().hex[:8].upper()}"
        f["run_id"] = run_id
        f["business_id"] = business_id
        f["status"] = "OPEN"
        f["created_at"] = datetime.now(timezone.utc).isoformat()
        f["invoice_id"] = None
        all_findings.append(f)

    circular_txns = detect_circular_transactions(bank_txns)
    for f in circular_txns:
        f["finding_id"] = f"RECON-{uuid.uuid4().hex[:8].upper()}"
        f["run_id"] = run_id
        f["business_id"] = business_id
        f["status"] = "OPEN"
        f["created_at"] = datetime.now(timezone.utc).isoformat()
        f["invoice_id"] = None
        all_findings.append(f)

    cash_spikes = detect_cash_deposit_spikes(bank_txns)
    for f in cash_spikes:
        f["finding_id"] = f"RECON-{uuid.uuid4().hex[:8].upper()}"
        f["run_id"] = run_id
        f["business_id"] = business_id
        f["status"] = "OPEN"
        f["created_at"] = datetime.now(timezone.utc).isoformat()
        f["invoice_id"] = None
        all_findings.append(f)

    # Persist findings
    if all_findings:
        db.reconciliation_findings.insert_many(
            [{**f} for f in all_findings]
        )

    severity_counts = {}
    for f in all_findings:
        sev = f.get("severity", "UNKNOWN")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    run_doc = {
        "run_id": run_id,
        "business_id": business_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_findings": len(all_findings),
        "severity_counts": severity_counts,
        "invoices_checked": len(invoices),
        "transactions_checked": len(bank_txns),
        "gst_periods_checked": len(gst_summaries),
        "detectors_run": [
            "paid_no_credit", "duplicate_invoices",
            "gst_bank_discrepancy", "circular_transactions",
            "cash_deposit_spikes",
        ],
        "is_demo": biz.get("is_demo", False),
    }
    db.reconciliation_runs.insert_one({"_id": run_id, **run_doc})

    return {**run_doc, "findings": all_findings}


@router.get("/{business_id}/findings")
async def list_findings(
    business_id: str,
    status: str = Query(None),
    severity: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_db()
    query = {"business_id": business_id}
    if status:
        query["status"] = status.upper()
    if severity:
        query["severity"] = severity.upper()

    skip = (page - 1) * limit
    findings = list(db.reconciliation_findings.find(
        query, {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit))
    total = db.reconciliation_findings.count_documents(query)

    return {
        "findings": findings,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.patch("/{business_id}/findings/{finding_id}")
async def update_finding(business_id: str, finding_id: str, req: FindingUpdateRequest):
    db = get_db()
    valid_statuses = {"OPEN", "REVIEWING", "RESOLVED", "DISMISSED"}
    if req.status.upper() not in valid_statuses:
        raise HTTPException(400, f"Invalid status. Must be one of {valid_statuses}")

    result = db.reconciliation_findings.update_one(
        {"business_id": business_id, "finding_id": finding_id},
        {"$set": {
            "status": req.status.upper(),
            "resolution_note": req.resolution_note,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(404, f"Finding {finding_id} not found")

    finding = db.reconciliation_findings.find_one(
        {"business_id": business_id, "finding_id": finding_id}, {"_id": 0}
    )
    return finding
