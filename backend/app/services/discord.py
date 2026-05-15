from __future__ import annotations

from datetime import datetime

import httpx

from app.core.config import settings
from app.schemas.signals import SignalResponse


def format_discord_message(signal: SignalResponse, timeframe: str) -> str:
    return (
        "------------------------------------------------\n"
        "🚀 AI STOCK SIGNAL ALERT\n\n"
        f"Stock: {signal.stock_name}\n"
        f"Symbol: {signal.ticker}\n\n"
        f"Signal: {signal.signal}\n"
        f"Confidence: {signal.confidence * 100:.2f}%\n\n"
        f"Entry: ₹{signal.entry_price:.2f}\n"
        f"Stop Loss: ₹{signal.stop_loss:.2f}\n\n"
        "Targets:\n"
        f"🎯 T1: ₹{signal.target1:.2f}\n"
        f"🎯 T2: ₹{signal.target2:.2f}\n\n"
        f"Risk/Reward: {signal.rr_ratio:.2f}\n\n"
        "Market Sentiment:\n"
        f"{signal.sentiment_summary}\n\n"
        "AI Reasoning:\n"
        f"{signal.reasoning}\n\n"
        f"Timeframe: {timeframe}\n\n"
        "Generated At:\n"
        f"{datetime.utcnow().isoformat()}\n"
        "------------------------------------------------"
    )


async def send_discord_alert(signal: SignalResponse, timeframe: str) -> None:
    if not settings.discord_webhook_url:
        return
    message = format_discord_message(signal, timeframe)
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(settings.discord_webhook_url, json={"content": message})
