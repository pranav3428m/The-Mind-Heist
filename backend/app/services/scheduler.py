from __future__ import annotations

import asyncio
import logging

from app.core.config import settings
from app.services.market_data import MarketDataService

logger = logging.getLogger(__name__)


async def poll_market_data(service: MarketDataService, symbols: list[str]) -> None:
    while True:
        try:
            for symbol in symbols:
                await service.get_snapshot(symbol)
        except Exception as exc:  # pragma: no cover - runtime integration
            logger.warning("Market data polling failed: %s", exc)
        await asyncio.sleep(settings.scheduler_poll_seconds)
