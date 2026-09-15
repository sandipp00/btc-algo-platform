from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Signal:
    side: str
    price: float
    stop: float
    reason: str


def ema_rsi_signal(frame: pd.DataFrame, fast: int = 20, slow: int = 50, rsi_period: int = 14) -> Signal | None:
    required = {"close"}
    if not required.issubset(frame.columns) or len(frame) < slow + 2:
        return None

    close = frame["close"].astype(float)
    fast_ema = close.ewm(span=fast, adjust=False).mean()
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / rsi_period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / rsi_period, adjust=False).mean()
    rs = gain / loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))

    prev = len(frame) - 2
    cur = len(frame) - 1
    price = float(close.iloc[cur])
    if fast_ema.iloc[prev] <= slow_ema.iloc[prev] and fast_ema.iloc[cur] > slow_ema.iloc[cur] and rsi.iloc[cur] < 70:
        return Signal("buy", price, float(close.iloc[cur] * 0.98), "ema_bull_cross_rsi")
    if fast_ema.iloc[prev] >= slow_ema.iloc[prev] and fast_ema.iloc[cur] < slow_ema.iloc[cur] and rsi.iloc[cur] > 30:
        return Signal("sell", price, float(close.iloc[cur] * 1.02), "ema_bear_cross_rsi")
    return None
