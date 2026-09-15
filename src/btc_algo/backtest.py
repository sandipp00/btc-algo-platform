from __future__ import annotations

from dataclasses import dataclass

from .market_data import Candle
from .risk import RiskEngine, RiskState
from .strategy import EmaRsiStrategy


@dataclass(frozen=True)
class BacktestResult:
    initial_equity: float
    final_equity: float
    trades: int
    wins: int
    losses: int
    max_drawdown: float


class Backtester:
    """Deterministic bar-by-bar backtester with fees and risk sizing."""

    def __init__(self, strategy: EmaRsiStrategy, risk: RiskEngine, fee_rate: float) -> None:
        self.strategy = strategy
        self.risk = risk
        self.fee_rate = fee_rate

    def run(self, candles: list[Candle], initial_equity: float) -> BacktestResult:
        if len(candles) < 30:
            raise ValueError("at least 30 candles are required")
        equity = initial_equity
        peak = equity
        day_start = equity
        position = 0.0
        entry = 0.0
        trades = wins = losses = 0
        max_dd = 0.0

        for i in range(30, len(candles)):
            window = candles[: i + 1]
            signal = self.strategy.signal(window)
            price = candles[i].close

            if position == 0 and signal == "buy":
                stop = price * 0.98
                state = RiskState(equity, day_start, peak, 0)
                allowed, _ = self.risk.can_trade(state)
                if allowed:
                    qty = self.risk.position_quantity(equity, price, stop)
                    qty = min(qty, equity / price)
                    position = qty
                    entry = price
                    equity -= qty * price * self.fee_rate
            elif position > 0 and signal == "sell":
                proceeds = position * price
                pnl = position * (price - entry) - proceeds * self.fee_rate
                equity += proceeds + pnl - position * price
                trades += 1
                wins += pnl > 0
                losses += pnl <= 0
                position = 0.0
                entry = 0.0

            mark = equity + position * price
            peak = max(peak, mark)
            max_dd = max(max_dd, (peak - mark) / peak if peak else 0.0)

        if position:
            price = candles[-1].close
            equity += position * price * (1 - self.fee_rate)
            pnl = position * (price - entry)
            trades += 1
            wins += pnl > 0
            losses += pnl <= 0

        return BacktestResult(initial_equity, equity, trades, wins, losses, max_dd)
