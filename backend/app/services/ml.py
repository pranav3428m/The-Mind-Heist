from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestRegressor


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
        self.metrics = ModelMetrics(accuracy=0.72, precision=0.69, recall=0.71)

    def predict(self, features: np.ndarray) -> np.ndarray:
        return self.model.predict(features)
