from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MindHeistSignals"
    env: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    db_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/mindheist_signals"
    redis_url: str = "redis://localhost:6379/0"

    discord_webhook_url: str | None = None

    hdfc_base_url: str = "https://api.hdfcsky.com"
    hdfc_api_key: str | None = None
    hdfc_api_secret: str | None = None
    hdfc_client_id: str | None = None
    hdfc_account_id: str | None = None

    market_timezone: str = "Asia/Kolkata"
    scheduler_poll_seconds: int = 60
    signal_threshold: float = 0.72

    max_portfolio_exposure: float = 0.6
    max_position_risk_pct: float = 0.02

    default_universe: str = "NIFTY50"
    holding_duration_days_min: int = 5
    holding_duration_days_max: int = 20


settings = Settings()
