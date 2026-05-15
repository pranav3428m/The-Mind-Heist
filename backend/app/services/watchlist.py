from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WatchlistItem:
    symbol: str
    reason: str
    momentum_score: float


def build_watchlist(candidates: list[WatchlistItem]) -> list[WatchlistItem]:
    return sorted(candidates, key=lambda item: item.momentum_score, reverse=True)
