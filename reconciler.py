import json
import pandas as pd
from fee_engine import IndianFeeBreakdown, ReconciledRecord

class ReconciliationEngine:
    def __init__(self, invoices_path: str, webhooks_path: str, bank_path: str):
        self.invoices_path = invoices_path
        self.webhooks_path = webhooks_path
        self.bank_path = bank_path

    def load_data(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        with open(self.invoices_path, "r") as f:
            invoices = pd.DataFrame(json.load(f))
        with open(self.webhooks_path, "r") as f:
            webhooks = pd.DataFrame(json.load(f))
        with open(self.bank_path, "r") as f:
            bank = pd.DataFrame(json.load(f))
            
        return invoices, webhooks, bank

    def run(self) -> dict:
        invoices_df, webhooks_df, bank_df = self.load_data()
        
        # 1. Merge Invoices with Gateway Webhooks on order_id
        merged_gw = pd.merge(
            invoices_df, 
            webhooks_df, 
            on="order_id", 
            how="left", 
            suffixes=('_inv', '_gw')
        )
        
        # 2. Merge with Bank settlements on order_id
        full_df = pd.merge(
            merged_gw, 
            bank_df, 
            on="order_id", 
            how="left", 
            suffixes=('_gw', '_bank')
        )
        
        reconciled = []
        exceptions = []

        for _, row in full_df.iterrows():
            order_id = row["order_id"]
            gross_paisa = int(row["gross_amount_paisa"])
            payment_id = row.get("payment_id_gw") if pd.notna(row.get("payment_id_gw")) else row.get("payment_id")
            
            # Case 1: Unpaid / Abandoned (No webhook log captured)
            if pd.isna(payment_id):
                exceptions.append({
                    "order_id": order_id,
                    "gross_paisa": gross_paisa,
                    "status": "UNPAID_ABANDONED",
                    "reason": "Invoice exists, but no payment was captured by payment gateway."
                })
                continue
            
            # Case 2: Bank Settlement Pending (T+2 banking delay)
            if pd.isna(row.get("credit_paisa")):
                exceptions.append({
                    "order_id": order_id,
                    "payment_id": payment_id,
                    "gross_paisa": gross_paisa,
                    "status": "PENDING_SETTLEMENT",
                    "reason": "Payment captured by gateway, but deposit has not cleared the bank yet."
                })
                continue

            # Case 3: Verify Settlement Math (MDR + GST formula check)
            actual_credit_paisa = int(row["credit_paisa"])
            fee_validator = IndianFeeBreakdown(gross_paisa=gross_paisa)
            is_match, discrepancy = fee_validator.verify_settlement(actual_credit_paisa)
            
            if is_match:
                reconciled.append(ReconciledRecord(
                    order_id=order_id,
                    payment_id=payment_id,
                    utr=str(row.get("utr", "")),
                    gross_paisa=gross_paisa,
                    net_settled_paisa=actual_credit_paisa,
                    status="RECONCILED",
                    discrepancy_paisa=0,
                    audit_note="Exact match verified against 2% MDR and 18% GST rules."
                ).model_dump())
            else:
                exceptions.append({
                    "order_id": order_id,
                    "payment_id": payment_id,
                    "utr": str(row.get("utr", "")),
                    "gross_paisa": gross_paisa,
                    "actual_credit_paisa": actual_credit_paisa,
                    "expected_credit_paisa": fee_validator.expected_net_paisa,
                    "discrepancy_paisa": discrepancy,
                    "status": "DISCREPANCY_DETECTED",
                    "gateway_notes": row.get("notes", ""),
                    "reason": f"Discrepancy of ₹{abs(discrepancy)/100:.2f} detected between expected and actual settlement."
                })

        total = len(full_df)
        match_rate = (len(reconciled) / total) * 100 if total > 0 else 0

        return {
            "total_processed": total,
            "reconciled_count": len(reconciled),
            "exception_count": len(exceptions),
            "match_rate_percentage": round(match_rate, 2),
            "reconciled_sample": reconciled[:2],
            "exceptions": exceptions
        }

if __name__ == "__main__":
    engine = ReconciliationEngine(
        "data/synthetic_invoices.json",
        "data/synthetic_webhooks.json",
        "data/synthetic_bank.json"
    )
    result = engine.run()
    print("=== RECONCILIATION TEST SUMMARY ===")
    print(f"Total Transactions: {result['total_processed']}")
    print(f"Successfully Reconciled: {result['reconciled_count']}")
    print(f"Flagged Exceptions: {result['exception_count']}")
    print(f"Deterministic Match Rate: {result['match_rate_percentage']}%")
    print("\n--- Flagged Exceptions Details ---")
    print(json.dumps(result["exceptions"], indent=2))