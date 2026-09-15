from dataclasses import dataclass
from decimal import Decimal

from btc_algo.domain import OrderSide


@dataclass
class Position:
    symbol: str
    side: OrderSide
    quantity: Decimal
    average_entry: Decimal
    realized_pnl: Decimal = Decimal("0")

    def apply_fill(self, side: OrderSide, quantity: Decimal, price: Decimal, fee: Decimal = Decimal("0")) -> None:
        if quantity <= 0 or price <= 0:
            raise ValueError("quantity and price must be positive")
        signed = quantity if side is OrderSide.BUY else -quantity
        current = self.quantity if self.side is OrderSide.BUY else -self.quantity
        if current == 0:
            self.side = side
            self.quantity = quantity
            self.average_entry = price
            return
        if (current > 0) == (signed > 0):
            new_abs = abs(current + signed)
            self.average_entry = ((abs(current) * self.average_entry) + (quantity * price)) / new_abs
            self.quantity = new_abs if signed > 0 else -new_abs
        else:
            closing = min(abs(current), quantity)
            pnl_per_unit = (price - self.average_entry) if current > 0 else (self.average_entry - price)
            self.realized_pnl += closing * pnl_per_unit - fee
            remaining = abs(current) - closing
            if quantity > closing:
                self.side = side
                self.quantity = quantity - closing
                self.average_entry = price
            elif remaining == 0:
                self.quantity = Decimal("0")
            else:
                self.quantity = remaining if current > 0 else -remaining


class Portfolio:
    def __init__(self, cash: Decimal):
        if cash <= 0:
            raise ValueError("cash must be positive")
        self.cash = cash
        self.positions: dict[str, Position] = {}

    def position(self, symbol: str) -> Position | None:
        return self.positions.get(symbol)

    def apply_fill(self, symbol: str, side: OrderSide, quantity: Decimal, price: Decimal, fee: Decimal = Decimal("0")) -> None:
        notional = quantity * price
        self.cash += -notional - fee if side is OrderSide.BUY else notional - fee
        position = self.positions.get(symbol)
        if position is None:
            position = Position(symbol, side, Decimal("0"), price)
            self.positions[symbol] = position
        position.apply_fill(side, quantity, price, fee)
        if position.quantity == 0:
            self.positions.pop(symbol, None)
