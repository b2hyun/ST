"""백테스트 엔진: 월별 리밸런싱, 거래비용 반영, 벤치마크 비교."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .strategy import TRADING_DAYS_MONTH, TRADING_DAYS_YEAR, target_weights


@dataclass
class BacktestResult:
    returns: pd.Series  # 전략 일별 수익률 (비용 차감 후)
    benchmark_returns: pd.Series  # 벤치마크 일별 수익률
    holdings: dict = field(default_factory=dict)  # 리밸런싱일 -> 목표 비중

    @property
    def equity_curve(self) -> pd.Series:
        return (1 + self.returns).cumprod()

    @property
    def benchmark_curve(self) -> pd.Series:
        return (1 + self.benchmark_returns).cumprod()


def month_end_dates(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """거래일 기준 매월 마지막 날짜들."""
    s = pd.Series(index, index=index)
    return pd.DatetimeIndex(s.groupby([index.year, index.month]).last().values)


def run_backtest(
    prices: pd.DataFrame,
    benchmark: pd.Series,
    defensive_prices: pd.Series | None = None,
    top_n: int = 20,
    lookback: int = TRADING_DAYS_YEAR,
    skip: int = TRADING_DAYS_MONTH,
    cost_bps: float = 10.0,
    use_regime_filter: bool = True,
) -> BacktestResult:
    """월말 리밸런싱 모멘텀 전략을 백테스트한다.

    - prices: 유니버스 수정주가 (일별, 종목별 컬럼)
    - benchmark: 벤치마크 수정주가 (SPY)
    - defensive_prices: 하락 국면에 보유할 방어 자산 수정주가 (없으면 현금)
    - cost_bps: 편도 거래비용 (basis points)

    보유 기간 중에는 동일비중을 매일 유지한다고 가정한다(일별 리밸런싱 근사).
    비용은 리밸런싱일에 비중 변화량 합계 x 편도비용으로 차감한다.
    """
    defensive_name = "_DEFENSIVE_"
    all_prices = prices.copy()
    if defensive_prices is not None:
        all_prices[defensive_name] = defensive_prices
    daily_returns = all_prices.pct_change().fillna(0.0)
    bench_returns = benchmark.pct_change().fillna(0.0)

    rebal_dates = month_end_dates(prices.index)
    # 모멘텀 계산이 가능한 시점 이후만 사용
    rebal_dates = rebal_dates[rebal_dates >= prices.index[lookback]]
    if len(rebal_dates) < 2:
        raise ValueError("백테스트 기간이 너무 짧습니다 (lookback 이후 2개월 이상 필요)")

    strat_returns = pd.Series(0.0, index=prices.index)
    holdings: dict = {}
    prev_weights = pd.Series(dtype=float)
    cost_rate = cost_bps / 10_000

    for i, rebal_date in enumerate(rebal_dates[:-1]):
        history = prices.loc[:rebal_date]
        bench_history = benchmark.loc[:rebal_date]
        weights = target_weights(
            history,
            bench_history,
            defensive=defensive_name if defensive_prices is not None else None,
            top_n=top_n,
            lookback=lookback,
            skip=skip,
            use_regime_filter=use_regime_filter,
        )
        holdings[rebal_date] = weights

        # 다음 리밸런싱일까지의 보유 기간
        period_end = rebal_dates[i + 1]
        mask = (prices.index > rebal_date) & (prices.index <= period_end)
        period_rets = daily_returns.loc[mask, weights.index]
        strat_returns.loc[mask] = (period_rets * weights).sum(axis=1)

        # 거래비용: 비중 변화량 총합 x 편도비용
        turnover = (
            weights.subtract(prev_weights, fill_value=0.0).abs().sum()
        )
        first_day = prices.index[mask][0] if mask.any() else None
        if first_day is not None:
            strat_returns.loc[first_day] -= turnover * cost_rate
        prev_weights = weights

    # 워밍업 구간 제외
    start = rebal_dates[0]
    strat_returns = strat_returns.loc[strat_returns.index > start]
    bench_returns = bench_returns.loc[bench_returns.index > start]
    return BacktestResult(
        returns=strat_returns, benchmark_returns=bench_returns, holdings=holdings
    )
