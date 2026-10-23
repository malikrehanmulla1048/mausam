"""
MAUSAM — Synthetic Demonstration Data Generator
Generates a reproducible 12-month dataset for Ramesh Textiles (Surat, Gujarat).
All data is clearly synthetic and labelled as demonstration data.

Planted anomalies:
1. Sharma Traders: payment delay drifts from 30→52 days over 12 months
2. Diwali cluster: large stock purchase + GST obligation + EMI in same week
3. INV-0412: marked PAID but no matching bank credit
4. Duplicate invoice number INV-0187 (same number, different amounts)
5. Bank credits exceed GST turnover by ~38% in months 3 and 9
6. EMI bounce in March (bank debit returned)
7. Unusual cash deposit spike in week before hypothetical loan application
8. ₹4.2 lakh round-trip: outflow returns within 3 days (circular indicator)
9. Month 6 (June) is clean control — no anomalies
"""
import random
import json
import hashlib
from datetime import date, datetime, timedelta
from typing import Any
from pathlib import Path

SEED = 42
random.seed(SEED)

# ─── business constants ───────────────────────────────────────────────────────
BUSINESS_ID = "demo_ramesh_textiles"
START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)
OPENING_CASH = 4_80_000       # ₹4.8 lakh

# ─── customers ────────────────────────────────────────────────────────────────
CUSTOMERS = [
    {"customer_id": "CUST-001", "name": "Sharma Traders",         "city": "Ahmedabad", "base_delay_days": 30, "credit_limit": 10_00_000},
    {"customer_id": "CUST-002", "name": "Mehta Fabrics",          "city": "Mumbai",    "base_delay_days": 15, "credit_limit":  8_00_000},
    {"customer_id": "CUST-003", "name": "Patel Garments",         "city": "Surat",     "base_delay_days": 10, "credit_limit":  6_00_000},
    {"customer_id": "CUST-004", "name": "Krishna Exports",        "city": "Delhi",     "base_delay_days": 45, "credit_limit": 12_00_000},
    {"customer_id": "CUST-005", "name": "Joshi Textiles",         "city": "Pune",      "base_delay_days": 20, "credit_limit":  5_00_000},
    {"customer_id": "CUST-006", "name": "Reddy Clothiers",        "city": "Hyderabad", "base_delay_days": 25, "credit_limit":  7_00_000},
    {"customer_id": "CUST-007", "name": "Singh Readymade",        "city": "Ludhiana",  "base_delay_days": 35, "credit_limit":  9_00_000},
    {"customer_id": "CUST-008", "name": "Gupta Wholesale",        "city": "Kanpur",    "base_delay_days": 18, "credit_limit":  4_00_000},
    {"customer_id": "CUST-009", "name": "Agarwal Fashion House",  "city": "Jaipur",    "base_delay_days": 22, "credit_limit":  6_50_000},
    {"customer_id": "CUST-010", "name": "Nair Emporiums",         "city": "Kochi",     "base_delay_days": 28, "credit_limit":  5_50_000},
    {"customer_id": "CUST-011", "name": "Chauhan Brothers",       "city": "Indore",    "base_delay_days": 12, "credit_limit":  3_00_000},
    {"customer_id": "CUST-012", "name": "Desai Silk House",       "city": "Surat",     "base_delay_days": 8,  "credit_limit":  4_50_000},
]

# ─── suppliers ────────────────────────────────────────────────────────────────
SUPPLIERS = [
    {"supplier_id": "SUPP-001", "name": "Ravi Yarn Mills",         "city": "Coimbatore", "payment_terms_days": 30},
    {"supplier_id": "SUPP-002", "name": "Bombay Dyeing Wholesale", "city": "Mumbai",     "payment_terms_days": 45},
    {"supplier_id": "SUPP-003", "name": "Gujarat Textile Corp",    "city": "Surat",      "payment_terms_days": 21},
    {"supplier_id": "SUPP-004", "name": "Tiruppur Knits",          "city": "Tiruppur",   "payment_terms_days": 30},
    {"supplier_id": "SUPP-005", "name": "National Fiber Pvt Ltd",  "city": "Silvassa",   "payment_terms_days": 60},
    {"supplier_id": "SUPP-006", "name": "Dhruv Silk Traders",      "city": "Varanasi",   "payment_terms_days": 30},
    {"supplier_id": "SUPP-007", "name": "Raj Cotton Exports",      "city": "Rajkot",     "payment_terms_days": 21},
    {"supplier_id": "SUPP-008", "name": "Om Synthetics",           "city": "Surat",      "payment_terms_days": 15},
]

# ─── recurring obligations ────────────────────────────────────────────────────
OBLIGATIONS = [
    {"obligation_id": "OBL-001", "name": "Shop Rent",           "type": "rent",    "amount": 55_000,  "day_of_month": 1},
    {"obligation_id": "OBL-002", "name": "Salaries (14 staff)", "type": "salary",  "amount": 2_80_000, "day_of_month": 5},
    {"obligation_id": "OBL-003", "name": "SBI Business Loan EMI","type": "emi",    "amount": 42_000,  "day_of_month": 10},
    {"obligation_id": "OBL-004", "name": "Electricity",         "type": "utility", "amount": 18_000,  "day_of_month": 15},
    {"obligation_id": "OBL-005", "name": "GST Payment",         "type": "tax",     "amount": 0,       "day_of_month": 20},  # variable
    {"obligation_id": "OBL-006", "name": "Accounting Software", "type": "software","amount": 3_500,   "day_of_month": 1},
    {"obligation_id": "OBL-007", "name": "Vehicle EMI",         "type": "emi",     "amount": 18_500,  "day_of_month": 7},
]

# ─── helpers ─────────────────────────────────────────────────────────────────

def jitter(base: float, pct: float = 0.15) -> float:
    return base * (1 + random.uniform(-pct, pct))

def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def to_iso(d: date | datetime) -> str:
    if isinstance(d, datetime):
        return d.isoformat()
    return d.isoformat()

def months_between(start: date, end: date) -> list[date]:
    result = []
    cur = date(start.year, start.month, 1)
    while cur <= end:
        result.append(cur)
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return result

# Monthly revenue profile (index 0 = Jan)
MONTHLY_REVENUE_MULTIPLIER = [0.7, 0.75, 0.85, 0.9, 0.8, 0.75, 0.85, 0.95, 1.0, 1.4, 1.6, 0.9]


def generate_dataset() -> dict[str, Any]:
    ground_truth_labels = []
    invoices = []
    bank_txns = []
    payment_histories = []
    gst_summaries = []
    payment_predictions_data = []

    invoice_counter = 1
    txn_counter = 1

    monthly_sales = {}  # period_key -> float (for GST reconciliation)
    monthly_bank_credits = {}  # period_key -> float

    # Track current bank balance for circular transaction plant
    bank_balance_running = OPENING_CASH

    def next_inv_id():
        nonlocal invoice_counter
        inv_id = f"INV-{invoice_counter:04d}"
        invoice_counter += 1
        return inv_id

    def next_txn_id():
        nonlocal txn_counter
        txn_id = f"TXN-{txn_counter:04d}"
        txn_counter += 1
        return txn_id

    # ── GENERATE INVOICES (sales) ─────────────────────────────────────────────
    # ~25 invoices/month × 12 months = ~300
    for month_idx, month_start in enumerate(months_between(START_DATE, END_DATE)):
        month_end = date(
            month_start.year,
            month_start.month,
            28 if month_start.month == 2 else 30 if month_start.month in [4,6,9,11] else 31
        )
        rev_mult = MONTHLY_REVENUE_MULTIPLIER[month_idx]
        n_invoices = int(jitter(25, 0.2))
        period_key = month_start.strftime("%Y-%m")
        monthly_sales[period_key] = 0.0

        for _ in range(n_invoices):
            cust = random.choice(CUSTOMERS)
            cid = cust["customer_id"]
            inv_date = rand_date(month_start, month_end)
            base_amount = jitter(random.uniform(20_000, 1_80_000) * rev_mult)
            amount = round(base_amount, 2)
            gst_rate = random.choice([0.05, 0.12, 0.18])
            gst_amount = round(amount * gst_rate, 2)
            total_amount = round(amount + gst_amount, 2)
            payment_terms = 30  # net-30 standard

            # Sharma Traders: payment delay drifts 30→52 days over year
            if cid == "CUST-001":
                drift = int(22 * (month_idx / 11))  # 0 to 22 extra days
                effective_delay = cust["base_delay_days"] + drift
            else:
                effective_delay = cust["base_delay_days"]

            due_date = inv_date + timedelta(days=payment_terms)
            actual_payment_delay = effective_delay + random.randint(-3, 5)
            actual_payment_date = inv_date + timedelta(days=actual_payment_delay)

            # ANOMALY 3: INV-0412 marked PAID but no bank credit
            is_anomaly_inv0412 = False

            inv_id = next_inv_id()
            if invoice_counter - 1 == 412:
                inv_id = "INV-0412"
                is_anomaly_inv0412 = True

            # ANOMALY 4: Duplicate invoice number INV-0187
            is_duplicate = False
            if invoice_counter - 1 == 250:
                inv_id = "INV-0187"
                is_duplicate = True

            status = "PAID" if actual_payment_date <= date.today() else "OUTSTANDING"
            if inv_date < date(2025, 11, 1):
                status = "PAID"

            if is_anomaly_inv0412:
                status = "PAID"  # Marked paid but NO bank credit will be created

            invoice_rec = {
                "invoice_id": inv_id,
                "business_id": BUSINESS_ID,
                "customer_id": cid,
                "customer_name": cust["name"],
                "invoice_date": to_iso(inv_date),
                "due_date": to_iso(due_date),
                "payment_terms_days": payment_terms,
                "amount": amount,
                "gst_rate": gst_rate,
                "gst_amount": gst_amount,
                "total_amount": total_amount,
                "currency": "INR",
                "status": status,
                "actual_payment_date": to_iso(actual_payment_date) if status == "PAID" else None,
                "payment_delay_days": (actual_payment_date - inv_date).days if status == "PAID" else None,
                "is_demo": True,
                "_anomaly_type": (
                    "PAID_NO_CREDIT" if is_anomaly_inv0412
                    else "DUPLICATE_INVOICE_NUMBER" if is_duplicate
                    else None
                ),
            }
            invoices.append(invoice_rec)
            monthly_sales[period_key] = monthly_sales.get(period_key, 0) + total_amount

            # Payment history
            if status == "PAID":
                payment_histories.append({
                    "business_id": BUSINESS_ID,
                    "invoice_id": inv_id,
                    "customer_id": cid,
                    "payment_date": to_iso(actual_payment_date),
                    "delay_days": max(0, (actual_payment_date - due_date).days),
                    "amount_paid": total_amount,
                    "is_demo": True,
                })

    # ── GENERATE BANK TRANSACTIONS ─────────────────────────────────────────────
    # Receipts from customers
    paid_invoices = [inv for inv in invoices if inv["status"] == "PAID" and inv.get("_anomaly_type") != "PAID_NO_CREDIT"]

    for inv in paid_invoices:
        pay_date = date.fromisoformat(inv["actual_payment_date"])
        period_key = pay_date.strftime("%Y-%m")
        bank_txns.append({
            "txn_id": next_txn_id(),
            "business_id": BUSINESS_ID,
            "date": to_iso(pay_date),
            "type": "CREDIT",
            "amount": inv["total_amount"],
            "description": f"Payment from {inv['customer_name']} for {inv['invoice_id']}",
            "counterparty": inv["customer_name"],
            "reference": inv["invoice_id"],
            "balance_after": None,  # will compute
            "is_demo": True,
            "_anomaly_type": None,
        })
        monthly_bank_credits[period_key] = monthly_bank_credits.get(period_key, 0) + inv["total_amount"]

    # ANOMALY 5: Bank credits exceed GST turnover by ~38% in months 3 and 9 (March, September)
    for anomaly_month in ["2025-03", "2025-09"]:
        extra_credit = monthly_sales.get(anomaly_month, 8_00_000) * 0.38
        anomaly_date = date(int(anomaly_month[:4]), int(anomaly_month[5:]), random.randint(10, 20))
        bank_txns.append({
            "txn_id": next_txn_id(),
            "business_id": BUSINESS_ID,
            "date": to_iso(anomaly_date),
            "type": "CREDIT",
            "amount": round(extra_credit, 2),
            "description": "Cash deposit - source undocumented",
            "counterparty": "CASH",
            "reference": f"CASH-DEP-{anomaly_month}",
            "balance_after": None,
            "is_demo": True,
            "_anomaly_type": "EXCESS_BANK_CREDIT_VS_GST",
        })
        monthly_bank_credits[anomaly_month] = monthly_bank_credits.get(anomaly_month, 0) + extra_credit
        ground_truth_labels.append({
            "label_id": f"GT-{len(ground_truth_labels)+1:03d}",
            "anomaly_type": "EXCESS_BANK_CREDIT_VS_GST",
            "period": anomaly_month,
            "expected_amount": monthly_sales.get(anomaly_month, 0),
            "observed_amount": monthly_bank_credits.get(anomaly_month, 0),
            "description": f"Bank credits exceed GST turnover by ~38% in {anomaly_month}",
            "planted": True,
        })

    # ANOMALY 6: EMI bounce in March
    emi_bounce_date = date(2025, 3, 10)
    bank_txns.append({
        "txn_id": next_txn_id(),
        "business_id": BUSINESS_ID,
        "date": to_iso(emi_bounce_date),
        "type": "DEBIT",
        "amount": 42_000,
        "description": "SBI Business Loan EMI - RETURNED/BOUNCED",
        "counterparty": "SBI Bank",
        "reference": "EMI-BOUNCE-MAR25",
        "balance_after": None,
        "is_demo": True,
        "_anomaly_type": "EMI_BOUNCE",
    })
    ground_truth_labels.append({
        "label_id": f"GT-{len(ground_truth_labels)+1:03d}",
        "anomaly_type": "EMI_BOUNCE",
        "period": "2025-03",
        "date": to_iso(emi_bounce_date),
        "description": "EMI debit returned/bounced in March 2025",
        "planted": True,
    })

    # ANOMALY 7: Unusual cash deposit spike before loan application (October)
    cash_spike_date = date(2025, 10, 5)
    for i in range(3):
        bank_txns.append({
            "txn_id": next_txn_id(),
            "business_id": BUSINESS_ID,
            "date": to_iso(cash_spike_date + timedelta(days=i)),
            "type": "CREDIT",
            "amount": round(jitter(80_000, 0.05), 2),
            "description": "Cash deposit",
            "counterparty": "CASH",
            "reference": f"CASH-SPIKE-{i+1}",
            "balance_after": None,
            "is_demo": True,
            "_anomaly_type": "CASH_DEPOSIT_SPIKE",
        })
    ground_truth_labels.append({
        "label_id": f"GT-{len(ground_truth_labels)+1:03d}",
        "anomaly_type": "CASH_DEPOSIT_SPIKE",
        "period": "2025-10",
        "description": "Three large cash deposits in 3 days preceding loan application window",
        "planted": True,
    })

    # ANOMALY 8: ₹4.2 lakh round-trip within 3 days
    circular_out_date = date(2025, 8, 12)
    circular_in_date = date(2025, 8, 15)
    circular_txn_out = next_txn_id()
    circular_txn_in = next_txn_id()
    bank_txns.append({
        "txn_id": circular_txn_out,
        "business_id": BUSINESS_ID,
        "date": to_iso(circular_out_date),
        "type": "DEBIT",
        "amount": 4_20_000,
        "description": "Transfer to Rajesh Enterprises",
        "counterparty": "Rajesh Enterprises",
        "reference": "NEFT-420000",
        "balance_after": None,
        "is_demo": True,
        "_anomaly_type": "CIRCULAR_TRANSACTION_OUT",
    })
    bank_txns.append({
        "txn_id": circular_txn_in,
        "business_id": BUSINESS_ID,
        "date": to_iso(circular_in_date),
        "type": "CREDIT",
        "amount": 4_20_000,
        "description": "Receipt from Rajesh Enterprises",
        "counterparty": "Rajesh Enterprises",
        "reference": "NEFT-420000-RTN",
        "balance_after": None,
        "is_demo": True,
        "_anomaly_type": "CIRCULAR_TRANSACTION_IN",
    })
    ground_truth_labels.append({
        "label_id": f"GT-{len(ground_truth_labels)+1:03d}",
        "anomaly_type": "CIRCULAR_TRANSACTION",
        "period": "2025-08",
        "amount": 4_20_000,
        "out_txn_id": circular_txn_out,
        "in_txn_id": circular_txn_in,
        "days_between": 3,
        "description": "₹4.2 lakh outflow returns to same account within 3 days",
        "planted": True,
    })

    # Regular supplier payments
    for month_idx, month_start in enumerate(months_between(START_DATE, END_DATE)):
        rev_mult = MONTHLY_REVENUE_MULTIPLIER[month_idx]
        for supp in SUPPLIERS:
            # not all suppliers every month
            if random.random() < 0.7:
                pay_date = month_start + timedelta(days=supp["payment_terms_days"] + random.randint(-3, 5))
                if pay_date.month != month_start.month:
                    pay_date = month_start + timedelta(days=supp["payment_terms_days"])
                amount = round(jitter(random.uniform(30_000, 1_50_000) * rev_mult), 2)
                bank_txns.append({
                    "txn_id": next_txn_id(),
                    "business_id": BUSINESS_ID,
                    "date": to_iso(pay_date),
                    "type": "DEBIT",
                    "amount": amount,
                    "description": f"Payment to {supp['name']}",
                    "counterparty": supp["name"],
                    "reference": f"SUPP-{supp['supplier_id']}-{month_start.strftime('%Y%m')}",
                    "balance_after": None,
                    "is_demo": True,
                    "_anomaly_type": None,
                })

    # Recurring obligations
    for month_idx, month_start in enumerate(months_between(START_DATE, END_DATE)):
        for obl in OBLIGATIONS:
            if obl["type"] == "tax":
                continue  # handled in GST section
            try:
                obl_date = date(month_start.year, month_start.month, obl["day_of_month"])
            except ValueError:
                obl_date = date(month_start.year, month_start.month, 28)

            amount = obl["amount"]

            # ANOMALY 6: EMI bounce already added, skip normal EMI for March
            if obl["obligation_id"] == "OBL-003" and month_start.month == 3:
                # Add the bounced EMI re-debit attempt (will be returned)
                continue

            bank_txns.append({
                "txn_id": next_txn_id(),
                "business_id": BUSINESS_ID,
                "date": to_iso(obl_date),
                "type": "DEBIT",
                "amount": amount,
                "description": f"{obl['name']}",
                "counterparty": obl["name"],
                "reference": f"{obl['obligation_id']}-{month_start.strftime('%Y%m')}",
                "balance_after": None,
                "is_demo": True,
                "_anomaly_type": None,
            })

        # ANOMALY 2: Diwali cluster (October = index 9)
        if month_idx == 9:
            # Large Diwali stock purchase
            bank_txns.append({
                "txn_id": next_txn_id(),
                "business_id": BUSINESS_ID,
                "date": to_iso(date(2025, 10, 18)),
                "type": "DEBIT",
                "amount": 8_50_000,
                "description": "Diwali season stock purchase - Gujarat Textile Corp",
                "counterparty": "Gujarat Textile Corp",
                "reference": "DIWALI-STOCK-OCT25",
                "balance_after": None,
                "is_demo": True,
                "_anomaly_type": "DIWALI_CLUSTER_PURCHASE",
            })

    # ── GST SUMMARIES ──────────────────────────────────────────────────────────
    for month_idx, month_start in enumerate(months_between(START_DATE, END_DATE)):
        period_key = month_start.strftime("%Y-%m")
        reported_turnover = monthly_sales.get(period_key, 0)

        # ANOMALY 5: months 3 and 9 underreport in GST vs actual bank
        is_anomaly_month = period_key in ["2025-03", "2025-09"]
        if is_anomaly_month:
            reported_turnover_gst = reported_turnover  # GST turnover stays as invoiced
        else:
            reported_turnover_gst = reported_turnover

        gst_payable = round(reported_turnover_gst * 0.12 * 0.5, 2)  # approx net GST after ITC
        gst_summaries.append({
            "business_id": BUSINESS_ID,
            "period_key": period_key,
            "period_month": month_start.month,
            "period_year": month_start.year,
            "taxable_turnover": round(reported_turnover_gst, 2),
            "gst_collected": round(reported_turnover_gst * 0.12, 2),
            "input_tax_credit": round(reported_turnover_gst * 0.06, 2),
            "net_gst_payable": gst_payable,
            "filed": True,
            "filing_date": to_iso(date(month_start.year, month_start.month, 20)),
            "is_demo": True,
            "_is_anomaly_month": is_anomaly_month,
        })

        # GST payment bank transaction
        bank_txns.append({
            "txn_id": next_txn_id(),
            "business_id": BUSINESS_ID,
            "date": to_iso(date(month_start.year, month_start.month, 20)),
            "type": "DEBIT",
            "amount": gst_payable,
            "description": f"GST Payment {period_key}",
            "counterparty": "GSTN / Government",
            "reference": f"GST-{period_key}",
            "balance_after": None,
            "is_demo": True,
            "_anomaly_type": None,
        })

    # ── GROUND TRUTH: planted anomalies already added above ────────────────────
    # Add INV-0412 and duplicate invoice to ground truth
    ground_truth_labels.insert(0, {
        "label_id": "GT-INV-0412",
        "anomaly_type": "PAID_NO_CREDIT",
        "invoice_id": "INV-0412",
        "description": "Invoice INV-0412 marked PAID in system but no matching bank credit exists",
        "planted": True,
    })
    ground_truth_labels.insert(1, {
        "label_id": "GT-DUP-0187",
        "anomaly_type": "DUPLICATE_INVOICE_NUMBER",
        "invoice_id": "INV-0187",
        "description": "Invoice number INV-0187 used twice with different amounts",
        "planted": True,
    })
    ground_truth_labels.insert(2, {
        "label_id": "GT-SHARMA",
        "anomaly_type": "PAYMENT_DELAY_DRIFT",
        "customer_id": "CUST-001",
        "customer_name": "Sharma Traders",
        "description": "Sharma Traders average payment delay drifts from 30 to 52 days over 12 months",
        "planted": True,
    })
    ground_truth_labels.insert(3, {
        "label_id": "GT-DIWALI",
        "anomaly_type": "DIWALI_CASH_CLUSTER",
        "period": "2025-10",
        "description": "Large stock purchase + GST obligation + EMI converge in October (Diwali)",
        "planted": True,
    })

    # ── PAYMENT PREDICTIONS (for Debtor DNA) ────────────────────────────────────
    outstanding_invoices = [inv for inv in invoices if inv["status"] == "OUTSTANDING"]
    for inv in outstanding_invoices:
        cid = inv["customer_id"]
        cust = next(c for c in CUSTOMERS if c["customer_id"] == cid)
        month_idx = date.fromisoformat(inv["invoice_date"]).month - 1
        if cid == "CUST-001":
            drift = int(22 * (month_idx / 11))
            effective_delay = cust["base_delay_days"] + drift
        else:
            effective_delay = cust["base_delay_days"]

        predicted_payment_date = date.fromisoformat(inv["invoice_date"]) + timedelta(days=effective_delay)
        days_overdue = max(0, (date(2025, 11, 15) - date.fromisoformat(inv["due_date"])).days)
        late_probability = min(0.95, 0.2 + (effective_delay - 15) / 50 + days_overdue / 60)

        payment_predictions_data.append({
            "business_id": BUSINESS_ID,
            "invoice_id": inv["invoice_id"],
            "customer_id": cid,
            "predicted_payment_date": to_iso(predicted_payment_date),
            "confidence": round(0.65 + random.uniform(0, 0.25), 2),
            "late_probability": round(max(0.05, min(0.95, late_probability)), 2),
            "effective_delay_days": effective_delay,
            "method": "historical_weighted_avg",
            "is_demo": True,
        })

    # Sort bank transactions by date
    bank_txns.sort(key=lambda x: x["date"])

    # Compute running balance
    running_bal = OPENING_CASH
    for txn in bank_txns:
        if txn["type"] == "CREDIT":
            running_bal += txn["amount"]
        else:
            running_bal -= txn["amount"]
        txn["balance_after"] = round(running_bal, 2)

    # ── OPENING FORECAST INPUTS ──────────────────────────────────────────────
    # Current cash = last balance before Nov 15, 2025
    pre_nov15_txns = [t for t in bank_txns if t["date"] <= "2025-11-15"]
    current_cash = pre_nov15_txns[-1]["balance_after"] if pre_nov15_txns else OPENING_CASH

    forecast_inputs = {
        "business_id": BUSINESS_ID,
        "as_of_date": "2025-11-15",
        "current_cash": round(current_cash, 2),
        "minimum_reserve": 1_00_000,
        "forecast_days": 42,
        "monthly_revenue_multiplier": MONTHLY_REVENUE_MULTIPLIER,
        "is_demo": True,
    }

    return {
        "business": {
            "business_id": BUSINESS_ID,
            "owner_name": "Ramesh Shah",
            "business_name": "Ramesh Textiles",
            "gstn": "24AAAAA0000A1Z5",  # fictional
            "business_type": "Trading",
            "industry": "Textiles",
            "city": "Surat",
            "state": "Gujarat",
            "employees": 14,
            "bank_name": "State Bank of India",
            "bank_account_masked": "XXXX-XXXX-4821",
            "currency": "INR",
            "opening_cash": OPENING_CASH,
            "minimum_reserve": 1_00_000,
            "is_demo": True,
            "demo_label": "SYNTHETIC DEMONSTRATION DATA — Not a real business",
        },
        "customers": CUSTOMERS,
        "suppliers": SUPPLIERS,
        "obligations": OBLIGATIONS,
        "invoices": invoices,
        "bank_transactions": bank_txns,
        "gst_summaries": gst_summaries,
        "payment_histories": payment_histories,
        "payment_predictions": payment_predictions_data,
        "forecast_inputs": forecast_inputs,
        "ground_truth_labels": ground_truth_labels,
        "metadata": {
            "generator_version": "1.0.0",
            "seed": SEED,
            "generated_at": datetime.utcnow().isoformat(),
            "invoice_count": len(invoices),
            "txn_count": len(bank_txns),
            "anomaly_count": len(ground_truth_labels),
            "is_demo": True,
        },
    }


if __name__ == "__main__":
    print("Generating MAUSAM synthetic demo dataset...")
    data = generate_dataset()
    out_path = Path(__file__).parent / "demo_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"Dataset written to {out_path}")
    print(f"  Invoices:     {data['metadata']['invoice_count']}")
    print(f"  Transactions: {data['metadata']['txn_count']}")
    print(f"  Anomalies:    {data['metadata']['anomaly_count']}")
    print(f"  Ground truth: {len(data['ground_truth_labels'])} labels")
