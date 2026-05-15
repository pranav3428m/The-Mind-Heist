from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from app.services.hdfc_client import HdfcClient


@dataclass
class MarketSnapshot:
    symbol: str
    last_price: float
    day_change_pct: float
    timestamp: datetime


class MarketDataService:
    def __init__(self, client: HdfcClient | None = None) -> None:
        self.client = client or HdfcClient()

    async def get_snapshot(self, symbol: str) -> MarketSnapshot:
        payload = await self.client.get_live_price(symbol)
        data = payload.get("data", payload)
        return MarketSnapshot(
            symbol=symbol,
            last_price=float(data.get("last_price", 0.0)),
            day_change_pct=float(data.get("day_change_pct", 0.0)),
            timestamp=datetime.now(timezone.utc),
        )

    async def get_candles(self, symbol: str, timeframe: str) -> pd.DataFrame:
        payload = await self.client.get_candles(symbol, timeframe)
        candles = payload.get("data", [])
        df = pd.DataFrame(candles)
        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    async def get_order_book(self, symbol: str) -> dict:
        payload = await self.client.get_order_book(symbol)
        return payload.get("data", payload)
