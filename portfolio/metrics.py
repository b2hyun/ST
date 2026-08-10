"""성과 지표 계산: CAGR, 변동성, 샤프, MDD, 알파/베타 등."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_YEAR = 252


def cagr(returns: pd.Series) -> float:
    """일별 수익률 시계열로부터 연복리 수익률을 계산한다."""
    total = float((1 + returns).prod())
    years = len(returns) / TRADING_DAYS_YEAR
    if years <= 0 or total <= 0:
        return float("nan")
    return total ** (1 / years) - 1


def annual_volatility(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(TRADING_DAYS_YEAR))


def sharpe_ratio(returns: pd.Series, risk_free_annual: float = 0.02) -> float:
    rf_daily = (1 + risk_free_annual) ** (1 / TRADING_DAYS_YEAR) - 1
    excess = returns - rf_daily
    vol = excess.std()
    if vol == 0:
        return float("nan")
    return float(excess.mean() / vol * np.sqrt(TRADING_DAYS_YEAR))


def max_drawdown(returns: pd.Series) -> float:
    """최대낙폭(MDD). 음수로 반환한다 (예: -0.35)."""
    curve = (1 + returns).cumprod()
    peak = curve.cummax()
    return float((curve / peak - 1).min())


def alpha_beta(
    returns: pd.Series, benchmark_returns: pd.Series
) -> tuple[float, float]:
    """벤치마크 대비 연환산 알파와 베타 (단순 CAPM 회귀)."""
    joined = pd.concat([returns, benchmark_returns], axis=1).dropna()
    r, b = joined.iloc[:, 0], joined.iloc[:, 1]
    var = b.var()
    if var == 0:
        return float("nan"), float("nan")
    beta = float(r.cov(b) / var)
    alpha_daily = float(r.mean() - beta * b.mean())
    return alpha_daily * TRADING_DAYS_YEAR, beta


def summary_table(
    strategy: pd.Series, benchmark: pd.Series, risk_free_annual: float = 0.02
) -> pd.DataFrame:
    """전략 vs 벤치마크 성과 요약표."""
    alpha, beta = alpha_beta(strategy, benchmark)
    rows = {
        "CAGR": [cagr(strategy), cagr(benchmark)],
        "연변동성": [annual_volatility(strategy), annual_volatility(benchmark)],
        "샤프비율": [
            sharpe_ratio(strategy, risk_free_annual),
            sharpe_ratio(benchmark, risk_free_annual),
        ],
        "MDD": [max_drawdown(strategy), max_drawdown(benchmark)],
        "알파(연)": [alpha, 0.0],
        "베타": [beta, 1.0],
    }
    return pd.DataFrame(rows, index=["전략", "S&P 500 (SPY)"]).T
