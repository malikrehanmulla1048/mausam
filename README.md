# 🌦️ MAUSAM — AI Cash-Flow Intelligence Platform for Indian MSMEs
> *AWS + MongoDB Hackathon 2025 Edition*

**MAUSAM** (मौसम) is a cloud-native financial intelligence platform designed specifically for the 63+ million Indian Micro, Small, and Medium Enterprises (MSMEs). By unifying GST filings (GSTR-1, 2B, 3B), multi-bank statement data, and Tally/ERP accounting ledgers into a real-time MongoDB Atlas data fabric, MAUSAM forecasts liquidity risks, diagnoses debtor delays, catches circular billing fraud, and simulates working capital interventions.

---

## 🚀 Key Modules & Capabilities

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                 MAUSAM PLATFORM                                  │
├─────────────────┬─────────────────┬──────────────────┬───────────────────────────┤
│  🌦 CASH MAUSAM  │  🧬 DEBTOR DNA  │  🔍 TRUTH CHECK  │  🩻 BANK'S-EYE X-RAY      │
│  90-day forecast│  Customer score │  GST/Bank/ERP 3- │  Credit readiness score,  │
│  Monte Carlo P10│  Promised vs    │  way match, ring │  DSCR gauge, pre-emptive  │
│  P50/P90, D-Day │  actual lag, WC │  trading & ghost │  underwriting mitigations │
│  radar sliders  │  drag, WhatsApp │  invoice detector│                           │
├─────────────────┼─────────────────┼──────────────────┼───────────────────────────┤
│ 🛟 RESCUE PLAN  │ 🏛️ AI COMMITTEE  │ 🚨 ALERTS CENTRE │ 📜 HEALTH PASSPORT        │
│ TReDS factoring,│ Bedrock 3-agent │ Multilingual     │ Cryptographically signed  │
│ cash discounts, │ risk deliberation│ alerts in Hindi, │ QR code badge for lenders │
│ vendor delays   │ & sanction memo │ Tamil, Gujarati  │ without trade data leak   │
└─────────────────┴─────────────────┴──────────────────┴───────────────────────────┘
```

### 1. 🌦 Cash Mausam (90-Day Liquidity Forecast)
- **Monte Carlo Simulation**: 1,000 statistical iterations rendering P10 (Pessimistic), P50 (Expected), and P90 (Optimistic) cash trajectories.
- **Cash D-Day Radar**: Automatically calculates the exact date and projected deficit when working capital dips below zero.
- **Stress-Testing Radar**: Real-time sliders for *Debtor Delay Shocks* (+0 to +30 days) and *Revenue Demand Shocks* (-30% to +15%).

### 2. 🧬 Debtor DNA (Customer Payment Intelligence)
- Profiles customer reliability across grades (**A+**, **A**, **B**, **C**, **D**).
- Computes **Working Capital Drag** (₹ locked in late payments beyond contractual credit terms).
- Direct WhatsApp nudge trigger with auto-generated contextual reminders.

### 3. 🔍 Truth Check (3-Way Reconciliation & Anomaly Radar)
- Multi-way cross-reconciliation between **GST Portal**, **Bank Statement Credits**, and **Tally Books**.
- Autonomous anomaly detection for:
  - **Circular Billing Rings**: Identifies artificial turnover churn loops with identical lot numbers and near-zero margins.
  - **Phantom / Cancelled GSTIN ITC**: Catches disallowed input tax credit from retrospectively cancelled vendor GSTINs.
  - **Ghost Invoices**: Uncredited cheques and missing bank settlements.
  - **Form 26AS TDS Mismatches**: Unreflected tax deductions on Traces portal.

### 4. 🩻 Bank's-Eye X-Ray (Underwriting Readiness)
- Generates a **0–100 Credit Readiness Score** tailored to Indian bank lending guidelines (SBI, HDFC, SIDBI).
- Evaluates **DSCR (Debt Service Coverage Ratio)**, **Current Ratio**, and **HHI Revenue Concentration**.
- Produces pre-emptive mitigation notes and exportable Credit Memos.

### 5. 🛟 Rescue Planner (Interactive Interventions)
- Live working capital levers:
  - **Early Payment Discounts** (2/10 Net 30 for prompt payers).
  - **TReDS Invoice Discounting** (RXIL / M1xchange factoring at ~8.2% p.a.).
  - **Supplier Payment Staggering** (Negotiated yarn/raw material deferrals).
  - **Emergency MSME Credit Line** (CGTMSE / SIDBI Prayaas drawdown).
- Dynamically recalculates net liquidity delta to verify that the Cash D-Day deficit is eliminated.

### 6. 🏛️ AI Credit Committee (Amazon Bedrock Multi-Agent)
- Simulates an autonomous bank credit committee composed of 3 specialized agent personas:
  - 🛡️ **Prudence (Risk Officer)**: Evaluates debtor concentration and fraud risks.
  - 🚀 **Catalyst (Growth Officer)**: Evaluates sector tailwinds, margins, and market opportunity.
  - ⚖️ **Arbiter (Chief Underwriter)**: Issues a binding sanction memo with facility limits, rates, and covenants.

### 7. 🚨 Alerts & Action Centre
- Categorized action feeds (**Critical**, **Warning**, **Opportunity**).
- Multilingual communications engine supporting **English**, **हिंदी (Hindi)**, **தமிழ் (Tamil)**, and **ગુજરાતી (Gujarati)**.
- Single-click WhatsApp payment reminders with tone selection (*Gentle*, *Firm*, *Legal Notice*).

### 8. 📜 Health Passport (Verifiable MSME Financial Badge)
- Cryptographically signed financial badge using **AWS KMS / HMAC SHA-256**.
- Scannable **QR code** for bank relationship managers and NBFC underwriters.
- Zero-knowledge style privacy: verifies solvency, DSCR, and tax compliance without disclosing sensitive supplier margins or customer lists.

---

## 🛠️ Architecture & Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Vanilla CSS with custom glassmorphism design system, Lucide icons.
- **Backend**: FastAPI (Python 3.11), Uvicorn, Pydantic v2, Pandas, NumPy, SciPy.
- **Database**: MongoDB Atlas with multi-key compound indexes; resilient in-memory `mongomock` fallback for offline demo development.
- **AWS Cloud Integration**:
  - **Amazon Bedrock**: Multi-agent reasoning for the AI Credit Committee (`anthropic.claude-3-5-sonnet`).
  - **AWS KMS**: Cryptographic signing and verification for MSME Health Passports.
  - **Amazon S3**: Secure storage for financial statements, GSTR JSONs, and audit memos.
  - **AWS Lambda & Mangum**: Serverless backend hosting option.

---

## 💻 Quick Start & Local Execution

### 1. Prerequisites
- Python 3.11
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd backend

# Create virtual environment and install dependencies
py -3.11 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install mongomock

# Generate synthetic MSME dataset (305 invoices, 465 bank txns, 9 anomalies)
.venv\Scripts\python scripts/generate_demo_data.py

# Run test suite
.venv\Scripts\python -m pytest -o pythonpath=. -p no:cacheprovider tests/test_api.py -v

# Start FastAPI server (runs on port 8000)
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Build production bundle
npm run build

# Start Vite dev server (runs on port 5173)
npm run dev -- --host 127.0.0.1 --port 5173
```

Open **`http://127.0.0.1:5173/`** in your browser.

---

## 🧪 Test Coverage
All unit and integration tests are verified in `backend/tests/test_api.py`:
- `test_health_endpoint` ✅
- `test_demo_seed_and_overview` ✅
- `test_cash_forecast` ✅
- `test_reconciliation_findings` ✅
- `test_health_passport_creation` ✅

---

## 📄 License
Built for the AWS + MongoDB Hackathon 2025. Proprietary to MAUSAM team.
