"""
MAUSAM — Financial Analytics Engine
All financial calculations are deterministic Python functions.
The AI may explain results but never manufactures these values.
"""
import math
import random
from datetime import date, timedelta
from typing import Any


# ─── CASH FLOW FORECAST ───────────────────────────────────────────────────────

WEATHER_THRESHOLDS = {
    "sunny":  {"shortfall_prob_max": 0.10, "runway_min": 30},
    "cloudy": {"shortfall_prob_max": 0.30, "runway_min": 20},
    "rain":   {"shortfall_prob_max": 0.55, "runway_min": 12},
    "storm":  {"shortfall_prob_max": 1.00, "runway_min": 0},
}


def classify_weather(shortfall_probability: float, runway_days: int) -> str:
    if shortfall_probability <= 0.10 and runway_days >= 30:
        return "sunny"
    elif shortfall_probability <= 0.30 and runway_days >= 20:
        return "cloudy"
    elif shortfall_probability <= 0.55 and runway_days >= 12:
        return "rain"
    else:
        return "storm"


def classify_daily_weather(projected_balance: float, minimum_reserve: float) -> str:
    if projected_balance < 0:
        return "storm"
    ratio = projected_balance / max(minimum_reserve, 1)
    if ratio >= 2.0:
        return "sunny"
    elif ratio >= 1.2:
        return "cloudy"
    elif ratio >= 0.5:
        return "rain"
    else:
        return "storm"


def build_daily_cash_schedule(
    current_cash: float,
    forecast_days: int,
    expected_inflows: list[dict],   # [{date, amount, source, customer_id}]
    expected_outflows: list[dict],  # [{date, amount, category, description}]
    minimum_reserve: float = 1_00_000,
) -> list[dict]:
    """
    Build a day-by-day cash balance schedule.
    Returns list of daily records with running balance.
    """
    today = date.today()
    schedule = []
    running = current_cash

    # Index by date
    inflow_by_date: dict[str, float] = {}
    outflow_by_date: dict[str, float] = {}

    for inf in expected_inflows:
        d = inf["date"] if isinstance(inf["date"], str) else inf["date"].isoformat()
        inflow_by_date[d] = inflow_by_date.get(d, 0) + inf["amount"]

    for out in expected_outflows:
        d = out["date"] if isinstance(out["date"], str) else out["date"].isoformat()
        outflow_by_date[d] = outflow_by_date.get(d, 0) + out["amount"]

    for i in range(forecast_days):
        day = today + timedelta(days=i)
        day_str = day.isoformat()
        day_inflow = inflow_by_date.get(day_str, 0.0)
        day_outflow = outflow_by_date.get(day_str, 0.0)
        running = running + day_inflow - day_outflow
        weather = classify_daily_weather(running, minimum_reserve)
        schedule.append({
            "date": day_str,
            "day_number": i + 1,
            "inflow": round(day_inflow, 2),
            "outflow": round(day_outflow, 2),
            "net": round(day_inflow - day_outflow, 2),
            "closing_balance": round(running, 2),
            "weather": weather,
            "below_reserve": running < minimum_reserve,
        })

    return schedule


def compute_runway_days(daily_schedule: list[dict], minimum_reserve: float = 0) -> int:
    """Returns how many days until balance drops below minimum_reserve."""
    for record in daily_schedule:
        if record["closing_balance"] < minimum_reserve:
            return record["day_number"] - 1
    return len(daily_schedule)


def monte_carlo_forecast(
    current_cash: float,
    base_daily_schedule: list[dict],
    n_simulations: int = 500,
    inflow_std_pct: float = 0.15,
    outflow_std_pct: float = 0.08,
    seed: int = 42,
    minimum_reserve: float = 1_00_000,
) -> dict:
    """
    Run Monte Carlo simulations over the base daily cash flow schedule.
    Returns P10, P50, P90 bands and shortfall probability.
    """
    rng = random.Random(seed)
    n_days = len(base_daily_schedule)
    all_balances = []  # shape: n_simulations × n_days
    shortfall_count = 0

    for _ in range(n_simulations):
        running = current_cash
        sim_balances = []
        hit_shortfall = False

        for day in base_daily_schedule:
            inflow_factor = max(0.0, 1 + rng.gauss(0, inflow_std_pct))
            outflow_factor = max(0.5, 1 + rng.gauss(0, outflow_std_pct))
            sim_inflow = day["inflow"] * inflow_factor
            sim_outflow = day["outflow"] * outflow_factor
            running = running + sim_inflow - sim_outflow
            sim_balances.append(round(running, 2))
            if running < minimum_reserve:
                hit_shortfall = True

        all_balances.append(sim_balances)
        if hit_shortfall:
            shortfall_count += 1

    shortfall_probability = shortfall_count / n_simulations

    # Compute percentile bands day by day
    p10_band = []
    p50_band = []
    p90_band = []

    for day_idx in range(n_days):
        day_vals = sorted(sim[day_idx] for sim in all_balances)
        p10_band.append(round(day_vals[int(0.10 * n_simulations)], 2))
        p50_band.append(round(day_vals[int(0.50 * n_simulations)], 2))
        p90_band.append(round(day_vals[int(0.90 * n_simulations)], 2))

    # Earliest shortfall date in median scenario
    earliest_shortfall_day = None
    for i, bal in enumerate(p50_band):
        if bal < minimum_reserve:
            earliest_shortfall_day = i + 1
            break

    return {
        "n_simulations": n_simulations,
        "shortfall_probability": round(shortfall_probability, 4),
        "p10_band": p10_band,
        "p50_band": p50_band,
        "p90_band": p90_band,
        "earliest_shortfall_day_p50": earliest_shortfall_day,
        "min_balance_p50": round(min(p50_band), 2) if p50_band else current_cash,
        "max_balance_p50": round(max(p50_band), 2) if p50_band else current_cash,
    }


# ─── DEBTOR DNA / PAYMENT PREDICTION ─────────────────────────────────────────

def compute_reliability_grade(avg_delay: float, late_rate: float) -> str:
    """A=best, E=worst."""
    score = avg_delay * 0.6 + late_rate * 30
    if score <= 8:   return "A"
    if score <= 18:  return "B"
    if score <= 30:  return "C"
    if score <= 45:  return "D"
    return "E"


def compute_customer_stats(payment_histories: list[dict]) -> dict:
    """Compute per-customer payment statistics from payment history records."""
    if not payment_histories:
        return {"avg_delay": 0, "std_delay": 0, "late_rate": 0, "count": 0}

    delays = [h["delay_days"] for h in payment_histories]
    n = len(delays)
    avg = sum(delays) / n
    variance = sum((d - avg) ** 2 for d in delays) / max(n - 1, 1)
    std = math.sqrt(variance)
    late_count = sum(1 for d in delays if d > 0)

    return {
        "avg_delay": round(avg, 1),
        "std_delay": round(std, 1),
        "late_rate": round(late_count / n, 3),
        "count": n,
    }


def predict_payment_date(
    invoice_date: date,
    payment_terms_days: int,
    customer_avg_delay: float,
    customer_std_delay: float,
) -> dict:
    """Predict when a payment will arrive based on historical behavior."""
    expected_delay = payment_terms_days + customer_avg_delay
    predicted_date = invoice_date + timedelta(days=int(expected_delay))
    due_date = invoice_date + timedelta(days=payment_terms_days)

    # Late probability: P(delay > 0 after due date)
    if customer_std_delay > 0:
        z = customer_avg_delay / customer_std_delay
        # Simplified normal CDF approximation
        late_prob = 1 - (1 / (1 + math.exp(-1.702 * z)))
    else:
        late_prob = 1.0 if customer_avg_delay > 0 else 0.0

    return {
        "predicted_payment_date": predicted_date.isoformat(),
        "due_date": due_date.isoformat(),
        "expected_delay_days": round(expected_delay, 1),
        "late_probability": round(min(0.97, max(0.03, late_prob)), 2),
        "earliest_date": (predicted_date - timedelta(days=int(customer_std_delay))).isoformat(),
        "latest_date": (predicted_date + timedelta(days=int(customer_std_delay * 1.5))).isoformat(),
    }


# ─── RECONCILIATION ──────────────────────────────────────────────────────────

def find_paid_no_credit(
    invoices: list[dict],
    bank_credits: list[dict],
    amount_tolerance: float = 0.01,
    date_window_days: int = 10,
) -> list[dict]:
    """
    Detect invoices marked PAID with no matching bank credit.
    Returns list of discrepancy findings.
    """
    findings = []
    for inv in invoices:
        if inv.get("status") != "PAID":
            continue
        if not inv.get("actual_payment_date"):
            continue

        inv_date = date.fromisoformat(inv["actual_payment_date"])
        inv_amount = inv["total_amount"]
        inv_id = inv["invoice_id"]
        cust_name = inv.get("customer_name", "")

        # Look for matching bank credit within window
        matched = False
        for credit in bank_credits:
            credit_date = date.fromisoformat(credit["date"])
            credit_amount = credit["amount"]
            date_diff = abs((credit_date - inv_date).days)

            if (
                date_diff <= date_window_days
                and abs(credit_amount - inv_amount) / max(inv_amount, 1) <= amount_tolerance
            ):
                matched = True
                break

        if not matched:
            findings.append({
                "finding_type": "PAID_NO_CREDIT",
                "severity": "HIGH",
                "invoice_id": inv_id,
                "customer_name": cust_name,
                "expected_date": inv["actual_payment_date"],
                "expected_amount": inv_amount,
                "observed": "No matching bank credit found",
                "difference": inv_amount,
                "explanation": (
                    f"Invoice {inv_id} is marked as PAID (₹{inv_amount:,.0f}) "
                    f"on {inv['actual_payment_date']}, but no corresponding bank "
                    f"credit was found within ±{date_window_days} days."
                ),
                "recommended_action": "Verify payment receipt with bank statement. Request bank remittance from customer.",
            })

    return findings


def find_duplicate_invoices(invoices: list[dict]) -> list[dict]:
    """Detect invoice numbers used more than once."""
    seen: dict[str, list] = {}
    for inv in invoices:
        inv_id = inv["invoice_id"]
        if inv_id not in seen:
            seen[inv_id] = []
        seen[inv_id].append(inv)

    findings = []
    for inv_id, dupes in seen.items():
        if len(dupes) > 1:
            amounts = [d["total_amount"] for d in dupes]
            findings.append({
                "finding_type": "DUPLICATE_INVOICE_NUMBER",
                "severity": "HIGH",
                "invoice_id": inv_id,
                "occurrences": len(dupes),
                "amounts": amounts,
                "explanation": (
                    f"Invoice number {inv_id} appears {len(dupes)} times "
                    f"with amounts ₹{', ₹'.join(f'{a:,.0f}' for a in amounts)}. "
                    f"Duplicate invoice numbers may indicate accidental re-issue or intentional manipulation."
                ),
                "recommended_action": "Audit invoice numbering sequence and verify with customer.",
            })

    return findings


def detect_gst_bank_discrepancy(
    gst_summaries: list[dict],
    monthly_bank_credits: dict[str, float],
    threshold_pct: float = 0.20,
) -> list[dict]:
    """Flag months where bank credits significantly exceed GST-reported turnover."""
    findings = []
    for gst in gst_summaries:
        period = gst["period_key"]
        gst_turnover = gst.get("taxable_turnover", 0)
        bank_credits = monthly_bank_credits.get(period, 0)

        if gst_turnover <= 0:
            continue

        excess_pct = (bank_credits - gst_turnover) / gst_turnover
        if excess_pct > threshold_pct:
            findings.append({
                "finding_type": "BANK_CREDIT_EXCEEDS_GST_TURNOVER",
                "severity": "MEDIUM" if excess_pct < 0.5 else "HIGH",
                "period": period,
                "gst_turnover": round(gst_turnover, 2),
                "bank_credits": round(bank_credits, 2),
                "excess_amount": round(bank_credits - gst_turnover, 2),
                "excess_pct": round(excess_pct * 100, 1),
                "explanation": (
                    f"In {period}, bank credits (₹{bank_credits:,.0f}) exceeded "
                    f"GST-reported turnover (₹{gst_turnover:,.0f}) by "
                    f"{excess_pct*100:.1f}% (₹{bank_credits-gst_turnover:,.0f}). "
                    f"This may indicate unreported sales, non-business receipts, or data errors."
                ),
                "recommended_action": "Cross-verify all credits against sales invoices. Consult GST advisor.",
            })

    return findings


def detect_circular_transactions(
    bank_transactions: list[dict],
    amount_tolerance: float = 0.01,
    max_days: int = 7,
) -> list[dict]:
    """Detect round-trip transactions: outflow returned within N days."""
    findings = []
    debits = [t for t in bank_transactions if t["type"] == "DEBIT"]
    credits = [t for t in bank_transactions if t["type"] == "CREDIT"]

    for debit in debits:
        d_date = date.fromisoformat(debit["date"])
        d_amount = debit["amount"]
        d_counterparty = debit.get("counterparty", "")

        for credit in credits:
            c_date = date.fromisoformat(credit["date"])
            c_amount = credit["amount"]
            c_counterparty = credit.get("counterparty", "")
            days_between = (c_date - d_date).days

            if (
                0 < days_between <= max_days
                and abs(c_amount - d_amount) / max(d_amount, 1) <= amount_tolerance
                and d_counterparty.lower() == c_counterparty.lower()
            ):
                findings.append({
                    "finding_type": "POTENTIAL_CIRCULAR_TRANSACTION",
                    "severity": "HIGH",
                    "out_txn_id": debit["txn_id"],
                    "in_txn_id": credit["txn_id"],
                    "amount": d_amount,
                    "counterparty": d_counterparty,
                    "outflow_date": debit["date"],
                    "inflow_date": credit["date"],
                    "days_between": days_between,
                    "explanation": (
                        f"₹{d_amount:,.0f} transferred to {d_counterparty} on {debit['date']} "
                        f"returned from the same counterparty on {credit['date']} "
                        f"({days_between} day{'s' if days_between>1 else ''} later). "
                        f"This pattern may indicate a circular or window-dressing transaction."
                    ),
                    "recommended_action": "Obtain documentation for both transactions. Not conclusive without investigation.",
                })

    return findings


def detect_cash_deposit_spikes(
    bank_transactions: list[dict],
    spike_threshold_multiplier: float = 2.5,
    window_days: int = 7,
) -> list[dict]:
    """Flag unusually large clusters of cash deposits."""
    cash_deposits = [
        t for t in bank_transactions
        if t["type"] == "CREDIT" and "cash" in t.get("description", "").lower()
    ]

    if len(cash_deposits) < 4:
        return []

    total = sum(t["amount"] for t in cash_deposits)
    avg_daily = total / max(len(cash_deposits), 1)

    findings = []
    checked = set()
    for i, dep in enumerate(cash_deposits):
        if dep["txn_id"] in checked:
            continue
        dep_date = date.fromisoformat(dep["date"])
        window_deposits = [
            d for d in cash_deposits
            if abs((date.fromisoformat(d["date"]) - dep_date).days) <= window_days
        ]
        window_total = sum(d["amount"] for d in window_deposits)
        if window_total > avg_daily * spike_threshold_multiplier and len(window_deposits) >= 2:
            findings.append({
                "finding_type": "CASH_DEPOSIT_SPIKE",
                "severity": "MEDIUM",
                "window_start": min(d["date"] for d in window_deposits),
                "window_end": max(d["date"] for d in window_deposits),
                "window_total": round(window_total, 2),
                "num_deposits": len(window_deposits),
                "avg_deposit_baseline": round(avg_daily, 2),
                "txn_ids": [d["txn_id"] for d in window_deposits],
                "explanation": (
                    f"₹{window_total:,.0f} in cash deposits across {len(window_deposits)} transactions "
                    f"within {window_days} days — {window_total/max(avg_daily,1):.1f}× the average. "
                    f"Unusual cash deposit patterns may warrant additional review."
                ),
                "recommended_action": "Document source of funds for each deposit. Ensure GST compliance.",
            })
            for d in window_deposits:
                checked.add(d["txn_id"])

    return findings


# ─── READINESS SCORE ──────────────────────────────────────────────────────────

SCORE_WEIGHTS = {
    "cash_flow_stability":      0.25,
    "customer_concentration":   0.15,
    "debt_service_capacity":    0.20,
    "receivables_quality":      0.15,
    "reconciliation_health":    0.15,
    "transaction_behaviour":    0.10,
}

SCORE_MIN = 300
SCORE_MAX = 900


def compute_readiness_score(
    cash_flow_stability: float,      # 0–100
    customer_concentration: float,   # 0–100 (100 = well diversified)
    debt_service_capacity: float,    # 0–100
    receivables_quality: float,      # 0–100
    reconciliation_health: float,    # 0–100
    transaction_behaviour: float,    # 0–100
) -> dict:
    """
    Compute the Mausam demonstration readiness index.
    Scale: 300 (very poor) to 900 (excellent).
    NOT a CIBIL score or official lending metric.
    """
    components = {
        "cash_flow_stability": round(cash_flow_stability, 1),
        "customer_concentration": round(customer_concentration, 1),
        "debt_service_capacity": round(debt_service_capacity, 1),
        "receivables_quality": round(receivables_quality, 1),
        "reconciliation_health": round(reconciliation_health, 1),
        "transaction_behaviour": round(transaction_behaviour, 1),
    }

    weighted_sum = sum(
        components[k] * SCORE_WEIGHTS[k] for k in SCORE_WEIGHTS
    )

    # Map 0–100 weighted score to 300–900 display scale
    raw_score = SCORE_MIN + (weighted_sum / 100) * (SCORE_MAX - SCORE_MIN)
    score = round(min(SCORE_MAX, max(SCORE_MIN, raw_score)))

    if score >= 750:   band = "Excellent"
    elif score >= 650: band = "Good"
    elif score >= 550: band = "Fair"
    elif score >= 450: band = "Caution"
    else:              band = "High Risk"

    return {
        "score": score,
        "band": band,
        "components": components,
        "weights": SCORE_WEIGHTS,
        "score_min": SCORE_MIN,
        "score_max": SCORE_MAX,
        "disclaimer": (
            "This is the Mausam demonstration readiness index. "
            "It is NOT a CIBIL score, credit bureau rating, or any official lending metric. "
            "Lender decisions depend on their own policies and additional factors."
        ),
    }


def compute_dscr(
    net_operating_income: float,
    total_debt_service: float,
) -> dict | None:
    """Compute Debt Service Coverage Ratio. Returns None if insufficient data."""
    if total_debt_service <= 0:
        return None
    dscr = net_operating_income / total_debt_service
    return {
        "dscr": round(dscr, 2),
        "net_operating_income": round(net_operating_income, 2),
        "total_debt_service": round(total_debt_service, 2),
        "interpretation": (
            "≥1.25 generally considered adequate by lenders" if dscr >= 1.25
            else "Below 1.25 — debt service may strain cash flow"
        ),
    }


# ─── RESCUE PLANNER ───────────────────────────────────────────────────────────

def compute_loan_emi(principal: float, annual_rate_pct: float, tenure_months: int) -> dict:
    """Compute monthly EMI and full repayment schedule."""
    if tenure_months <= 0 or principal <= 0:
        return {"error": "Invalid parameters"}

    monthly_rate = annual_rate_pct / 100 / 12
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months / (
            (1 + monthly_rate) ** tenure_months - 1
        )

    total_payment = emi * tenure_months
    total_interest = total_payment - principal

    schedule = []
    remaining = principal
    for month in range(1, tenure_months + 1):
        interest_comp = remaining * monthly_rate
        principal_comp = emi - interest_comp
        remaining -= principal_comp
        schedule.append({
            "month": month,
            "emi": round(emi, 2),
            "principal": round(principal_comp, 2),
            "interest": round(interest_comp, 2),
            "balance": round(max(0, remaining), 2),
        })

    return {
        "principal": round(principal, 2),
        "annual_rate_pct": annual_rate_pct,
        "tenure_months": tenure_months,
        "monthly_emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "schedule": schedule[:12],  # first 12 months in response
    }


def evaluate_rescue_intervention(
    intervention_type: str,
    params: dict,
    current_cash: float,
    daily_schedule: list[dict],
    minimum_reserve: float,
) -> dict:
    """
    Evaluate a single rescue intervention and return its impact.
    All calculations are deterministic.
    """
    original_shortfall_day = compute_runway_days(daily_schedule, minimum_reserve)
    original_min_balance = min(d["closing_balance"] for d in daily_schedule)

    impact_cash = 0.0
    cost = 0.0
    assumptions = []

    if intervention_type == "EARLY_COLLECTION":
        customer_name = params.get("customer_name", "Customer")
        outstanding = params.get("outstanding_amount", 0)
        days_early = params.get("days_early", 7)
        impact_cash = outstanding
        assumptions.append(f"Assumes {customer_name} agrees to pay ₹{outstanding:,.0f} {days_early} days early.")
        assumptions.append("Early payment is at the customer's discretion and not guaranteed.")

    elif intervention_type == "EARLY_PAYMENT_DISCOUNT":
        outstanding = params.get("outstanding_amount", 0)
        discount_pct = params.get("discount_pct", 2.0)
        impact_cash = outstanding * (1 - discount_pct / 100)
        cost = outstanding * (discount_pct / 100)
        assumptions.append(f"{discount_pct}% discount offered for early payment of ₹{outstanding:,.0f}.")
        assumptions.append("Customer acceptance rate is uncertain and not modelled here.")

    elif intervention_type == "SUPPLIER_DEFERRAL":
        supplier_amount = params.get("supplier_amount", 0)
        defer_days = params.get("defer_days", 15)
        impact_cash = supplier_amount  # temporarily improves cash position
        assumptions.append(f"Supplier agrees to defer payment of ₹{supplier_amount:,.0f} by {defer_days} days.")
        assumptions.append("Deferral may affect supplier relationship and future credit terms.")

    elif intervention_type == "NEW_LOAN":
        loan_amount = params.get("loan_amount", 0)
        annual_rate = params.get("annual_rate_pct", 12.0)
        tenure = params.get("tenure_months", 12)
        emi_data = compute_loan_emi(loan_amount, annual_rate, tenure)
        impact_cash = loan_amount
        cost = emi_data["total_interest"]
        assumptions.append(f"Loan amount ₹{loan_amount:,.0f} at {annual_rate}% p.a. for {tenure} months.")
        assumptions.append(f"Monthly EMI: ₹{emi_data['monthly_emi']:,.0f}. Total interest: ₹{cost:,.0f}.")
        assumptions.append("Loan approval is not guaranteed. Rates are illustrative.")

    elif intervention_type == "EXPENSE_REDUCTION":
        monthly_savings = params.get("monthly_savings", 0)
        impact_cash = monthly_savings  # simplified: one-month savings
        assumptions.append(f"Monthly expense reduction of ₹{monthly_savings:,.0f} assumed.")
        assumptions.append("Actual savings depend on specific expense line and operational constraints.")

    # Simulate modified cash flow
    new_current_cash = current_cash + impact_cash
    new_schedule = []
    running = new_current_cash
    for day in daily_schedule:
        running = running + day["inflow"] - day["outflow"]
        new_schedule.append({**day, "closing_balance": round(running, 2)})

    new_shortfall_day = compute_runway_days(new_schedule, minimum_reserve)
    new_min_balance = min(d["closing_balance"] for d in new_schedule)

    runway_improvement = new_shortfall_day - original_shortfall_day
    balance_improvement = new_min_balance - original_min_balance

    return {
        "intervention_type": intervention_type,
        "impact_cash": round(impact_cash, 2),
        "cost": round(cost, 2),
        "net_benefit": round(impact_cash - cost, 2),
        "original_runway_days": original_shortfall_day,
        "new_runway_days": new_shortfall_day,
        "runway_improvement_days": runway_improvement,
        "original_min_balance": round(original_min_balance, 2),
        "new_min_balance": round(new_min_balance, 2),
        "balance_improvement": round(balance_improvement, 2),
        "assumptions": assumptions,
        "disclaimer": "Simulated outcomes are illustrative. Actual results depend on many factors outside this model.",
    }
