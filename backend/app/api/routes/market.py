from fastapi import APIRouter

from app.schemas.market import MarketSnapshot
from app.services.market_data import MarketDataService

router = APIRouter(tags=["market"])


@router.get("/market/{symbol}", response_model=MarketSnapshot)
async def get_market_snapshot(symbol: str) -> MarketSnapshot:
    market = MarketDataService()
    snapshot = await market.get_snapshot(symbol)
    return MarketSnapshot(
        symbol=snapshot.symbol,
        last_price=snapshot.last_price,
        day_change_pct=snapshot.day_change_pct,
        timestamp=snapshot.timestamp,
    )
