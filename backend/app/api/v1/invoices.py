"""Invoice endpoints."""
from fastapi import APIRouter, HTTPException, Query
from app.core.database import get_db

router = APIRouter()


@router.get("/{business_id}/invoices")
async def list_invoices(
    business_id: str,
    status: str = Query(None),
    customer_id: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
):
    db = get_db()
    query = {"business_id": business_id}
    if status:
        query["status"] = status.upper()
    if customer_id:
        query["customer_id"] = customer_id

    skip = (page - 1) * limit
    invoices = list(db.invoices.find(query, {"_id": 0}).sort("invoice_date", -1).skip(skip).limit(limit))
    total = db.invoices.count_documents(query)

    return {
        "invoices": invoices,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{business_id}/invoices/{invoice_id}")
async def get_invoice(business_id: str, invoice_id: str):
    db = get_db()
    inv = db.invoices.find_one(
        {"business_id": business_id, "invoice_id": invoice_id}, {"_id": 0}
    )
    if not inv:
        raise HTTPException(404, f"Invoice {invoice_id} not found")

    # Attach payment prediction if available
    pred = db.payment_predictions.find_one(
        {"business_id": business_id, "invoice_id": invoice_id}, {"_id": 0}
    )
    inv["payment_prediction"] = pred

    # Attach any reconciliation findings
    findings = list(db.reconciliation_findings.find(
        {"business_id": business_id, "invoice_id": invoice_id}, {"_id": 0}
    ))
    inv["reconciliation_findings"] = findings

    return inv
