from fastapi import APIRouter

from app.services.watchlist import WatchlistItem, build_watchlist

router = APIRouter(tags=["watchlist"])


@router.get("/watchlist")
async def get_watchlist() -> list[WatchlistItem]:
    candidates = [
        WatchlistItem(symbol="RELIANCE", reason="Sector momentum", momentum_score=0.82),
        WatchlistItem(symbol="TCS", reason="Breakout setup", momentum_score=0.76),
    ]
    return build_watchlist(candidates)
