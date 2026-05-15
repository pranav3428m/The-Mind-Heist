from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score


@dataclass
class ModelMetrics:
    accuracy: float
    precision: float
    recall: float


class SignalModel:
    def __init__(self) -> None:
        self.model = RandomForestRegressor(n_estimators=200, random_state=42)
        self.metrics = ModelMetrics(accuracy=0.0, precision=0.0, recall=0.0)

    def train(self, features: np.ndarray, targets: np.ndarray) -> None:
        self.model.fit(features, targets)
        predictions = self.model.predict(features)
        y_true = (targets > 0).astype(int)
        y_pred = (predictions > 0).astype(int)
        if len(np.unique(y_true)) < 2:
            self.metrics = ModelMetrics(accuracy=0.0, precision=0.0, recall=0.0)
            return
        self.metrics = ModelMetrics(
            accuracy=float(accuracy_score(y_true, y_pred)),
            precision=float(precision_score(y_true, y_pred, zero_division=0)),
            recall=float(recall_score(y_true, y_pred, zero_division=0)),
        )

    def predict(self, features: np.ndarray) -> np.ndarray:
        return self.model.predict(features)
