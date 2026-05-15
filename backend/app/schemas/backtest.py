from datetime import date

from pydantic import BaseModel


class BacktestRequest(BaseModel):
    strategy: str
    symbol: str
    start_date: date
    end_date: date


class BacktestResult(BaseModel):
    strategy: str
    symbol: str
    total_return: float
    win_rate: float
    max_drawdown: float
