"""API routes for trading operations."""

import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Query

from src.utils.logger import setup_logging
from src.api.schemas import (
    TradeSchema,
    PositionSchema,
    PortfolioSchema,
    CreateTradeSchema,
    BacktestRequestSchema,
    BacktestResultSchema,
    AnalyticsSchema,
)
from src.core.engine import TradingEngine
from src.data.cache import CacheManager

logger = setup_logging(__name__)

router = APIRouter(tags=["Trading"])

# Global references (set by main.py)
trading_engine: TradingEngine = None
cache_manager: CacheManager = None


def set_engine(engine: TradingEngine, cache: CacheManager) -> None:
    """Set global trading engine and cache references."""
    global trading_engine, cache_manager
    trading_engine = engine
    cache_manager = cache


@router.get("/trades", response_model=List[TradeSchema])
async def get_trades(
    symbol: str = Query(None, description="Filter by symbol"),
    status: str = Query(None, description="Filter by status"),
    limit: int = Query(100, le=500),
):
    """Get trades with optional filtering."""
    try:
        if not trading_engine:
            raise HTTPException(status_code=503, detail="Trading engine not initialized")
        
        trades = trading_engine.get_trades()
        
        # Apply filters
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        if status:
            trades = [t for t in trades if t.status == status]
        
        return trades[:limit]
    except Exception as e:
        logger.error(f"Error fetching trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/{trade_id}", response_model=TradeSchema)
async def get_trade(trade_id: str):
    """Get trade by ID."""
    try:
        if not trading_engine:
            raise HTTPException(status_code=503, detail="Trading engine not initialized")
        
        trades = [t for t in trading_engine.get_trades() if t.id == trade_id]
        if not trades:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        return trades[0]
    except Exception as e:
        logger.error(f"Error fetching trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trades", response_model=TradeSchema)
async def create_trade(trade_data: CreateTradeSchema):
    """Create a new trade."""
    try:
        if not trading_engine:
            raise HTTPException(status_code=503, detail="Trading engine not initialized")
        
        if trade_data.side.upper() == "BUY":
            trade = await trading_engine.execute_buy_order(trade_data.quantity)
        elif trade_data.side.upper() == "SELL":
            trade = await trading_engine.execute_sell_order(trade_data.quantity)
        else:
            raise ValueError(f"Invalid side: {trade_data.side}")
        
        return trade
    except Exception as e:
        logger.error(f"Error creating trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio", response_model=PortfolioSchema)
async def get_portfolio():
    """Get current portfolio state."""
    try:
        if not trading_engine:
            raise HTTPException(status_code=503, detail="Trading engine not initialized")
        
        portfolio = trading_engine.get_portfolio()
        positions = trading_engine.get_positions()
        
        return PortfolioSchema(
            balance=portfolio.get("balance", 0),
            equity=portfolio.get("equity", 0),
            total_value=portfolio.get("equity", 0),
            open_positions=len(positions),
            unrealized_pnl=sum([p.unrealized_pnl for p in positions]),
            realized_pnl=0,
            positions=[PositionSchema(**p.__dict__) for p in positions],
        )
    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/positions", response_model=List[PositionSchema])
async def get_positions():
    """Get open positions."""
    try:
        if not trading_engine:
            raise HTTPException(status_code=503, detail="Trading engine not initialized")
        
        positions = trading_engine.get_positions()
        return [PositionSchema(**p.__dict__) for p in positions]
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/performance", response_model=AnalyticsSchema)
async def get_analytics():
    """Get performance analytics."""
    try:
        if not trading_engine:
            raise HTTPException(status_code=503, detail="Trading engine not initialized")
        
        trades = trading_engine.get_trades()
        closed_trades = [t for t in trades if t.status == "CLOSED"]
        
        if not closed_trades:
            return AnalyticsSchema(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                total_pnl=0,
                average_win=0,
                average_loss=0,
                profit_factor=0,
                max_drawdown=0,
                sharpe_ratio=0,
            )
        
        winning = [t for t in closed_trades if t.pnl > 0]
        losing = [t for t in closed_trades if t.pnl < 0]
        
        total_pnl = sum([t.pnl for t in closed_trades])
        avg_win = sum([t.pnl for t in winning]) / len(winning) if winning else 0
        avg_loss = abs(sum([t.pnl for t in losing]) / len(losing)) if losing else 0
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        return AnalyticsSchema(
            total_trades=len(closed_trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=len(winning) / len(closed_trades) if closed_trades else 0,
            total_pnl=total_pnl,
            average_win=avg_win,
            average_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=0,  # Simplified
            sharpe_ratio=0,  # Simplified
        )
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
