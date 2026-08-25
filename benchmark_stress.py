import time
import os
from generate_synthetic_data import generate_datasets
from reconciler import ReconciliationEngine
from anomaly_ml_model import SettlementRiskModel

def run_stress_benchmark(volume: int = 500):
    print("=" * 65)
    print(f"   STRESS BENCHMARK: High-Throughput Tier-1 Math Engine ({volume} Tx)")
    print("=" * 65)

    # 1. Generate 500 synthetic enterprise transactions
    print(f"\n[1/3] Generating {volume} synthetic enterprise transactions...")
    generate_datasets(volume)

    # 2. Benchmark Integer-Paisa Deterministic Reconciliation Core
    print("[2/3] Executing Integer-Paisa Deterministic Reconciliation...")
    engine = ReconciliationEngine(
        "data/synthetic_invoices.json",
        "data/synthetic_webhooks.json",
        "data/synthetic_bank.json"
    )
    
    start_recon = time.perf_counter()
    result = engine.run()
    recon_duration_ms = (time.perf_counter() - start_recon) * 1000

    # 3. Benchmark ML Risk Scoring
    print("[3/3] Executing Scikit-Learn Anomaly Risk Classifier...")
    risk_model = SettlementRiskModel()
    start_ml = time.perf_counter()
    for exc in result["exceptions"]:
        gross_p = exc.get("amount_paisa") or exc.get("gross_amount_paisa") or 100000
        risk_model.predict_risk_score(
            gross_paisa=gross_p,
            discrepancy_paisa=gross_p,
            is_dispute=True,
            is_delay=False
        )
    ml_duration_ms = (time.perf_counter() - start_ml) * 1000

    throughput_tps = volume / (recon_duration_ms / 1000)

    print("\n" + "=" * 65)
    print("                BENCHMARK SCORECARD")
    print("=" * 65)
    print(f"  • Processed Volume       : {result['total_processed']} Transactions")
    print(f"  • Reconciled Matches     : {result['reconciled_count']} Records")
    print(f"  • Flagged Exceptions     : {result['exception_count']} Anomalies")
    print(f"  • Match Rate Accuracy    : {result['match_rate_percentage']}%")
    print(f"  • Math Core Latency      : {recon_duration_ms:.2f} ms")
    print(f"  • ML Risk Latency        : {ml_duration_ms:.2f} ms")
    print(f"  • Engine Throughput      : {throughput_tps:,.0f} Transactions / Second")
    print("=" * 65)

    # Reset synthetic data back to default 60 transactions for UI demo
    print("\nResetting dataset back to 60 records for interactive UI demo...")
    generate_datasets(60)
    print("✓ Reset complete.\n")

if __name__ == "__main__":
    run_stress_benchmark(500)