"""Backtesting engine for strategy validation."""

import logging
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

from src.utils.logger import setup_logging
from src.core.strategy import StrategyFactory
from src.core.risk import RiskManager

logger = setup_logging(__name__)


class BacktestEngine:
    """Engine for backtesting trading strategies on historical data."""
    
    def __init__(
        self,
        strategy_type: str,
        initial_capital: float,
        symbol: str,
        timeframe: str,
    ):
        self.strategy_type = strategy_type
        self.initial_capital = initial_capital
        self.symbol = symbol
        self.timeframe = timeframe
        
        self.strategy = StrategyFactory.create_strategy(strategy_type, timeframe)
        self.risk_manager = RiskManager(initial_capital)
        
        self.results = {
            "trades": [],
            "equity_curve": [],
            "metrics": {},
        }
    
    def run(
        self,
        historical_data: List[Tuple],
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> Dict:
        """Run backtest on historical data."""
        logger.info(f"Starting backtest: {self.strategy_type} on {self.symbol}")
        
        try:
            equity_curve = [self.initial_capital]
            trades = []
            
            # Process each candle
            for i, candle in enumerate(historical_data):
                # Get signal from strategy
                signal = self.strategy.analyze(historical_data[:i+1])
                
                if signal == "BUY" and self.risk_manager.check_constraints():
                    # Execute buy
                    trades.append({
                        "type": "BUY",
                        "price": candle[4],  # close price
                        "time": candle[0],
                    })
                    self.risk_manager.open_position()
                
                elif signal == "SELL" and len(trades) > 0 and trades[-1]["type"] == "BUY":
                    # Execute sell
                    entry_price = trades[-1]["price"]
                    exit_price = candle[4]
                    pnl = (exit_price - entry_price) * 100  # Assuming 100 units
                    
                    trades.append({
                        "type": "SELL",
                        "price": exit_price,
                        "time": candle[0],
                        "pnl": pnl,
                    })
                    
                    self.risk_manager.record_trade(pnl)
                    self.risk_manager.close_position()
                
                # Track equity
                equity_curve.append(self.risk_manager.current_equity)
            
            # Calculate metrics
            metrics = self._calculate_metrics(equity_curve, trades)
            
            self.results = {
                "trades": trades,
                "equity_curve": equity_curve,
                "metrics": metrics,
            }
            
            logger.info(f"Backtest completed: {metrics}")
            return self.results
        
        except Exception as e:
            logger.error(f"Backtest failed: {e}", exc_info=True)
            raise
    
    def _calculate_metrics(self, equity_curve: List[float], trades: List[Dict]) -> Dict:
        """Calculate backtest performance metrics."""
        if len(equity_curve) < 2:
            return {}
        
        initial = equity_curve[0]
        final = equity_curve[-1]
        
        # Total return
        total_return = (final - initial) / initial
        
        # Max drawdown
        max_equity = initial
        max_drawdown = 0
        for equity in equity_curve:
            if equity > max_equity:
                max_equity = equity
            drawdown = 1 - (equity / max_equity)
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Winning trades
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("pnl", 0) < 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        total_trades = len([t for t in trades if t["type"] == "SELL"])
        
        return {
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "final_equity": final,
        }
    
    def get_results(self) -> Dict:
        """Get backtest results."""
        return self.results
