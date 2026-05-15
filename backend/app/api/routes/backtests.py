from fastapi import APIRouter

from app.schemas.backtest import BacktestRequest, BacktestResult
from app.services.backtesting import run_backtest
from app.services.market_data import MarketDataService

router = APIRouter(tags=["backtests"])


@router.post("/backtests", response_model=BacktestResult)
async def create_backtest(payload: BacktestRequest) -> BacktestResult:
    market = MarketDataService()
    candles = await market.get_candles(payload.symbol, "1d")
    summary = run_backtest(candles)
    return BacktestResult(
        strategy=payload.strategy,
        symbol=payload.symbol,
        total_return=summary.total_return,
        win_rate=summary.win_rate,
        max_drawdown=summary.max_drawdown,
    )
