"""Database repository layer for data persistence."""

import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.utils.logger import setup_logging
from src.utils.config import settings
from src.data.models import Trade, Position

logger = setup_logging(__name__)

Base = declarative_base()


class TradeModel(Base):
    """SQLAlchemy model for trades."""
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True)
    symbol = Column(String)
    side = Column(String)  # BUY or SELL
    quantity = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    entry_time = Column(DateTime)
    exit_time = Column(DateTime, nullable=True)
    status = Column(String)
    pnl = Column(Float)
    pnl_percent = Column(Float)
    strategy = Column(String, nullable=True)


class PortfolioSnapshotModel(Base):
    """SQLAlchemy model for portfolio snapshots."""
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    balance = Column(Float)
    equity = Column(Float)
    total_value = Column(Float)
    open_positions = Column(Integer)
    unrealized_pnl = Column(Float)
    realized_pnl = Column(Float)


class DatabaseRepository:
    """Repository for database operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = None
        self.Session = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize database connection."""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                echo=settings.DATABASE_ECHO,
            )
            self.Session = sessionmaker(bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(self.engine)
            logger.info(f"Database initialized: {self.database_url}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_trade(self, trade: Trade) -> None:
        """Save trade to database."""
        try:
            session = self.Session()
            trade_model = TradeModel(
                id=trade.id,
                symbol=trade.symbol,
                side=trade.side,
                quantity=trade.quantity,
                entry_price=trade.entry_price,
                exit_price=trade.exit_price,
                entry_time=trade.entry_time,
                exit_time=trade.exit_time,
                status=trade.status,
                pnl=trade.pnl,
                pnl_percent=trade.pnl_percent,
                strategy=trade.strategy,
            )
            session.add(trade_model)
            session.commit()
            session.close()
            logger.info(f"Trade saved: {trade.id}")
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")
            raise
    
    def get_trades(
        self,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Trade]:
        """Get trades from database."""
        try:
            session = self.Session()
            query = session.query(TradeModel)
            
            if symbol:
                query = query.filter(TradeModel.symbol == symbol)
            if status:
                query = query.filter(TradeModel.status == status)
            
            results = query.order_by(TradeModel.entry_time.desc()).limit(limit).all()
            session.close()
            
            trades = [
                Trade(
                    id=t.id,
                    symbol=t.symbol,
                    side=t.side,
                    quantity=t.quantity,
                    entry_price=t.entry_price,
                    exit_price=t.exit_price,
                    entry_time=t.entry_time,
                    exit_time=t.exit_time,
                    status=t.status,
                    pnl=t.pnl,
                    pnl_percent=t.pnl_percent,
                    strategy=t.strategy,
                )
                for t in results
            ]
            return trades
        except Exception as e:
            logger.error(f"Failed to get trades: {e}")
            return []
    
    def save_portfolio_snapshot(self, snapshot) -> None:
        """Save portfolio snapshot to database."""
        try:
            session = self.Session()
            snapshot_model = PortfolioSnapshotModel(
                timestamp=snapshot.timestamp,
                balance=snapshot.balance,
                equity=snapshot.equity,
                total_value=snapshot.total_value,
                open_positions=snapshot.open_positions,
                unrealized_pnl=snapshot.unrealized_pnl,
                realized_pnl=snapshot.realized_pnl,
            )
            session.add(snapshot_model)
            session.commit()
            session.close()
            logger.info(f"Portfolio snapshot saved")
        except Exception as e:
            logger.error(f"Failed to save portfolio snapshot: {e}")
            raise
    
    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
