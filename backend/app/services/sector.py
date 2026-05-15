from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SectorMomentum:
    sector: str
    score: float


def rank_sectors(scores: dict[str, float]) -> list[SectorMomentum]:
    return [SectorMomentum(sector=k, score=v) for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)]
