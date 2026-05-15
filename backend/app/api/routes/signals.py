from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, WebSocket

from app.schemas.signals import SignalRequest, SignalResponse
from app.services.discord import send_discord_alert
from app.services.indicators import compute_indicators
from app.services.liquidity import volume_confirmation
from app.services.market_data import MarketDataService
from app.services.sentiment import aggregate_sentiment
from app.services.signal_engine import generate_signal

router = APIRouter(tags=["signals"])


@router.post("/signals", response_model=SignalResponse)
async def create_signal(payload: SignalRequest) -> SignalResponse:
    market = MarketDataService()
    candles = await market.get_candles(payload.symbol, payload.timeframe)
    if candles.empty:
        return SignalResponse(
            stock_name=payload.symbol,
            ticker=payload.symbol,
            signal="HOLD",
            confidence=0.1,
            entry_price=0.0,
            stop_loss=0.0,
            target1=0.0,
            target2=0.0,
            rr_ratio=0.0,
            holding_duration="N/A",
            reasoning="Insufficient data for signal",
            sentiment_summary="No data",
            generated_at=datetime.utcnow(),
        )

    indicators = compute_indicators(candles)
    snapshot = await market.get_snapshot(payload.symbol)
    sentiment = aggregate_sentiment(0.12, 0.08, 0.05, 0.03)

    decision = generate_signal(
        symbol=payload.symbol,
        stock_name=payload.symbol,
        indicators=indicators,
        sentiment=sentiment,
        last_price=snapshot.last_price,
        volume_confirmed=volume_confirmation(candles),
    )

    response = SignalResponse(
        stock_name=payload.symbol,
        ticker=payload.symbol,
        signal=decision.signal,
        confidence=decision.confidence,
        entry_price=decision.entry_price,
        stop_loss=decision.stop_loss,
        target1=decision.target1,
        target2=decision.target2,
        rr_ratio=decision.rr_ratio,
        holding_duration=decision.holding_duration,
        reasoning=decision.reasoning,
        sentiment_summary=decision.sentiment_summary,
        generated_at=decision.generated_at,
    )

    await send_discord_alert(response, payload.timeframe)
    return response


@router.websocket("/signals/stream")
async def signal_stream(ws: WebSocket) -> None:
    await ws.accept()
    await ws.send_json({"message": "Signal stream connected"})
    await ws.close()
