"""모멘텀 전략: 횡단면 모멘텀(종목 선택) + 절대 모멘텀(시장 국면 필터)."""

from __future__ import annotations

import pandas as pd

TRADING_DAYS_YEAR = 252
TRADING_DAYS_MONTH = 21


def momentum_score(
    prices: pd.DataFrame,
    lookback: int = TRADING_DAYS_YEAR,
    skip: int = TRADING_DAYS_MONTH,
) -> pd.Series:
    """12-1 모멘텀: 최근 1개월을 제외한 과거 12개월 수익률.

    최근 1개월을 제외하는 이유는 단기 반전(short-term reversal) 효과를
    피하기 위함이다 (Jegadeesh & Titman, 1993).
    """
    if len(prices) < lookback + 1:
        raise ValueError(f"모멘텀 계산에 최소 {lookback + 1}일의 데이터가 필요합니다")
    recent = prices.iloc[-1 - skip]
    past = prices.iloc[-1 - lookback]
    return (recent / past - 1).dropna()


def select_top_momentum(
    prices: pd.DataFrame,
    top_n: int = 20,
    lookback: int = TRADING_DAYS_YEAR,
    skip: int = TRADING_DAYS_MONTH,
) -> list[str]:
    """모멘텀 점수 상위 top_n 종목을 반환한다."""
    scores = momentum_score(prices, lookback=lookback, skip=skip)
    return scores.nlargest(top_n).index.tolist()


def market_regime_bullish(
    benchmark: pd.Series, lookback: int = TRADING_DAYS_YEAR
) -> bool:
    """절대 모멘텀 필터: 벤치마크의 과거 12개월 수익률이 양수인지 여부.

    음수이면 시장 하락 국면으로 판단하고 방어 자산으로 회피한다
    (Antonacci, Dual Momentum).
    """
    if len(benchmark) < lookback + 1:
        raise ValueError(f"국면 판단에 최소 {lookback + 1}일의 데이터가 필요합니다")
    ret = benchmark.iloc[-1] / benchmark.iloc[-1 - lookback] - 1
    return bool(ret > 0)


def target_weights(
    prices: pd.DataFrame,
    benchmark: pd.Series,
    defensive: str | None,
    top_n: int = 20,
    lookback: int = TRADING_DAYS_YEAR,
    skip: int = TRADING_DAYS_MONTH,
    use_regime_filter: bool = True,
) -> pd.Series:
    """리밸런싱 시점의 목표 비중을 계산한다.

    상승 국면: 모멘텀 상위 top_n 종목 동일비중.
    하락 국면: 방어 자산 100% (방어 자산이 없으면 현금 = 빈 비중).
    """
    if use_regime_filter and not market_regime_bullish(benchmark, lookback):
        if defensive is not None:
            return pd.Series({defensive: 1.0})
        return pd.Series(dtype=float)  # 전량 현금

    picks = select_top_momentum(prices, top_n=top_n, lookback=lookback, skip=skip)
    return pd.Series(1.0 / len(picks), index=picks)
