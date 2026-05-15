from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SignalRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"
    include_explain: bool = True


class SignalResponse(BaseModel):
    stock_name: str
    ticker: str
    signal: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0, le=1)
    entry_price: float
    stop_loss: float
    target1: float
    target2: float
    rr_ratio: float
    holding_duration: str
    reasoning: str
    sentiment_summary: str
    generated_at: datetime
