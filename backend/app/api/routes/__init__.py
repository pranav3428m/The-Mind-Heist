from fastapi import APIRouter

from app.api.routes import backtests, health, market, signals, watchlist

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(signals.router)
api_router.include_router(watchlist.router)
api_router.include_router(backtests.router)
api_router.include_router(market.router)
