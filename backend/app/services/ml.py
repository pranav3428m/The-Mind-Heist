from __future__ import annotations

from dataclasses import dataclass
import logging

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score


@dataclass
class ModelMetrics:
    accuracy: float
    precision: float
    recall: float


class SignalModel:
    def __init__(self) -> None:
        self.model = RandomForestClassifier(n_estimators=200, random_state=42)
        self.metrics = ModelMetrics(accuracy=0.0, precision=0.0, recall=0.0)
        self.logger = logging.getLogger(__name__)

    def train(self, features: np.ndarray, targets: np.ndarray) -> None:
        y_true = (targets > 0).astype(int)
        self.model.fit(features, y_true)
        y_pred = self.model.predict(features).astype(int)
        if len(np.unique(y_true)) < 2:
            self.metrics = ModelMetrics(accuracy=0.0, precision=0.0, recall=0.0)
            self.logger.warning("Insufficient class diversity for metrics computation")
            return
        self.metrics = ModelMetrics(
            accuracy=float(accuracy_score(y_true, y_pred)),
            precision=float(precision_score(y_true, y_pred, zero_division=0)),
            recall=float(recall_score(y_true, y_pred, zero_division=0)),
        )

    def predict(self, features: np.ndarray) -> np.ndarray:
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(features)[:, 1]
        return self.model.predict(features)
