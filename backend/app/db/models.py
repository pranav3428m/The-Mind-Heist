from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    exchange: Mapped[str] = mapped_column(String(16))
    sector: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Candle(Base):
    __tablename__ = "candles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"))
    timeframe: Mapped[str] = mapped_column(String(16))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)

    instrument: Mapped[Instrument] = relationship("Instrument")


class OrderBookSnapshot(Base):
    __tablename__ = "order_book_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    bid_depth: Mapped[int] = mapped_column(Integer)
    ask_depth: Mapped[int] = mapped_column(Integer)
    bid_volume: Mapped[float] = mapped_column(Float)
    ask_volume: Mapped[float] = mapped_column(Float)
    spread: Mapped[float] = mapped_column(Float)

    instrument: Mapped[Instrument] = relationship("Instrument")


class IndicatorValue(Base):
    __tablename__ = "indicator_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"))
    timeframe: Mapped[str] = mapped_column(String(16))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    indicator: Mapped[str] = mapped_column(String(64))
    value: Mapped[float] = mapped_column(Float)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    source: Mapped[str] = mapped_column(String(64))
    score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    summary: Mapped[str | None] = mapped_column(String(512), nullable=True)


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    signal_type: Mapped[str] = mapped_column(String(16))
    confidence: Mapped[float] = mapped_column(Float)
    entry_price: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    target1: Mapped[float] = mapped_column(Float)
    target2: Mapped[float] = mapped_column(Float)
    rr_ratio: Mapped[float] = mapped_column(Float)
    holding_period_days: Mapped[int] = mapped_column(Integer)
    reasoning: Mapped[str] = mapped_column(String(2000))
    sentiment_summary: Mapped[str] = mapped_column(String(1000))


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    exposure_limit: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"))
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    quantity: Mapped[float] = mapped_column(Float)
    avg_price: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    target1: Mapped[float] = mapped_column(Float)
    target2: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16))


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16))
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    strategy: Mapped[str] = mapped_column(String(128))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    results: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class SignalPerformance(Base):
    __tablename__ = "signal_performance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signal_id: Mapped[int] = mapped_column(ForeignKey("signals.id"))
    outcome: Mapped[str] = mapped_column(String(16))
    pnl: Mapped[float] = mapped_column(Float)
    max_drawdown: Mapped[float] = mapped_column(Float)
    closed_at: Mapped[datetime] = mapped_column(DateTime)
