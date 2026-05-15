# Mind Heist AI Stock Signal Backend

Production-ready backend scaffold for an AI-powered stock signal finder focused on NSE/BSE swing and medium-term trades. This service does **not** guarantee profits; it prioritises risk-adjusted signals with confidence scoring.

## Architecture

- **Data Ingestion**: `services/hdfc_client.py`, `services/market_data.py`
- **Feature/Indicator Engine**: `services/indicators.py`
- **Sentiment & Market Emotion**: `services/sentiment.py`
- **Signal Engine**: `services/signal_engine.py`
- **Risk Engine**: `services/risk.py`
- **ML Pipeline**: `services/ml.py`
- **Backtesting**: `services/backtesting.py`
- **Notification**: `services/discord.py`
- **API Layer**: `app/main.py`, `api/routes/*`
- **Storage**: SQLAlchemy models in `db/models.py`
- **Cache/Queue**: Redis (configured via `REDIS_URL`)

## Database Schema (Core Tables)

- `instruments`, `candles`, `order_book_snapshots`
- `indicator_values`, `sentiment_scores`, `signals`
- `positions`, `portfolios`, `model_registry`
- `backtest_runs`, `signal_performance`

## Setup

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up --build
```

## API Endpoints (v1)

- `GET /api/v1/health`
- `POST /api/v1/signals`
- `GET /api/v1/watchlist`
- `POST /api/v1/backtests`
- `GET /api/v1/market/{symbol}`
- `WS  /api/v1/signals/stream`

## Discord Alerts

Alerts use the required format in `services/discord.py`. Configure `DISCORD_WEBHOOK_URL` to enable.

## Notes

- Configure HDFC Sky/Demat credentials before enabling live trading.
- Use the ML pipeline to track signal accuracy and adapt weights over time.
- Validate signals with backtests and paper trading before capital deployment.
