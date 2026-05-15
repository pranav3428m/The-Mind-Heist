from __future__ import annotations

import pandas as pd


def volume_confirmation(candles: pd.DataFrame) -> bool:
    if candles.empty:
        return False
    if len(candles) < 20:
        return candles["volume"].tail(3).mean() >= candles["volume"].mean()
    recent_volume = candles["volume"].tail(3).mean()
    baseline = candles["volume"].rolling(20).mean().iloc[-1]
    return recent_volume >= baseline * 1.2
