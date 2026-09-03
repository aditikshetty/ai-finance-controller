import os
import json
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables (.env)
load_dotenv()

# Import the core engine modules
from reconciler import ReconciliationEngine
from llm_auditor import LLMAuditor

# 1. Instantiate FastAPI App
app = FastAPI(
    title="FinControl AI — Autonomous Finance Controller",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Instantiate Engine Instances
recon_engine = ReconciliationEngine(
    invoices_path="data/synthetic_invoices.json",
    webhooks_path="data/synthetic_webhooks.json",
    bank_path="data/synthetic_bank.json"
)
auditor = LLMAuditor()

# 3. Instantiate Gemini Client
api_key = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key) if api_key else None

# In-memory store for live batch reconciliation state
latest_reconciliation_context: Dict[str, Any] = {}


@app.get("/")
def health_check():
    return {
        "status": "ACTIVE",
        "engine": "FinControl AI Hybrid Reconciler",
        "gemini_connected": client is not None
    }


@app.post("/api/v1/reconcile/run")
def run_reconciliation():
    global latest_reconciliation_context

    # Step 1: Run Tier-1 Integer-Paisa Reconciliation Core
    recon_result = recon_engine.run()

    # Step 2: Run Tier-2 (ML Scoring) + Tier-3 (Agentic LLM Tool Auditor)
    audit_result = auditor.audit_exceptions(recon_result["exceptions"])

    # Step 3: Cache live run state for dynamic Copilot context
    latest_reconciliation_context = {
        "total_processed": recon_result["total_processed"],
        "reconciled_count": recon_result["reconciled_count"],
        "exceptions_count": recon_result["exception_count"],
        "match_rate_percentage": recon_result["match_rate_percentage"],
        "diagnoses": audit_result["diagnoses"],
        "tool_traces": audit_result["tool_traces"]
    }

    return latest_reconciliation_context


@app.post("/api/v1/copilot/chat")
def copilot_chat(payload: dict):
    query = payload.get("query", "")
    if not query:
        return {"answer": "Please provide a financial query."}

    # If reconciliation hasn't been executed yet, run a fresh cycle
    global latest_reconciliation_context
    if not latest_reconciliation_context:
        run_reconciliation()

    context_str = json.dumps(latest_reconciliation_context, indent=2)

    prompt = f"""
You are FinControl Copilot, an autonomous and accounting controller assistant.
Answer the user's question accurately using ONLY the live reconciliation and exception ledger data provided below.

LIVE RECONCILIATION CONTEXT:
{context_str}

USER QUERY:
{query}

INSTRUCTIONS:
1. Provide exact INR amounts (₹) and reference Paisa-level precision where relevant.
2. Break down anomalies by Order ID, Root Cause, ML Risk Score, and Prescribed Action Items.
3. Keep the tone concise, professional, and audit-ready.
"""

    if client:
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1
                )
            )
            return {"answer": response.text}
        except Exception as e:
            return {
                "answer": f"Gemini API request failed ({str(e)}). Total unhandled exceptions in ledger: {latest_reconciliation_context.get('exceptions_count', 0)}."
            }
    else:
        # Fallback if GEMINI_API_KEY is missing
        return {
            "answer": "GEMINI_API_KEY is not configured in .env. Live context shows "
                      f"{latest_reconciliation_context.get('exceptions_count', 0)} flagged exceptions."
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)