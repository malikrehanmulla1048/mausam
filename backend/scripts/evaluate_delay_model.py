"""
MAUSAM — Demo & Evaluation of Payment Delay Prediction Model
Loads payment_histories and invoices from demo_data.json, trains the PaymentDelayPredictor,
and prints predictions and customer profile insights.
"""
import sys
import json
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.delay_predictor import PaymentDelayPredictor


def main():
    json_path = backend_dir / "scripts" / "demo_data.json"
    if not json_path.exists():
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    payment_histories = data.get("payment_histories", [])
    invoices = data.get("invoices", [])

    print("=================================================================")
    print(" 🌦️  MAUSAM — AI PAYMENT DELAY & RISK PREDICTION MODEL")
    print("=================================================================")
    print(f"Loaded {len(payment_histories)} payment histories across {len(data.get('customers', []))} customers.")

    # Train model
    model = PaymentDelayPredictor()
    model.fit(payment_histories, invoices)

    print("\n📊 Customer Payment Profiles Learned:")
    print(f"{'Customer ID':<12} {'Grade':<8} {'Avg Delay':<12} {'Std Dev':<10} {'Trend':<10} {'Samples':<8}")
    print("-" * 65)
    for cid, prof in sorted(model.customer_profiles.items()):
        trend_desc = "Worsening" if prof["drift_slope"] > 0.4 else "Stable"
        print(f"{cid:<12} {prof['grade']:<8} {prof['mean_delay']:>5.1f} days  {prof['std_delay']:>5.1f} d   {trend_desc:<10} {prof['sample_count']:<8}")

    print("\n🔍 Live Prediction Sample for Open Invoices:")
    print("-" * 85)
    # Pick 4 representative open invoices
    test_invoices = [
        {"customer_id": "CUST-001", "invoice_id": "INV-NEW-01", "due_date": "2025-12-01", "amount": 125000.0},
        {"customer_id": "CUST-003", "invoice_id": "INV-NEW-02", "due_date": "2025-12-05", "amount": 84000.0},
        {"customer_id": "CUST-004", "invoice_id": "INV-NEW-03", "due_date": "2025-12-10", "amount": 250000.0},
        {"customer_id": "CUST-012", "invoice_id": "INV-NEW-04", "due_date": "2025-12-15", "amount": 45000.0},
    ]

    for inv in test_invoices:
        pred = model.predict_invoice(
            customer_id=inv["customer_id"],
            invoice_id=inv["invoice_id"],
            due_date_str=inv["due_date"],
            amount=inv["amount"],
        )
        print(f"Invoice: {pred.invoice_id} | Customer: {pred.customer_id} | Amount: ₹{pred.invoice_amount:,.2f}")
        print(f"  • Due Date:           {pred.due_date}")
        print(f"  • Predicted Payment:  {pred.predicted_payment_date} (+{pred.predicted_delay_days} days delay)")
        print(f"  • Late Probability:   {int(pred.late_probability * 100)}% | Risk Level: {pred.risk_level} | Grade: {pred.reliability_grade}")
        print(f"  • Action:             {pred.recommended_action}\n")


if __name__ == "__main__":
    main()
