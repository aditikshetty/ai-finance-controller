from pydantic import BaseModel, Field
from typing import Optional, Dict

class PaymentMethodFeeRule:
    RATES: Dict[str, float] = {
        "upi": 0.00,             # 0% MDR on UPI
        "debit_card": 0.009,      # 0.9% MDR
        "credit_card": 0.020,    # 2.0% Standard MDR
        "corporate_card": 0.030  # 3.0% Commercial MDR
    }
    GST_RATE: float = 0.18        # 18% GST on MDR
    TDS_194O_RATE: float = 0.01   # 1% TDS on E-commerce Gross

class DynamicFeeCalculator(BaseModel):
    gross_paisa: int
    payment_method: str = "credit_card"
    apply_tds: bool = False

    @property
    def mdr_rate(self) -> float:
        return PaymentMethodFeeRule.RATES.get(self.payment_method.lower(), 0.020)

    @property
    def mdr_paisa(self) -> int:
        return int(round(self.gross_paisa * self.mdr_rate))

    @property
    def gst_paisa(self) -> int:
        return int(round(self.mdr_paisa * PaymentMethodFeeRule.GST_RATE))

    @property
    def tds_paisa(self) -> int:
        if not self.apply_tds:
            return 0
        return int(round(self.gross_paisa * PaymentMethodFeeRule.TDS_194O_RATE))

    @property
    def expected_net_settlement_paisa(self) -> int:
        return self.gross_paisa - self.mdr_paisa - self.gst_paisa - self.tds_paisa

    # Backwards compatibility property
    @property
    def expected_net_paisa(self) -> int:
        return self.expected_net_settlement_paisa

    def verify_settlement(self, actual_net_paisa: int) -> tuple[bool, int]:
        discrepancy = actual_net_paisa - self.expected_net_settlement_paisa
        return discrepancy == 0, discrepancy

# Alias for full backward compatibility
IndianFeeBreakdown = DynamicFeeCalculator

class ReconciledRecord(BaseModel):
    order_id: str
    payment_id: Optional[str] = None
    utr: Optional[str] = None
    gross_paisa: int
    net_settled_paisa: int
    status: str
    discrepancy_paisa: int = 0
    audit_note: str = ""