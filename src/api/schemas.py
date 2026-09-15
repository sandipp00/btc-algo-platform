"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TradeSchema(BaseModel):
    """Trade schema."""
    id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    exit_price: Optional[float] = None
    entry_time: datetime
    exit_time: Optional[datetime] = None
    status: str
    pnl: float
    pnl_percent: float
    strategy: Optional[str] = None
    
    class Config:
        from_attributes = True


class PositionSchema(BaseModel):
    """Position schema."""
    id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    entry_time: datetime
    
    class Config:
        from_attributes = True


class PortfolioSchema(BaseModel):
    """Portfolio schema."""
    balance: float
    equity: float
    total_value: float
    open_positions: int
    unrealized_pnl: float
    realized_pnl: float
    positions: List[PositionSchema] = []
    
    class Config:
        from_attributes = True


class CreateTradeSchema(BaseModel):
    """Schema for creating a trade."""
    symbol: str = Field(..., description="Trading symbol")
    side: str = Field(..., description="BUY or SELL")
    quantity: float = Field(..., gt=0, description="Trade quantity")
    strategy: Optional[str] = None


class BacktestRequestSchema(BaseModel):
    """Schema for backtest request."""
    strategy: str = Field(..., description="Strategy type")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    initial_capital: float = Field(default=10000, gt=0)
    symbol: str = Field(default="BTC/USDT")


class BacktestResultSchema(BaseModel):
    """Schema for backtest result."""
    strategy: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    
    class Config:
        from_attributes = True


class AnalyticsSchema(BaseModel):
    """Analytics schema."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    average_win: float
    average_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float


class HealthCheckSchema(BaseModel):
    """Health check response."""
    status: str
    environment: str
    mode: str
