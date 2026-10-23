"""Bank's-Eye X-Ray — Risk assessment endpoints."""
import uuid
from datetime import datetime, date, timezone
from fastapi import APIRouter, HTTPException
from app.core.database import get_db
from app.services.analytics import compute_readiness_score, compute_dscr

router = APIRouter()


@router.get("/{business_id}/risk-assessment")
async def get_risk_assessment(business_id: str):
    db = get_db()
    assessment = db.risk_assessments.find_one(
        {"business_id": business_id}, {"_id": 0}, sort=[("created_at", -1)]
    )
    if not assessment:
        # Auto-compute
        return await _compute_and_store_risk(business_id, db)
    return assessment


@router.post("/{business_id}/risk-assessment/run")
async def run_risk_assessment(business_id: str):
    db = get_db()
    return await _compute_and_store_risk(business_id, db)


async def _compute_and_store_risk(business_id: str, db):
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    invoices = list(db.invoices.find({"business_id": business_id}, {"_id": 0}))
    bank_txns = list(db.bank_transactions.find({"business_id": business_id}, {"_id": 0}))
    customers = list(db.customers.find({"business_id": business_id}, {"_id": 0}))
    findings = list(db.reconciliation_findings.find(
        {"business_id": business_id, "status": {"$in": ["OPEN", "REVIEWING"]}}, {"_id": 0}
    ))

    today = date.today().isoformat()
    paid_invoices = [i for i in invoices if i.get("status") == "PAID"]
    outstanding = [i for i in invoices if i.get("status") == "OUTSTANDING"]
    overdue = [i for i in outstanding if i.get("due_date", "") < today]
    total_outstanding = sum(i.get("total_amount", 0) for i in outstanding)
    overdue_amount = sum(i.get("total_amount", 0) for i in overdue)

    # Cash flow stability: based on variance of monthly income
    monthly_income: dict[str, float] = {}
    for i in paid_invoices:
        month = i.get("actual_payment_date", i.get("invoice_date", ""))[:7]
        if month:
            monthly_income[month] = monthly_income.get(month, 0) + i.get("total_amount", 0)
    incomes = list(monthly_income.values())
    if len(incomes) >= 3:
        avg_income = sum(incomes) / len(incomes)
        variance = sum((x - avg_income) ** 2 for x in incomes) / len(incomes)
        import math
        cv = math.sqrt(variance) / avg_income if avg_income > 0 else 1.0
        cash_flow_stability = max(0, min(100, 100 - cv * 100))
    else:
        cash_flow_stability = 50.0

    # Customer concentration
    customer_totals: dict[str, float] = {}
    for i in paid_invoices:
        cid = i.get("customer_id", "")
        customer_totals[cid] = customer_totals.get(cid, 0) + i.get("total_amount", 0)
    if customer_totals:
        total_sales = sum(customer_totals.values())
        top_pct = max(customer_totals.values()) / total_sales * 100 if total_sales > 0 else 0
        customer_concentration = max(0, min(100, 100 - max(0, top_pct - 20) * 2))
        top_customer_pct = round(top_pct, 1)
    else:
        customer_concentration = 50.0
        top_customer_pct = 0.0

    # Debt service capacity (DSCR approximation)
    obligations = list(db.obligations.find({"business_id": business_id}, {"_id": 0}))
    monthly_emi = sum(
        o.get("amount", 0) for o in obligations if o.get("type") == "emi"
    )
    avg_monthly_income = sum(incomes) / len(incomes) if incomes else 0
    avg_monthly_expenses = sum(
        o.get("amount", 0) for o in obligations if o.get("type") not in ["emi"]
    )
    net_operating = avg_monthly_income - avg_monthly_expenses
    dscr_data = compute_dscr(net_operating, monthly_emi * 12) if monthly_emi > 0 else None

    if dscr_data:
        dscr_val = dscr_data["dscr"]
        debt_service_capacity = max(0, min(100, (dscr_val / 2.5) * 100))
    else:
        debt_service_capacity = 60.0

    # Receivables quality
    if total_outstanding > 0:
        overdue_pct = overdue_amount / total_outstanding
        receivables_quality = max(0, min(100, 100 - overdue_pct * 100))
    else:
        receivables_quality = 80.0

    # Reconciliation health
    high_findings = len([f for f in findings if f.get("severity") == "HIGH"])
    medium_findings = len([f for f in findings if f.get("severity") == "MEDIUM"])
    finding_penalty = high_findings * 15 + medium_findings * 7
    reconciliation_health = max(0, min(100, 100 - finding_penalty))

    # Transaction behaviour
    bounce_txns = [t for t in bank_txns if "bounce" in t.get("description", "").lower() or "return" in t.get("description", "").lower()]
    circular_findings = [f for f in findings if f.get("finding_type") == "POTENTIAL_CIRCULAR_TRANSACTION"]
    txn_penalty = len(bounce_txns) * 20 + len(circular_findings) * 15
    transaction_behaviour = max(0, min(100, 100 - txn_penalty))

    score_result = compute_readiness_score(
        cash_flow_stability=cash_flow_stability,
        customer_concentration=customer_concentration,
        debt_service_capacity=debt_service_capacity,
        receivables_quality=receivables_quality,
        reconciliation_health=reconciliation_health,
        transaction_behaviour=transaction_behaviour,
    )

    # Risk flags
    risk_flags = []
    if high_findings > 0:
        risk_flags.append({
            "flag_id": "FLAG-RECON",
            "label": "Unresolved Reconciliation Findings",
            "severity": "HIGH",
            "detail": f"{high_findings} HIGH-severity findings require resolution.",
        })
    if top_customer_pct > 35:
        risk_flags.append({
            "flag_id": "FLAG-CONC",
            "label": "Customer Concentration",
            "severity": "MEDIUM",
            "detail": f"Top customer accounts for {top_customer_pct:.1f}% of revenue.",
        })
    if len(bounce_txns) > 0:
        risk_flags.append({
            "flag_id": "FLAG-BOUNCE",
            "label": "EMI/Cheque Bounce",
            "severity": "HIGH",
            "detail": f"{len(bounce_txns)} bounce/returned transaction(s) on record.",
        })
    if circular_findings:
        risk_flags.append({
            "flag_id": "FLAG-CIRC",
            "label": "Potential Circular Transactions",
            "severity": "HIGH",
            "detail": f"{len(circular_findings)} potential circular transaction pattern(s) detected.",
        })

    # Sharma Traders specific delay
    sharma_histories = list(db.payment_histories.find(
        {"business_id": business_id, "customer_id": "CUST-001"}, {"_id": 0}
    ).sort("payment_date", -1).limit(6))
    sharma_recent_delays = [h.get("delay_days", 0) for h in sharma_histories]
    sharma_avg_delay = round(sum(sharma_recent_delays) / len(sharma_recent_delays), 1) if sharma_recent_delays else 30

    assessment_id = f"RISK-{uuid.uuid4().hex[:10].upper()}"
    assessment = {
        "assessment_id": assessment_id,
        "business_id": business_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **score_result,
        "dscr": dscr_data,
        "top_customer_pct": top_customer_pct,
        "overdue_amount": round(overdue_amount, 2),
        "overdue_count": len(overdue),
        "total_outstanding": round(total_outstanding, 2),
        "open_high_findings": high_findings,
        "bounce_count": len(bounce_txns),
        "sharma_avg_delay": sharma_avg_delay,
        "reconciliation_health": reconciliation_health,
        "risk_flags": risk_flags,
        "improvement_actions": [
            {"action": "Resolve HIGH-severity reconciliation findings", "score_impact": "+30–50 pts"},
            {"action": "Collect overdue receivables promptly", "score_impact": "+15–25 pts"},
            {"action": "Diversify customer base beyond top customer", "score_impact": "+10–20 pts"},
            {"action": "Maintain EMI payment record for 6+ months", "score_impact": "+20–30 pts"},
        ],
        "is_demo": biz.get("is_demo", False),
    }

    db.risk_assessments.update_one(
        {"assessment_id": assessment_id},
        {"$set": assessment},
        upsert=True,
    )

    return assessment
