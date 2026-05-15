from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

try:
    import talib
except ImportError:  # pragma: no cover - runtime dependency
    talib = None


@dataclass
class IndicatorBundle:
    rsi: float
    macd: float
    macd_signal: float
    ema_20: float
    ema_50: float
    ema_200: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    vwap: float
    fib_38: float
    fib_50: float
    fib_61: float
    supertrend: float
    atr: float
    stoch_rsi: float
    obv: float
    adx: float
    support: float
    resistance: float
    candle_pattern: str | None


def _fallback_rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).iloc[-1]


def compute_indicators(candles: pd.DataFrame) -> IndicatorBundle:
    close = candles["close"]
    high = candles["high"]
    low = candles["low"]
    volume = candles["volume"]

    if talib:
        rsi = talib.RSI(close, timeperiod=14)[-1]
        macd, macd_signal, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        macd_value = macd[-1]
        macd_signal_value = macd_signal[-1]
        ema_20 = talib.EMA(close, timeperiod=20)[-1]
        ema_50 = talib.EMA(close, timeperiod=50)[-1]
        ema_200 = talib.EMA(close, timeperiod=200)[-1]
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
        atr = talib.ATR(high, low, close, timeperiod=14)[-1]
        stoch_rsi = talib.STOCHRSI(close, timeperiod=14)[0][-1]
        obv = talib.OBV(close, volume)[-1]
        adx = talib.ADX(high, low, close, timeperiod=14)[-1]
        candle_pattern = _detect_candlestick(talib, candles)
    else:
        rsi = _fallback_rsi(close)
        macd_value = close.ewm(span=12).mean().iloc[-1] - close.ewm(span=26).mean().iloc[-1]
        macd_signal_value = pd.Series([macd_value]).ewm(span=9).mean().iloc[-1]
        ema_20 = close.ewm(span=20).mean().iloc[-1]
        ema_50 = close.ewm(span=50).mean().iloc[-1]
        ema_200 = close.ewm(span=200).mean().iloc[-1]
        bb_middle = close.rolling(20).mean().iloc[-1]
        bb_std = close.rolling(20).std().iloc[-1]
        bb_upper = bb_middle + 2 * bb_std
        bb_lower = bb_middle - 2 * bb_std
        atr = (high - low).rolling(14).mean().iloc[-1]
        stoch_rsi = ((rsi - 30) / 40) * 100
        obv = (np.sign(close.diff().fillna(0)) * volume).cumsum().iloc[-1]
        adx = 20.0
        candle_pattern = None

    vwap = (close * volume).sum() / volume.sum()

    swing_high = high.max()
    swing_low = low.min()
    fib_38 = swing_high - (swing_high - swing_low) * 0.382
    fib_50 = swing_high - (swing_high - swing_low) * 0.5
    fib_61 = swing_high - (swing_high - swing_low) * 0.618

    supertrend = close.rolling(10).mean().iloc[-1]
    support = low.rolling(20).min().iloc[-1]
    resistance = high.rolling(20).max().iloc[-1]

    return IndicatorBundle(
        rsi=float(rsi),
        macd=float(macd_value),
        macd_signal=float(macd_signal_value),
        ema_20=float(ema_20),
        ema_50=float(ema_50),
        ema_200=float(ema_200),
        bb_upper=float(bb_upper[-1] if hasattr(bb_upper, "__iter__") else bb_upper),
        bb_middle=float(bb_middle[-1] if hasattr(bb_middle, "__iter__") else bb_middle),
        bb_lower=float(bb_lower[-1] if hasattr(bb_lower, "__iter__") else bb_lower),
        vwap=float(vwap),
        fib_38=float(fib_38),
        fib_50=float(fib_50),
        fib_61=float(fib_61),
        supertrend=float(supertrend),
        atr=float(atr),
        stoch_rsi=float(stoch_rsi),
        obv=float(obv),
        adx=float(adx),
        support=float(support),
        resistance=float(resistance),
        candle_pattern=candle_pattern,
    )


def _detect_candlestick(talib_module, candles: pd.DataFrame) -> str | None:
    open_ = candles["open"]
    high = candles["high"]
    low = candles["low"]
    close = candles["close"]

    patterns = {
        "hammer": talib_module.CDLHAMMER,
        "engulfing": talib_module.CDLENGULFING,
        "doji": talib_module.CDLDOJI,
        "morning_star": talib_module.CDLMORNINGSTAR,
        "evening_star": talib_module.CDLEVENINGSTAR,
    }
    for name, func in patterns.items():
        result = func(open_, high, low, close)
        if result[-1] != 0:
            return name
    return None
