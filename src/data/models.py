"""Data models for trading entities."""

from datetime import datetime
from typing import Optional
from enum import Enum
from dataclasses import dataclass, asdict
from uuid import uuid4


class TradeStatus(str, Enum):
    """Trade status enum."""
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class OrderSide(str, Enum):
    """Order side enum."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Trade:
    """Represents a single trade."""
    id: str
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    entry_price: float
    exit_price: Optional[float] = None
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    status: str = TradeStatus.OPEN
    pnl: float = 0.0
    pnl_percent: float = 0.0
    strategy: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid4())
        if not self.entry_time:
            self.entry_time = datetime.utcnow()
    
    def close(self, exit_price: float) -> None:
        """Close the trade."""
        self.exit_price = exit_price
        self.exit_time = datetime.utcnow()
        
        if self.side == "BUY":
            self.pnl = (exit_price - self.entry_price) * self.quantity
        else:
            self.pnl = (self.entry_price - exit_price) * self.quantity
        
        self.pnl_percent = (self.pnl / (self.entry_price * self.quantity)) * 100
        self.status = TradeStatus.CLOSED
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Position:
    """Represents an open position."""
    id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    entry_time: datetime
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid4())
    
    def update_price(self, current_price: float) -> None:
        """Update current price and PnL."""
        self.current_price = current_price
        
        if self.side == "BUY":
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity
        
        self.unrealized_pnl_percent = (self.unrealized_pnl / (self.entry_price * self.quantity)) * 100
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PortfolioSnapshot:
    """Snapshot of portfolio state."""
    timestamp: datetime
    balance: float
    equity: float
    total_value: float
    open_positions: int
    unrealized_pnl: float
    realized_pnl: float
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class BacktestResult:
    """Results from backtesting."""
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
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)
