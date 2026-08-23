import time
import json
from reconciler import ReconciliationEngine
from llm_auditor import LLMFinanceAuditor, AuditReport

def run_benchmark():
    print("=" * 65)
    print("      FinControl AI: Autonomous Reconciliation & Audit Engine    ")
    print("=" * 65)
    
    start_time = time.time()
    
    # 1. Deterministic Reconciliation Pass
    print("\n[1/2] Executing Deterministic Math Core...")
    recon_start = time.time()
    engine = ReconciliationEngine(
        "data/synthetic_invoices.json",
        "data/synthetic_webhooks.json",
        "data/synthetic_bank.json"
    )
    recon_result = engine.run()
    recon_elapsed = (time.time() - recon_start) * 1000  # ms
    
    print(f"      ✓ Processed {recon_result['total_processed']} records in {recon_elapsed:.2f}ms")
    print(f"      ✓ Clean Matches: {recon_result['reconciled_count']}")
    print(f"      ✓ Flagged Exceptions: {recon_result['exception_count']}")
    print(f"      ✓ Match Rate: {recon_result['match_rate_percentage']}%")

    # 2. LLM Exception Auditing Pass
    print("\n[2/2] Running LLM Root-Cause Exception Auditor...")
    llm_start = time.time()
    auditor = LLMFinanceAuditor()
    report: AuditReport = auditor.audit_exceptions(recon_result["exceptions"])
    llm_elapsed = (time.time() - llm_start) * 1000  # ms
    print(f"      ✓ Audited {report.total_exceptions_audited} exceptions in {llm_elapsed:.2f}ms")

    total_elapsed = (time.time() - start_time) * 1000

    # 3. Final Executive Scorecard
    print("\n" + "=" * 65)
    print("                    EXECUTIVE AUDIT SCORECARD                    ")
    print("=" * 65)
    print(f"Total Transactions Processed : {recon_result['total_processed']}")
    print(f"Reconciled with Proof        : {recon_result['reconciled_count']} ({recon_result['match_rate_percentage']}%)")
    print(f"Exceptions Resolved by AI    : {report.total_exceptions_audited}")
    print(f"Total Pipeline Latency       : {total_elapsed:.2f}ms")
    print("-" * 65)
    print("ACTIONABLE EXCEPTION LEDGER:")
    
    for idx, item in enumerate(report.diagnoses, 1):
        print(f"\n{idx}. [{item.order_id}] Category: {item.anomaly_type}")
        print(f"   • Financial Impact : ₹{item.financial_impact_inr:.2f}")
        print(f"   • Root Cause       : {item.root_cause_explanation}")
        print(f"   • Recommended Step : {item.action_item}")
        
    print("\n" + "=" * 65)

if __name__ == "__main__":
    run_benchmark()