from btc_algo.risk import RiskEngine, RiskLimits, RiskState


def test_daily_loss_circuit_breaker() -> None:
    engine = RiskEngine(RiskLimits(0.01, 0.03, 0.10, 3))
    state = RiskState(equity=9_700, day_start_equity=10_000, peak_equity=10_000)
    allowed, reason = engine.can_trade(state)
    assert not allowed
    assert reason == "daily_loss_limit"


def test_position_sizing() -> None:
    engine = RiskEngine(RiskLimits(0.01, 0.03, 0.10, 3))
    assert engine.position_quantity(10_000, 50_000, 49_000) == 0.1
