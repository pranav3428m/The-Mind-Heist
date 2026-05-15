from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass
class RiskProfile:
    rr_ratio: float
    position_size: float
    stop_loss: float
    target1: float
    target2: float


def calculate_risk(entry: float, atr: float, confidence: float) -> RiskProfile:
    stop_loss = max(0.0, entry - atr * 1.8)
    target1 = entry + atr * 2.5
    target2 = entry + atr * 4.0
    rr_ratio = (target1 - entry) / max(entry - stop_loss, 0.01)
    position_size = settings.max_position_risk_pct * confidence
    return RiskProfile(
        rr_ratio=rr_ratio,
        position_size=position_size,
        stop_loss=stop_loss,
        target1=target1,
        target2=target2,
    )
