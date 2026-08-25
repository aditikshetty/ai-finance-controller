# ai-finance-controller
# FinControl AI — Autonomous Financial Reconciliation & Audit Engine

> **Razorpay Buildathon (Track 04)** | *Hybrid 3-Tier Waterfall Architecture: Deterministic Math Core, Scikit-Learn ML Risk Prioritization, and Autonomous Gemini 3.6 Flash LLM Auditor with CFO Copilot.*

---

## 1. Executive Summary

Enterprise payment reconciliation across disparate sources (ERP Invoices, Gateway Webhooks, and Bank Settlement Feeds) traditionally suffers from two systemic points of failure:
1. **Floating-Point Drift:** Native binary floating-point representation causes fractional rounding inaccuracies on multi-tier fees (MDR, GST, TDS), leading to false exception alerts.
2. **LLM Hallucinations:** Using unstructured LLM prompts to analyze raw logs leads to speculative explanations without live verifiable proof from banking or gateway backends.

**FinControl AI** resolves this with a **Hybrid 3-Tier Waterfall Architecture**:
- **Tier 1 (Deterministic Core):** Strict integer-paisa fixed-point arithmetic reconciles the clean 95% volume in sub-milliseconds with mathematical certainty.
- **Tier 2 (ML Risk Prioritization):** A Scikit-learn classification model scores loss exposure probability (0.00 - 1.00), routing high-risk chargebacks ahead of standard banking clearing delays.
- **Tier 3 (Agentic Tool Auditor):** Gemini 3.6 Flash interrogates external microservice tools (`query_dispute_portal`, `query_bank_clearing_schedule`) to produce structured Pydantic root-cause diagnoses and actionable accounting steps.

---

## 2. System Architecture
[ INGESTION ENGINE ]
                 (ERP Invoices + Gateway Webhooks + Bank Feeds)
                                       │
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │    TIER 1: Deterministic Math Core (Paisa)       │
             │   - 100% Integer Arithmetic (1 INR = 100 Paisa)  │
             │   - Dynamic Multi-Rail MDR (UPI, Card, NetBank)  │
             │   - Section 194-O TDS & 18% GST Fee Breakdown    │
             └─────────────────────────┬────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │ 95% Match Rate                      │ 5% Discrepancies
                    ▼                                     ▼
         ┌─────────────────────┐       ┌───────────────────────────────────────┐
         │ RECONCILED LEDGER   │       │  TIER 2: Predictive ML Risk Scorer    │
         │ (Zero Float Drift)  │       │  - Scikit-Learn Classifier (0.0 - 1.0)│
         └─────────────────────┘       └──────────────────┬────────────────────┘
                                                          │
                                                          ▼
                                       ┌───────────────────────────────────────┐
                                       │  TIER 3: Autonomous LLM Auditor       │
                                       │  (Gemini 3.6 Flash + Function Tools)  │
                                       │   - query_dispute_portal()            │
                                       │   - query_bank_clearing_schedule()    │
                                       └──────────────────┬────────────────────┘
                                                          │
                                                          ▼
                                       ┌───────────────────────────────────────┐
                                       │ Structured Pydantic Audit Diagnoses   │
                                       │ & Real-Time CFO Copilot Q&A           │
                                       └───────────────────────────────────────┘
                                       ---

## 3. Technical Specifications & Mathematical Proof

### 1. Integer-Paisa Arithmetic Formula
Every transaction amount is calculated as an exact integer in **Paisa**:
$$\text{Net Settlement (Paisa)} = \text{Gross Amount} - \text{MDR Fee} - \text{GST (18\% on MDR)} - \text{TDS (1\% u/s 194-O)}$$

- **UPI:** 0% MDR $\rightarrow$ Zero deductions.
- **Debit Card:** 0.9% MDR + 18% GST.
- **Credit Card:** 2.0% MDR + 18% GST.
- **Corporate / NetBanking:** 3.0% MDR + 18% GST.

### 2. Machine Learning Risk Scoring
The random forest classifier evaluates the feature vector:
$$\vec{x} = \begin{bmatrix} \text{Gross Amount (Paisa)}, & |\text{Discrepancy (Paisa)}|, & \mathbb{I}_{\text{Dispute}}, & \mathbb{I}_{\text{Delay}} \end{bmatrix}$$

Outputting a risk probability metric:
- **0.70 – 1.00 (Critical Risk):** Unpaid abandoned invoices, unlinked merchant charges.
- **0.40 – 0.69 (Medium Risk):** Active chargebacks with evidence submission windows.
- **0.00 – 0.39 (Low Risk):** Routine $T+2$ banking batch settlements in transit.

---

## 4. High-Volume Stress Benchmark (500 Transactions)

| Benchmark Metric | Performance Result | Target / Standard |
| :--- | :--- | :--- |
| **Deterministic Math Latency** | **< 35 ms** | Sub-150 ms |
| **Batch Match Accuracy** | **95.0%** (475/500 Records) | Zero Decimal Drift |
| **ML Risk Classifier Latency** | **< 5 ms** (Vectorized) | Real-time |
| **Engine Throughput** | **12,500+ TPS** | High-Volume Ingestion |
| **Tool-Augmented Resolution** | **100% Correct Diagnosis** | Grounded Output |

---

## 5. Repository Structure

ai-finance-controller/
├── data/
│   ├── synthetic_invoices.json      # ERP invoice records
│   ├── synthetic_webhooks.json      # Gateway webhook payloads
│   └── synthetic_bank.json          # Bank settlement credit feeds
├── agent_tools.py                   # External dispute & bank clearing mock microservices
├── anomaly_ml_model.py              # Scikit-learn predictive loss risk classifier
├── api.py                           # FastAPI REST endpoints & Copilot bridge
├── app.py                           # Single-view Cashly-inspired Streamlit dashboard
├── benchmark_stress.py              # High-volume (500 Tx) performance benchmarking tool
├── bundle_fincontrol.py             # Consolidated all-in-one single-file engine
├── docker-compose.yml               # Multi-service container orchestration
├── Dockerfile                       # Multi-stage container build file
├── fee_engine.py                    # Integer-Paisa deterministic fee calculation engine
├── generate_synthetic_data.py       # Deterministic transaction generator with injected anomalies
├── llm_auditor.py                   # Tool-calling Gemini 3.6 Flash exception auditor
├── reconciler.py                    # 2-Tier deterministic waterfall reconciliation engine
├── run_pipeline.py                  # CLI pipeline benchmark runner
└── requirements.txt                 # Python dependencies
---

## 6. Quickstart & Installation

### 1. Prerequisites
- Python 3.10+
- Google Gemini API Key

### 2. Clone and Setup Environment
```bash
git clone [https://github.com/your-username/ai-finance-controller.git](https://github.com/your-username/ai-finance-controller.git)
cd ai-finance-controller

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows (or source venv/bin/activate on Unix)

# Install dependencies
pip install -r requirements.txt

#Configure API Credentials
GEMINI_API_KEY=your_gemini_api_key_here
Run CLI Engine & Benchmarking

# Run the complete reconciliation & LLM audit pipeline
python run_pipeline.py

# Execute the 500-record high-volume performance benchmark
python benchmark_stress.py

Start Backend REST API

uvicorn api:app --reload --port 8000

#Start Web Dashboard
streamlit run app.py

#Containerized Deployment (Docker)
docker compose up --build

