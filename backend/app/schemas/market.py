from datetime import datetime

from pydantic import BaseModel


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketSnapshot(BaseModel):
    symbol: str
    last_price: float
    day_change_pct: float
    timestamp: datetime
