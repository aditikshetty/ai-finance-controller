import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

from reconciler import ReconciliationEngine
from llm_auditor import LLMFinanceAuditor
from anomaly_ml_model import SettlementRiskModel

load_dotenv()

app = FastAPI(
    title="FinControl AI API",
    description="Autonomous Financial Reconciliation Engine",
    version="1.0.0"
)

risk_model = SettlementRiskModel()

latest_state = {
    "recon_result": None,
    "audit_report": None,
    "tool_traces": []
}

class CopilotChatRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "FinControl AI Engine"}

@app.post("/api/v1/reconcile/run")
def trigger_reconciliation():
    try:
        engine = ReconciliationEngine(
            "data/synthetic_invoices.json",
            "data/synthetic_webhooks.json",
            "data/synthetic_bank.json"
        )
        recon_result = engine.run()
        
        auditor = LLMFinanceAuditor()
        report, traces = auditor.audit_exceptions(recon_result["exceptions"])
        
        diagnoses_with_risk = []
        for d in report.diagnoses:
            d_dict = d.model_dump()
            is_dispute = "CHARGEBACK" in d.anomaly_type
            is_delay = "DELAY" in d.anomaly_type
            d_dict["ml_loss_risk_score"] = risk_model.predict_risk_score(
                gross_paisa=int(d.financial_impact_inr * 100),
                discrepancy_paisa=int(d.financial_impact_inr * 100),
                is_dispute=is_dispute,
                is_delay=is_delay
            )
            diagnoses_with_risk.append(d_dict)

        latest_state["recon_result"] = recon_result
        latest_state["audit_report"] = diagnoses_with_risk
        latest_state["tool_traces"] = traces

        return {
            "status": "SUCCESS",
            "total_processed": recon_result["total_processed"],
            "match_rate_percentage": recon_result["match_rate_percentage"],
            "reconciled_count": recon_result["reconciled_count"],
            "exceptions_count": recon_result["exception_count"],
            "diagnoses": diagnoses_with_risk,
            "tool_traces": traces
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/exceptions/risk-sorted")
def get_risk_sorted_exceptions():
    if not latest_state["audit_report"]:
        raise HTTPException(status_code=400, detail="Run /api/v1/reconcile/run first to populate data.")
    
    sorted_exceptions = sorted(
        latest_state["audit_report"],
        key=lambda x: x["ml_loss_risk_score"],
        reverse=True
    )
    return {"exceptions": sorted_exceptions}

@app.post("/api/v1/copilot/chat")
def ask_finance_copilot(req: CopilotChatRequest):
    if not latest_state["recon_result"]:
        raise HTTPException(status_code=400, detail="Reconciliation batch not initialized.")

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    system_context = f"""
    You are FinControl AI Copilot.
    Reconciliation State:
    - Processed: {latest_state['recon_result']['total_processed']}
    - Match Rate: {latest_state['recon_result']['match_rate_percentage']}%
    - Exceptions:
    {json.dumps(latest_state['audit_report'], indent=2)}
    """
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"{system_context}\n\nQuestion: {req.query}"
    )
    return {"answer": response.text}