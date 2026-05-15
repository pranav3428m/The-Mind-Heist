from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SentimentSnapshot:
    score: float
    confidence: float
    summary: str


def aggregate_sentiment(
    news_score: float,
    social_score: float,
    fear_greed: float,
    sector_rotation: float,
) -> SentimentSnapshot:
    weights = {
        "news": 0.35,
        "social": 0.25,
        "fear_greed": 0.2,
        "sector": 0.2,
    }
    combined = (
        news_score * weights["news"]
        + social_score * weights["social"]
        + fear_greed * weights["fear_greed"]
        + sector_rotation * weights["sector"]
    )
    confidence = min(1.0, 0.4 + abs(combined) * 0.6)
    sentiment_label = "positive" if combined > 0.1 else "negative" if combined < -0.1 else "neutral"
    summary = (
        f"News sentiment {news_score:.2f}, social sentiment {social_score:.2f}, "
        f"fear/greed {fear_greed:.2f}, sector rotation {sector_rotation:.2f}. "
        f"Overall tone is {sentiment_label}."
    )
    return SentimentSnapshot(score=combined, confidence=confidence, summary=summary)
