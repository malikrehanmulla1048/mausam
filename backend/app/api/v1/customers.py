"""Customer and Debtor DNA endpoints."""
from fastapi import APIRouter, HTTPException, Query
from app.core.database import get_db
from app.services.analytics import compute_customer_stats, compute_reliability_grade, predict_payment_date
from datetime import date

router = APIRouter()


@router.get("/{business_id}/customers")
async def list_customers(
    business_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_db()
    skip = (page - 1) * limit
    customers = list(db.customers.find(
        {"business_id": business_id}, {"_id": 0}
    ).skip(skip).limit(limit))
    total = db.customers.count_documents({"business_id": business_id})

    # Enrich with payment stats
    for cust in customers:
        cid = cust["customer_id"]
        histories = list(db.payment_histories.find(
            {"business_id": business_id, "customer_id": cid}, {"_id": 0}
        ).limit(100))
        stats = compute_customer_stats(histories)
        cust["payment_stats"] = stats
        cust["reliability_grade"] = compute_reliability_grade(
            stats.get("avg_delay", 0), stats.get("late_rate", 0)
        )
        cust["payment_history_count"] = stats.get("count", 0)

        outstanding = list(db.invoices.find(
            {"business_id": business_id, "customer_id": cid, "status": "OUTSTANDING"},
            {"_id": 0, "total_amount": 1, "due_date": 1}
        ))
        cust["outstanding_amount"] = round(sum(i.get("total_amount", 0) for i in outstanding), 2)
        cust["outstanding_count"] = len(outstanding)
        today_str = date.today().isoformat()
        cust["overdue_amount"] = round(sum(
            i.get("total_amount", 0) for i in outstanding
            if i.get("due_date", "") < today_str
        ), 2)

    return {
        "customers": customers,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{business_id}/customers/{customer_id}")
async def get_customer(business_id: str, customer_id: str):
    db = get_db()
    cust = db.customers.find_one(
        {"business_id": business_id, "customer_id": customer_id}, {"_id": 0}
    )
    if not cust:
        raise HTTPException(404, f"Customer {customer_id} not found")

    histories = list(db.payment_histories.find(
        {"business_id": business_id, "customer_id": customer_id}, {"_id": 0}
    ).sort("payment_date", -1).limit(200))
    stats = compute_customer_stats(histories)
    grade = compute_reliability_grade(stats.get("avg_delay", 0), stats.get("late_rate", 0))

    invoices = list(db.invoices.find(
        {"business_id": business_id, "customer_id": customer_id}, {"_id": 0}
    ).sort("invoice_date", -1).limit(50))

    outstanding_invoices = [i for i in invoices if i["status"] == "OUTSTANDING"]
    predictions = []
    for inv in outstanding_invoices:
        pred = predict_payment_date(
            invoice_date=date.fromisoformat(inv["invoice_date"]),
            payment_terms_days=inv.get("payment_terms_days", 30),
            customer_avg_delay=stats.get("avg_delay", 0),
            customer_std_delay=stats.get("std_delay", 5),
        )
        predictions.append({
            "invoice_id": inv["invoice_id"],
            "invoice_date": inv["invoice_date"],
            "due_date": inv["due_date"],
            "amount": inv["total_amount"],
            **pred,
        })

    # Monthly delay trend (for drift detection)
    monthly_delays = {}
    for h in histories:
        month = h.get("payment_date", "")[:7]
        if month:
            monthly_delays.setdefault(month, []).append(h.get("delay_days", 0))
    delay_trend = [
        {"month": m, "avg_delay": round(sum(ds) / len(ds), 1), "count": len(ds)}
        for m, ds in sorted(monthly_delays.items())
    ]

    return {
        **cust,
        "payment_stats": stats,
        "reliability_grade": grade,
        "recent_histories": histories[:12],
        "invoices": invoices[:20],
        "outstanding_predictions": predictions,
        "delay_trend": delay_trend,
        "outstanding_amount": round(sum(i.get("total_amount", 0) for i in outstanding_invoices), 2),
        "total_invoices": len(invoices),
    }


from pydantic import BaseModel
from typing import Optional
from app.services.sms import dispatch_sms, generate_sms_text


class CustomerSMSRequest(BaseModel):
    phone: str
    message: Optional[str] = None
    tone: str = "firm"
    language: str = "en"
    amount_str: Optional[str] = None
    days_overdue: int = 15


@router.post("/{business_id}/customers/{customer_id}/send-sms")
async def send_customer_sms(business_id: str, customer_id: str, req: CustomerSMSRequest):
    """Dispatch an SMS payment reminder to a customer via SMS Gateway/SNS."""
    db = get_db()
    cust = db.customers.find_one({"business_id": business_id, "customer_id": customer_id})
    cust_name = cust.get("name", customer_id) if cust else customer_id

    msg = req.message
    if not msg:
        msg = generate_sms_text(
            customer_name=cust_name,
            overdue_amount_formatted=req.amount_str or "₹1,50,000",
            days_overdue=req.days_overdue,
            tone=req.tone,
            language=req.language,
        )

    result = await dispatch_sms(
        business_id=business_id,
        recipient_phone=req.phone,
        message=msg,
        customer_id=customer_id,
        customer_name=cust_name,
        tone=req.tone,
        language=req.language,
    )
    return result
