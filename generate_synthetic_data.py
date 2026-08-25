import json
import os
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_IN')
random.seed(42)

def generate_datasets(count: int = 60):
    os.makedirs("data", exist_ok=True)
    
    invoices = []
    webhooks = []
    bank_records = []
    
    base_time = datetime(2026, 8, 20, 10, 0, 0)
    
    for i in range(1, count + 1):
        order_id = f"ord_{1000 + i}"
        payment_id = f"pay_{2000 + i}"
        utr = f"UTR{random.randint(100000000000, 999999999999)}"
        
        # Gross amount in Paisa (INR 500 to INR 10,000)
        gross_amount_paisa = random.randint(50000, 1000000)
        created_time = base_time + timedelta(minutes=i * 15)
        
        # Standard fee: 2% MDR, 18% GST on MDR
        mdr_fee_paisa = int(gross_amount_paisa * 0.02)
        gst_paisa = int(mdr_fee_paisa * 0.18)
        net_settled_paisa = gross_amount_paisa - mdr_fee_paisa - gst_paisa

        # 1. Injected Anomaly: Unpaid / Abandoned Invoice
        if i == 15:
            invoices.append({
                "order_id": order_id,
                "gross_amount_paisa": gross_amount_paisa,
                "amount_paisa": gross_amount_paisa,
                "customer_name": fake.name(),
                "created_at": created_time.isoformat(),
                "status": "ISSUED"
            })
            continue

        # 2. Injected Anomaly: Chargeback Dispute Hold (₹500 / 50,000 paisa reserve hold)
        elif i == 25:
            invoices.append({
                "order_id": order_id,
                "gross_amount_paisa": gross_amount_paisa,
                "amount_paisa": gross_amount_paisa,
                "customer_name": fake.name(),
                "created_at": created_time.isoformat(),
                "status": "ISSUED"
            })
            webhooks.append({
                "order_id": order_id,
                "payment_id": payment_id,
                "amount_paisa": gross_amount_paisa,
                "payment_method": "credit_card",
                "captured_at": (created_time + timedelta(minutes=2)).isoformat(),
                "status": "captured"
            })
            bank_records.append({
                "order_id": order_id,
                "payment_id": payment_id,
                "utr": utr,
                "credit_paisa": net_settled_paisa - 50000,
                "settled_at": (created_time + timedelta(hours=24)).isoformat(),
                "status": "SETTLED"
            })
            continue

        # 3. Injected Anomaly: T+2 Banking Settlement Delay
        elif i == 35:
            invoices.append({
                "order_id": order_id,
                "gross_amount_paisa": gross_amount_paisa,
                "amount_paisa": gross_amount_paisa,
                "customer_name": fake.name(),
                "created_at": created_time.isoformat(),
                "status": "ISSUED"
            })
            webhooks.append({
                "order_id": order_id,
                "payment_id": payment_id,
                "amount_paisa": gross_amount_paisa,
                "payment_method": "netbanking",
                "captured_at": (created_time + timedelta(minutes=2)).isoformat(),
                "status": "captured"
            })
            continue

        # Standard Clean Matching Records
        invoices.append({
            "order_id": order_id,
            "gross_amount_paisa": gross_amount_paisa,
            "amount_paisa": gross_amount_paisa,
            "customer_name": fake.name(),
            "created_at": created_time.isoformat(),
            "status": "ISSUED"
        })
        webhooks.append({
            "order_id": order_id,
            "payment_id": payment_id,
            "amount_paisa": gross_amount_paisa,
            "payment_method": "upi",
            "captured_at": (created_time + timedelta(minutes=2)).isoformat(),
            "status": "captured"
        })
        bank_records.append({
            "order_id": order_id,
            "payment_id": payment_id,
            "utr": utr,
            "credit_paisa": net_settled_paisa,
            "settled_at": (created_time + timedelta(hours=12)).isoformat(),
            "status": "SETTLED"
        })

    with open("data/synthetic_invoices.json", "w") as f:
        json.dump(invoices, f, indent=2)
    with open("data/synthetic_webhooks.json", "w") as f:
        json.dump(webhooks, f, indent=2)
    with open("data/synthetic_bank.json", "w") as f:
        json.dump(bank_records, f, indent=2)

if __name__ == "__main__":
    generate_datasets(60)