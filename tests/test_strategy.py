"""합성 데이터로 전략·백테스트 로직을 검증한다 (네트워크 불필요)."""

import numpy as np
import pandas as pd
import pytest

from portfolio.backtest import month_end_dates, run_backtest
from portfolio.metrics import (
    alpha_beta,
    cagr,
    max_drawdown,
    sharpe_ratio,
    summary_table,
)
from portfolio.strategy import (
    market_regime_bullish,
    momentum_score,
    select_top_momentum,
    target_weights,
)


def make_prices(daily_returns: dict[str, float], days: int = 600) -> pd.DataFrame:
    """종목별 일정한 일별 수익률을 갖는 합성 가격 데이터."""
    idx = pd.bdate_range("2020-01-01", periods=days)
    data = {
        t: 100 * (1 + r) ** np.arange(days) for t, r in daily_returns.items()
    }
    return pd.DataFrame(data, index=idx)


class TestMomentum:
    def test_ranks_by_past_return(self):
        prices = make_prices({"UP": 0.002, "FLAT": 0.0, "DOWN": -0.002})
        scores = momentum_score(prices)
        assert scores["UP"] > scores["FLAT"] > scores["DOWN"]

    def test_top_n_selection(self):
        prices = make_prices({"A": 0.003, "B": 0.002, "C": 0.001, "D": -0.001})
        assert set(select_top_momentum(prices, top_n=2)) == {"A", "B"}

    def test_skip_excludes_recent_month(self):
        # 과거 11개월 강세 후 최근 1개월 폭락한 종목: 12-1 모멘텀은 폭락을 무시해야 함
        idx = pd.bdate_range("2020-01-01", periods=300)
        up_then_crash = np.concatenate(
            [100 * 1.003 ** np.arange(279), np.full(21, 1.0)]
        )
        prices = pd.DataFrame({"X": up_then_crash, "FLAT": 100.0}, index=idx)
        scores = momentum_score(prices)
        assert scores["X"] > scores["FLAT"]

    def test_insufficient_history_raises(self):
        prices = make_prices({"A": 0.001}, days=100)
        with pytest.raises(ValueError):
            momentum_score(prices)


class TestRegimeFilter:
    def test_bullish_market(self):
        bench = make_prices({"SPY": 0.001})["SPY"]
        assert market_regime_bullish(bench) is True

    def test_bearish_market(self):
        bench = make_prices({"SPY": -0.001})["SPY"]
        assert market_regime_bullish(bench) is False

    def test_bearish_switches_to_defensive(self):
        prices = make_prices({"A": 0.002, "B": 0.001})
        bench = make_prices({"SPY": -0.001})["SPY"]
        w = target_weights(prices, bench, defensive="DEF", top_n=2)
        assert w.to_dict() == {"DEF": 1.0}

    def test_bearish_without_defensive_goes_to_cash(self):
        prices = make_prices({"A": 0.002, "B": 0.001})
        bench = make_prices({"SPY": -0.001})["SPY"]
        w = target_weights(prices, bench, defensive=None, top_n=2)
        assert len(w) == 0

    def test_bullish_equal_weights(self):
        prices = make_prices({"A": 0.003, "B": 0.002, "C": -0.001})
        bench = make_prices({"SPY": 0.001})["SPY"]
        w = target_weights(prices, bench, defensive="DEF", top_n=2)
        assert set(w.index) == {"A", "B"}
        assert np.allclose(w.values, 0.5)


class TestMetrics:
    def test_cagr_constant_return(self):
        # 252일간 매일 r이면 연복리 = (1+r)^252 - 1
        r = 0.001
        rets = pd.Series([r] * 252)
        assert cagr(rets) == pytest.approx((1 + r) ** 252 - 1, rel=1e-6)

    def test_max_drawdown(self):
        # +100% 후 -50%: 고점 대비 낙폭 50%
        rets = pd.Series([1.0, -0.5])
        assert max_drawdown(rets) == pytest.approx(-0.5)

    def test_sharpe_positive_for_steady_gains(self):
        rets = pd.Series(np.full(252, 0.001))
        rets.iloc[::2] += 0.0001  # 변동성 0 방지
        assert sharpe_ratio(rets) > 0

    def test_beta_of_benchmark_itself_is_one(self):
        rng = np.random.default_rng(0)
        bench = pd.Series(rng.normal(0.0005, 0.01, 500))
        alpha, beta = alpha_beta(bench, bench)
        assert beta == pytest.approx(1.0)
        assert alpha == pytest.approx(0.0, abs=1e-12)

    def test_summary_table_shape(self):
        rng = np.random.default_rng(1)
        idx = pd.bdate_range("2020-01-01", periods=300)
        s = pd.Series(rng.normal(0.001, 0.01, 300), index=idx)
        b = pd.Series(rng.normal(0.0005, 0.01, 300), index=idx)
        table = summary_table(s, b)
        assert list(table.columns) == ["전략", "S&P 500 (SPY)"]
        assert "CAGR" in table.index and "MDD" in table.index


class TestBacktest:
    def test_month_end_dates(self):
        idx = pd.bdate_range("2020-01-01", "2020-03-31")
        ends = month_end_dates(idx)
        assert len(ends) == 3
        assert all(d in idx for d in ends)

    def test_strategy_holds_winners(self):
        # 강한 상승 종목 2개 + 하락 종목 다수: 전략은 벤치마크(전체 평균)를 이겨야 함
        universe = {"W1": 0.002, "W2": 0.0018}
        universe.update({f"L{i}": -0.0005 for i in range(8)})
        prices = make_prices(universe, days=800)
        bench = prices.mean(axis=1)
        result = run_backtest(
            prices, bench, top_n=2, cost_bps=10, use_regime_filter=False
        )
        assert (1 + result.returns).prod() > (1 + result.benchmark_returns).prod()
        # 리밸런싱마다 상승 종목만 보유했는지 확인
        for w in result.holdings.values():
            assert set(w.index) == {"W1", "W2"}

    def test_costs_reduce_returns(self):
        prices = make_prices({"A": 0.001, "B": 0.0009, "C": 0.0008}, days=700)
        bench = prices.mean(axis=1)
        no_cost = run_backtest(
            prices, bench, top_n=2, cost_bps=0, use_regime_filter=False
        )
        with_cost = run_backtest(
            prices, bench, top_n=2, cost_bps=50, use_regime_filter=False
        )
        assert (1 + with_cost.returns).prod() < (1 + no_cost.returns).prod()

    def test_regime_filter_avoids_crash(self):
        # 전반 상승 후 후반 지속 하락하는 시장: 필터 사용 시 손실이 줄어야 함
        days = 900
        idx = pd.bdate_range("2018-01-01", periods=days)
        half = days // 2
        path = np.concatenate(
            [100 * 1.001 ** np.arange(half),
             100 * 1.001**half * 0.998 ** np.arange(days - half)]
        )
        prices = pd.DataFrame({"A": path, "B": path * 0.99, "C": path * 1.01},
                              index=idx)
        bench = pd.Series(path, index=idx)
        filtered = run_backtest(prices, bench, top_n=2, cost_bps=0,
                                use_regime_filter=True)
        unfiltered = run_backtest(prices, bench, top_n=2, cost_bps=0,
                                  use_regime_filter=False)
        assert max_drawdown(filtered.returns) > max_drawdown(unfiltered.returns)

    def test_short_history_raises(self):
        prices = make_prices({"A": 0.001, "B": 0.0}, days=260)
        bench = prices.mean(axis=1)
        with pytest.raises(ValueError):
            run_backtest(prices, bench, top_n=1)
