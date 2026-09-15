from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLimits:
    risk_per_trade: float
    max_daily_loss: float
    max_drawdown: float
    max_positions: int


@dataclass
class RiskState:
    equity: float
    day_start_equity: float
    peak_equity: float
    open_positions: int = 0

    @property
    def daily_loss_fraction(self) -> float:
        return max(0.0, (self.day_start_equity - self.equity) / self.day_start_equity)

    @property
    def drawdown_fraction(self) -> float:
        return max(0.0, (self.peak_equity - self.equity) / self.peak_equity)


class RiskEngine:
    def __init__(self, limits: RiskLimits) -> None:
        self.limits = limits

    def can_trade(self, state: RiskState) -> tuple[bool, str]:
        if state.daily_loss_fraction >= self.limits.max_daily_loss:
            return False, "daily_loss_limit"
        if state.drawdown_fraction >= self.limits.max_drawdown:
            return False, "max_drawdown"
        if state.open_positions >= self.limits.max_positions:
            return False, "max_positions"
        return True, "ok"

    def position_quantity(self, equity: float, entry: float, stop: float) -> float:
        if equity <= 0 or entry <= 0 or stop <= 0:
            raise ValueError("equity, entry and stop must be positive")
        risk_budget = equity * self.limits.risk_per_trade
        risk_per_unit = abs(entry - stop)
        if risk_per_unit == 0:
            raise ValueError("entry and stop cannot be equal")
        return risk_budget / risk_per_unit
