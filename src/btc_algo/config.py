from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TradingMode(StrEnum):
    BACKTEST = "backtest"
    PAPER = "paper"
    TESTNET = "testnet"
    LIVE = "live"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mode: TradingMode = TradingMode.PAPER
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    initial_capital: float = Field(10_000, gt=0)
    risk_per_trade: float = Field(0.01, gt=0, le=0.05)
    max_daily_loss: float = Field(0.03, gt=0, le=1)
    max_drawdown: float = Field(0.10, gt=0, le=1)
    max_positions: int = Field(3, ge=1)
    fee_rate: float = Field(0.001, ge=0)
    slippage_rate: float = Field(0.0005, ge=0)
    exchange_api_key: str = ""
    exchange_api_secret: str = ""
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/btc_algo"
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = Field(8000, ge=1, le=65535)
    log_level: str = "INFO"
    enable_live_trading: bool = False
    strategy: str = "ema_rsi"

    def validate_live_gate(self) -> None:
        if self.mode is TradingMode.LIVE and not self.enable_live_trading:
            raise RuntimeError("LIVE mode requires ENABLE_LIVE_TRADING=true")
        if self.mode is TradingMode.LIVE and (not self.exchange_api_key or not self.exchange_api_secret):
            raise RuntimeError("LIVE mode requires exchange API credentials")
