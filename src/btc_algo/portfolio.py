from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Position:
    symbol: str
    quantity: Decimal = Decimal("0")
    average_entry: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")

    def apply_fill(self, side: str, quantity: Decimal, price: Decimal, fee: Decimal = Decimal("0")) -> None:
        if quantity <= 0 or price <= 0 or fee < 0:
            raise ValueError("quantity and price must be positive and fee non-negative")
        signed = quantity if side == "buy" else -quantity
        current = self.quantity

        if current == 0:
            self.quantity = signed
            self.average_entry = price
            self.realized_pnl -= fee
            return

        same_direction = (current > 0) == (signed > 0)
        if same_direction:
            new_abs = abs(current) + quantity
            self.average_entry = (
                abs(current) * self.average_entry + quantity * price
            ) / new_abs
            self.quantity = current + signed
            self.realized_pnl -= fee
            return

        closing = min(abs(current), quantity)
        pnl_per_unit = (
            price - self.average_entry if current > 0
            else self.average_entry - price
        )
        self.realized_pnl += closing * pnl_per_unit - fee
        remaining = abs(current) - closing

        if remaining == 0:
            self.quantity = Decimal("0")
            self.average_entry = Decimal("0")
        elif quantity > closing:
            self.quantity = signed + (current if current > 0 else -current)
            self.quantity = signed + current
            self.average_entry = price
        else:
            self.quantity = current + signed

    def unrealized_pnl(self, mark_price: Decimal) -> Decimal:
        if self.quantity == 0:
            return Decimal("0")
        if mark_price <= 0:
            raise ValueError("mark price must be positive")
        return self.quantity * (mark_price - self.average_entry)


class Portfolio:
    def __init__(self, cash: Decimal):
        if cash <= 0:
            raise ValueError("cash must be positive")
        self.cash = cash
        self.positions: dict[str, Position] = {}

    def apply_fill(self, symbol: str, side: str, quantity: Decimal, price: Decimal, fee: Decimal = Decimal("0")) -> None:
        notional = quantity * price
        self.cash += -notional - fee if side == "buy" else notional - fee
        position = self.positions.setdefault(symbol, Position(symbol))
        position.apply_fill(side, quantity, price, fee)
        if position.quantity == 0:
            self.positions.pop(symbol, None)

    def equity(self, marks: dict[str, Decimal]) -> Decimal:
        value = self.cash
        for symbol, position in self.positions.items():
            if symbol not in marks:
                raise KeyError(f"missing mark price for {symbol}")
            value += position.quantity * marks[symbol]
        return value

    def exposure(self, marks: dict[str, Decimal]) -> Decimal:
        total = Decimal("0")
        for symbol, position in self.positions.items():
            if symbol not in marks:
                raise KeyError(f"missing mark price for {symbol}")
            total += abs(position.quantity * marks[symbol])
        return total
