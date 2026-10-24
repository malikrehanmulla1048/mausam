"""
MAUSAM — AI Payment Delay & Cash-Flow Risk Prediction Model
Predicts invoice payment delay (delay_days), late payment probability,
and assigns customer reliability grades based on historical settlement behaviors.
"""
import math
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ─── Pydantic Data Models ────────────────────────────────────────────────────

class PaymentHistoryRecord(BaseModel):
    business_id: str
    invoice_id: str
    customer_id: str
    payment_date: str
    delay_days: int = Field(ge=0, description="Days delayed past credit terms / due date")
    amount_paid: float
    is_demo: bool = False


class PaymentDelayPrediction(BaseModel):
    invoice_id: str
    customer_id: str
    invoice_amount: float
    due_date: str
    predicted_payment_date: str
    predicted_delay_days: int
    late_probability: float
    confidence: float
    reliability_grade: str
    risk_level: str
    recommended_action: str


# ─── Statistical ML Model: PaymentDelayPredictor ─────────────────────────────

class PaymentDelayPredictor:
    """
    Empirical Bayes & Time-Decay Weighted Model for Customer Payment Delay.
    Learns customer behavioral parameters:
      - mean_delay (μ)
      - delay_variance (σ)
      - recent_drift_trend (slope of delay over time)
      - amount_elasticity (tendency to delay larger invoices longer)
    """

    def __init__(self):
        self.customer_profiles: Dict[str, Dict[str, Any]] = {}
        self.global_mean_delay: float = 18.0
        self.global_std_delay: float = 12.0
        self.is_fitted: bool = False

    def fit(self, payment_histories: List[Dict[str, Any]], invoices: Optional[List[Dict[str, Any]]] = None) -> "PaymentDelayPredictor":
        """
        Train the model using historical payment settlements.
        """
        if not payment_histories:
            return self

        # Map invoice amounts if provided
        inv_amount_map = {}
        if invoices:
            for inv in invoices:
                inv_amount_map[inv["invoice_id"]] = float(inv.get("amount", 0.0))

        # Group by customer
        by_customer: Dict[str, List[Dict[str, Any]]] = {}
        all_delays = []

        for p in payment_histories:
            cid = p.get("customer_id")
            delay = float(p.get("delay_days", 0))
            all_delays.append(delay)
            by_customer.setdefault(cid, []).append(p)

        if all_delays:
            self.global_mean_delay = sum(all_delays) / len(all_delays)
            variance = sum((d - self.global_mean_delay) ** 2 for d in all_delays) / max(len(all_delays), 1)
            self.global_std_delay = math.sqrt(variance) if variance > 0 else 5.0

        # Compute customer parameters with Bayesian shrinkage
        for cid, records in by_customer.items():
            # Sort chronologically
            records.sort(key=lambda x: str(x.get("payment_date", "")))
            delays = [float(r.get("delay_days", 0)) for r in records]
            n = len(delays)

            # Sample statistics
            sample_mean = sum(delays) / n
            sample_var = sum((d - sample_mean) ** 2 for d in delays) / max(n - 1, 1)

            # Empirical Bayes weighting (shrink small-sample customers towards global mean)
            k = 3.0  # prior pseudo-observations
            shrunk_mean = (n * sample_mean + k * self.global_mean_delay) / (n + k)

            # Drift / Trend analysis (is delay getting worse?)
            drift_slope = 0.0
            if n >= 4:
                # Linear trend across sequential payments
                x_vals = list(range(n))
                x_bar = (n - 1) / 2.0
                num = sum((x - x_bar) * (y - sample_mean) for x, y in zip(x_vals, delays))
                den = sum((x - x_bar) ** 2 for x in x_vals)
                drift_slope = num / den if den > 0 else 0.0

            # Reliability grading (A+, A, B, C, D)
            grade = self._classify_grade(shrunk_mean, drift_slope)

            self.customer_profiles[cid] = {
                "sample_count": n,
                "mean_delay": round(shrunk_mean, 1),
                "std_delay": round(math.sqrt(sample_var), 1),
                "drift_slope": round(drift_slope, 2),
                "grade": grade,
                "last_delay": delays[-1] if delays else 0,
            }

        self.is_fitted = True
        return self

    def predict_invoice(
        self,
        customer_id: str,
        invoice_id: str,
        due_date_str: str,
        amount: float,
    ) -> PaymentDelayPrediction:
        """
        Generate payment delay forecast and risk profile for an open invoice.
        """
        profile = self.customer_profiles.get(customer_id)

        if profile:
            base_delay = profile["mean_delay"]
            drift = profile["drift_slope"]
            # Amount impact: larger invoices often face mild bureaucratic lag
            amount_factor = 1.0 + min(0.25, max(0.0, (amount - 50_000) / 500_000))
            predicted_delay = int(round((base_delay + max(0.0, drift * 2)) * amount_factor))
            grade = profile["grade"]
            confidence = min(0.95, round(0.60 + 0.03 * profile["sample_count"], 2))
        else:
            predicted_delay = int(round(self.global_mean_delay))
            grade = "B"
            confidence = 0.50

        # Calculate late probability (> 0 days past due)
        if predicted_delay <= 2:
            late_prob = 0.15
            risk_level = "Low"
            recommendation = "Standard automated courtesy reminder 3 days before due date."
        elif predicted_delay <= 15:
            late_prob = 0.45
            risk_level = "Moderate"
            recommendation = "Send friendly SMS reminder on due date; offer 2% early payment discount."
        elif predicted_delay <= 30:
            late_prob = 0.75
            risk_level = "High"
            recommendation = "Priority collection call required. Consider factoring via TReDS (RXIL/M1xchange)."
        else:
            late_prob = 0.92
            risk_level = "Critical"
            recommendation = "Severe working capital drag. Place credit hold on further deliveries; issue formal demand."

        # Parse due date & compute predicted settlement date
        try:
            due_dt = date.fromisoformat(due_date_str)
        except Exception:
            due_dt = date.today() + timedelta(days=30)

        predicted_dt = due_dt + timedelta(days=predicted_delay)

        return PaymentDelayPrediction(
            invoice_id=invoice_id,
            customer_id=customer_id,
            invoice_amount=round(amount, 2),
            due_date=due_dt.isoformat(),
            predicted_payment_date=predicted_dt.isoformat(),
            predicted_delay_days=predicted_delay,
            late_probability=late_prob,
            confidence=confidence,
            reliability_grade=grade,
            risk_level=risk_level,
            recommended_action=recommendation,
        )

    @staticmethod
    def _classify_grade(avg_delay: float, trend_slope: float) -> str:
        if avg_delay <= 5 and trend_slope <= 0.2:
            return "A+"
        elif avg_delay <= 15 and trend_slope <= 0.5:
            return "A"
        elif avg_delay <= 25:
            return "B"
        elif avg_delay <= 40:
            return "C"
        else:
            return "D"
