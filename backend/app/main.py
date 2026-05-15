from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI

from app.api.routes import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.market_data import MarketDataService
from app.services.scheduler import poll_market_data

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting %s", settings.app_name)
    market = MarketDataService()
    symbols = ["RELIANCE", "TCS", "INFY"]
    asyncio.create_task(poll_market_data(market, symbols))
