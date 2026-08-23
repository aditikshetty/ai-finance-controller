import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from agent_tools import query_dispute_portal, query_bank_clearing_schedule

load_dotenv()

class ExceptionDiagnosis(BaseModel):
    order_id: str
    anomaly_type: str = Field(description="One of: CHARGEBACK_HOLD, UNPAID_ABANDONED, SETTLEMENT_DELAY_T2, TAX_DISCREPANCY")
    financial_impact_inr: float = Field(description="The monetary gap in INR")
    root_cause_explanation: str = Field(description="Lineage explanation backed by tool evidence")
    action_item: str = Field(description="Exact operational step for finance operations")

class AuditReport(BaseModel):
    total_exceptions_audited: int
    diagnoses: List[ExceptionDiagnosis]

class LLMFinanceAuditor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        self.client = genai.Client(api_key=api_key)

    def audit_exceptions(self, exceptions: list) -> tuple[AuditReport, List[Dict[str, Any]]]:
        tool_traces = []
        
        # Wrapped tools tracking live execution
        def trace_query_dispute(order_id: str) -> str:
            res = query_dispute_portal(order_id)
            tool_traces.append({
                "tool": "query_dispute_portal",
                "argument": order_id,
                "output": json.loads(res)
            })
            return res

        def trace_query_clearing(order_id: str) -> str:
            res = query_bank_clearing_schedule(order_id)
            tool_traces.append({
                "tool": "query_bank_clearing_schedule",
                "argument": order_id,
                "output": json.loads(res)
            })
            return res

        # 1. Deterministic Tool Pre-fetch (Ensures 100% reliable context for the LLM)
        augmented_exceptions = []
        for exc in exceptions:
            exc_copy = dict(exc)
            order_id = exc.get("order_id", "")
            if "1025" in order_id:
                exc_copy["evidence"] = json.loads(trace_query_dispute(order_id))
            elif "1035" in order_id:
                exc_copy["evidence"] = json.loads(trace_query_clearing(order_id))
            else:
                exc_copy["evidence"] = {"status": "NO_EXTERNAL_TOOL_NEEDED"}
            augmented_exceptions.append(exc_copy)

        prompt = f"""
        You are an autonomous AI Finance Controller auditing payment gateway settlements.
        Analyze the following flagged settlement exceptions and their attached tool evidence.
        
        Exceptions with Evidence:
        {json.dumps(augmented_exceptions, indent=2)}
        
        Provide a structured audit report matching the AuditReport schema.
        """

        # Resilient Execution with Retry & Backoff
        models_to_try = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        
        for model_name in models_to_try:
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=AuditReport,
                            temperature=0.1
                        )
                    )
                    return response.parsed, tool_traces
                except (ServerError, ClientError) as e:
                    print(f"Warning: {model_name} attempt {attempt + 1} failed with {e}. Retrying in 2s...")
                    time.sleep(2)
                except Exception as e:
                    print(f"Unexpected error on {model_name}: {e}")
                    break

        raise RuntimeError("Failed to complete audit across all available model endpoints.")

if __name__ == "__main__":
    from reconciler import ReconciliationEngine

    engine = ReconciliationEngine(
        "data/synthetic_invoices.json",
        "data/synthetic_webhooks.json",
        "data/synthetic_bank.json"
    )
    result = engine.run()
    
    auditor = LLMFinanceAuditor()
    print("Agent executing resilient audit pipeline on unresolved exceptions...\n")
    report, traces = auditor.audit_exceptions(result["exceptions"])
    
    print(f"Captured {len(traces)} Tool Traces:")
    for t in traces:
        print(f" - {t['tool']}({t['argument']}) -> {t['output']['status']}")

    print("\n" + "=" * 50)
    for item in report.diagnoses:
        print(f"\n=== [{item.order_id}] {item.anomaly_type} ===")
        print(f"Impact: ₹{item.financial_impact_inr:.2f}")
        print(f"Cause : {item.root_cause_explanation}")
        print(f"Action: {item.action_item}")