from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time

import pytz


@dataclass
class MarketHours:
    open_time: time
    close_time: time


NSE_HOURS = MarketHours(open_time=time(9, 15), close_time=time(15, 30))


def is_market_open(timestamp: datetime, timezone: str = "Asia/Kolkata") -> bool:
    tz = pytz.timezone(timezone)
    localized = timestamp.astimezone(tz)
    if localized.weekday() >= 5:
        return False
    return NSE_HOURS.open_time <= localized.time() <= NSE_HOURS.close_time
