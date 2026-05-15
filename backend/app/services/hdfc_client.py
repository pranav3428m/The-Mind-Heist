from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.config import settings

logger = logging.getLogger(__name__)


class HdfcClient:
    def __init__(self) -> None:
        if not settings.hdfc_api_key or not settings.hdfc_api_secret:
            logger.warning("HDFC credentials are not configured")
        self.base_url = settings.hdfc_base_url
        self.headers = {
            "X-API-KEY": settings.hdfc_api_key or "",
            "X-API-SECRET": settings.hdfc_api_secret or "",
            "X-CLIENT-ID": settings.hdfc_client_id or "",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_live_price(self, symbol: str) -> dict[str, Any]:
        return await self._get("/market/price", params={"symbol": symbol})

    async def get_candles(self, symbol: str, timeframe: str = "1d") -> dict[str, Any]:
        return await self._get("/market/candles", params={"symbol": symbol, "timeframe": timeframe})

    async def get_order_book(self, symbol: str) -> dict[str, Any]:
        return await self._get("/market/orderbook", params={"symbol": symbol})

    async def get_positions(self) -> dict[str, Any]:
        return await self._get("/portfolio/positions")

    async def get_instruments(self, universe: str) -> dict[str, Any]:
        return await self._get("/market/instruments", params={"universe": universe})
