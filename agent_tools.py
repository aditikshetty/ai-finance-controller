import json

# Mock external microservices / DBs that the agent queries via tool calling

DISPUTE_DATABASE = {
    "ord_1025": {
        "dispute_id": "DSP_RAZORPAY_8832",
        "reason": "Damaged goods reported by buyer",
        "reserve_hold_paisa": 50000,
        "status": "EVIDENCE_REQUIRED",
        "deadline_hours": 72
    }
}

BANK_CLEARING_SCHEDULE = {
    "ord_1035": {
        "channel": "NEFT_BATCH_4",
        "gateway_capture_time": "2026-08-22T23:30:00",
        "clearing_window": "T+2 Business Days",
        "expected_deposit_date": "2026-08-25T09:00:00",
        "bank_status": "PROCESSING_IN_NEXT_CLEARING_CYCLE"
    }
}

def query_dispute_portal(order_id: str) -> str:
    """Tool: Query the Razorpay Dispute & Chargeback API for active customer claims."""
    record = DISPUTE_DATABASE.get(order_id)
    if record:
        return json.dumps({"status": "FOUND", "data": record})
    return json.dumps({"status": "NOT_FOUND", "message": f"No active dispute on {order_id}."})

def query_bank_clearing_schedule(order_id: str) -> str:
    """Tool: Check inter-bank NEFT/RTGS batch settlement clearing schedules and T+2 windows."""
    record = BANK_CLEARING_SCHEDULE.get(order_id)
    if record:
        return json.dumps({"status": "FOUND", "data": record})
    return json.dumps({"status": "NOT_FOUND", "message": f"No scheduled clearing delay found for {order_id}."})