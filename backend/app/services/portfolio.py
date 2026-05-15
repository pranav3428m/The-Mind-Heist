from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass
class PortfolioExposure:
    current_exposure: float
    max_exposure: float
    available_capacity: float


def calculate_exposure(positions_value: float, portfolio_value: float) -> PortfolioExposure:
    exposure = positions_value / max(portfolio_value, 1.0)
    max_exposure = settings.max_portfolio_exposure
    available = max(0.0, max_exposure - exposure)
    return PortfolioExposure(
        current_exposure=exposure,
        max_exposure=max_exposure,
        available_capacity=available,
    )
