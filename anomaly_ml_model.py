import numpy as np
from sklearn.ensemble import RandomForestClassifier

class SettlementRiskModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self._train_baseline()

    def _train_baseline(self):
        # Feature Matrix: [Gross Paisa, Discrepancy Paisa, Has Dispute Flag (0/1), Has Delay Flag (0/1)]
        X_train = np.array([
            [100000, 0, 0, 0],      # Clean match (Low risk)
            [220340, 0, 0, 1],      # T+2 Clearing delay (Low risk / temporary)
            [342448, 342448, 0, 0], # Unpaid abandoned cart (High risk / uncollectable)
            [480746, 50000, 1, 0],  # Active chargeback dispute (High risk)
            [500000, 20000, 1, 0],  # Large dispute reserve (High risk)
            [150000, 0, 0, 0],      # Normal settlement (Low risk)
        ])
        y_train = np.array([0, 0, 1, 1, 1, 0])
        self.model.fit(X_train, y_train)

    def predict_risk_score(self, gross_paisa: int, discrepancy_paisa: int, is_dispute: bool, is_delay: bool) -> float:
        features = np.array([[
            gross_paisa,
            abs(discrepancy_paisa),
            1 if is_dispute else 0,
            1 if is_delay else 0
        ]])
        loss_prob = self.model.predict_proba(features)[0][1]
        return round(float(loss_prob), 2)