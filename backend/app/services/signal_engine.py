from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.core.config import settings
from app.services.indicators import IndicatorBundle
from app.services.risk import calculate_risk
from app.services.sentiment import SentimentSnapshot


@dataclass
class SignalDecision:
    signal: str
    confidence: float
    entry_price: float
    stop_loss: float
    target1: float
    target2: float
    rr_ratio: float
    holding_duration: str
    reasoning: str
    sentiment_summary: str
    generated_at: datetime


def generate_signal(
    symbol: str,
    stock_name: str,
    indicators: IndicatorBundle,
    sentiment: SentimentSnapshot,
    last_price: float,
    volume_confirmed: bool,
) -> SignalDecision:
    reasons: list[str] = []
    bullish_signals = 0

    if indicators.rsi < 35:
        bullish_signals += 1
        reasons.append("RSI indicates oversold momentum")
    if indicators.macd > indicators.macd_signal:
        bullish_signals += 1
        reasons.append("MACD bullish crossover")
    if indicators.ema_20 > indicators.ema_50 > indicators.ema_200:
        bullish_signals += 1
        reasons.append("EMA stack supports uptrend")
    if last_price > indicators.vwap:
        bullish_signals += 1
        reasons.append("Price above VWAP")
    if indicators.adx > 20:
        bullish_signals += 1
        reasons.append("Trend strength confirmed by ADX")
    if volume_confirmed:
        bullish_signals += 1
        reasons.append("Volume confirms accumulation")

    risk = calculate_risk(last_price, indicators.atr, sentiment.confidence)

    confidence = min(1.0, 0.15 + bullish_signals * 0.12 + sentiment.score * 0.4)
    confidence = max(0.0, confidence)
    rr_ok = risk.rr_ratio >= 1.8
    sentiment_ok = sentiment.score > 0.05

    if bullish_signals >= 4 and sentiment_ok and rr_ok and confidence >= settings.signal_threshold:
        signal = "BUY"
    elif sentiment.score < -0.2 or indicators.macd < indicators.macd_signal:
        signal = "SELL"
        reasons.append("Momentum weakening; protect gains")
    else:
        signal = "HOLD"

    if not rr_ok:
        reasons.append("Risk/reward below threshold")
    if not sentiment_ok:
        reasons.append("Sentiment lacks confirmation")

    reasoning = "; ".join(reasons) if reasons else "Awaiting clearer confirmation"

    return SignalDecision(
        signal=signal,
        confidence=round(confidence, 3),
        entry_price=last_price,
        stop_loss=risk.stop_loss,
        target1=risk.target1,
        target2=risk.target2,
        rr_ratio=round(risk.rr_ratio, 2),
        holding_duration="5-20 trading days",
        reasoning=reasoning,
        sentiment_summary=sentiment.summary,
        generated_at=datetime.utcnow(),
    )
