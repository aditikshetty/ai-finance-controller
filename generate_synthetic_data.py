import json
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('en_IN')
random.seed(42)

def generate_datasets(num_records=60):
    invoices = []
    webhooks = []
    bank_lines = []
    
    base_time = datetime.now() - timedelta(days=5)

    for i in range(1, num_records + 1):
        order_id = f"ord_{1000 + i}"
        payment_id = f"pay_{2000 + i}"
        gross_rupees = round(random.uniform(500, 5000), 2)
        gross_paisa = int(round(gross_rupees * 100))
        tx_time = base_time + timedelta(hours=i)
        
        # 1. Invoice Record
        invoices.append({
            "order_id": order_id,
            "customer_name": fake.name(),
            "gross_amount_paisa": gross_paisa,
            "created_at": tx_time.isoformat()
        })
        
        # Intentional Anomaly Injections for Hackathon Benchmark
        if i == 15:
            # Case 1: Unpaid Abandoned Order (Invoice exists, no webhook, no bank credit)
            continue
        elif i == 25:
            # Case 2: Chargeback dispute (₹500 / 50000 paisa reserve deduction)
            mdr_paisa = int(round(gross_paisa * 0.02))
            gst_paisa = int(round(mdr_paisa * 0.18))
            hold_paisa = 50000
            net_paisa = gross_paisa - mdr_paisa - gst_paisa - hold_paisa
            
            webhooks.append({
                "order_id": order_id,
                "payment_id": payment_id,
                "gross_paisa": gross_paisa,
                "mdr_paisa": mdr_paisa,
                "gst_paisa": gst_paisa,
                "status": "captured",
                "notes": "Chargeback dispute initiated on item; reserve withheld"
            })
            bank_lines.append({
                "utr": f"UTR_ICICI_{5000 + i}",
                "payment_id": payment_id,
                "order_id": order_id,
                "credit_paisa": net_paisa,
                "settled_at": (tx_time + timedelta(days=1)).isoformat()
            })
        elif i == 35:
            # Case 3: T+2 Weekend Settlement Delay (Webhook exists, Bank credit pending)
            mdr_paisa = int(round(gross_paisa * 0.02))
            gst_paisa = int(round(mdr_paisa * 0.18))
            webhooks.append({
                "order_id": order_id,
                "payment_id": payment_id,
                "gross_paisa": gross_paisa,
                "mdr_paisa": mdr_paisa,
                "gst_paisa": gst_paisa,
                "status": "captured",
                "notes": "Transaction pending weekend bank settlement window"
            })
        else:
            # Standard Clean Transaction: Gross - 2% MDR - 18% GST
            mdr_paisa = int(round(gross_paisa * 0.02))
            gst_paisa = int(round(mdr_paisa * 0.18))
            net_paisa = gross_paisa - mdr_paisa - gst_paisa
            
            webhooks.append({
                "order_id": order_id,
                "payment_id": payment_id,
                "gross_paisa": gross_paisa,
                "mdr_paisa": mdr_paisa,
                "gst_paisa": gst_paisa,
                "status": "captured",
                "notes": "Standard clearance"
            })
            bank_lines.append({
                "utr": f"UTR_ICICI_{5000 + i}",
                "payment_id": payment_id,
                "order_id": order_id,
                "credit_paisa": net_paisa,
                "settled_at": (tx_time + timedelta(days=1)).isoformat()
            })

    # Write files to the data/ directory
    with open("data/synthetic_invoices.json", "w") as f:
        json.dump(invoices, f, indent=2)
    with open("data/synthetic_webhooks.json", "w") as f:
        json.dump(webhooks, f, indent=2)
    with open("data/synthetic_bank.json", "w") as f:
        json.dump(bank_lines, f, indent=2)
        
    print(f" Successfully generated:")
    print(f" - data/synthetic_invoices.json ({len(invoices)} records)")
    print(f" - data/synthetic_webhooks.json ({len(webhooks)} records)")
    print(f" - data/synthetic_bank.json ({len(bank_lines)} records)")

if __name__ == "__main__":
    generate_datasets(60)