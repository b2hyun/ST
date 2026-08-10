"""S&P 500 초과수익 모멘텀 포트폴리오 백테스트 실행 스크립트.

사용 예:
    python main.py --start 2015-01-01 --top-n 20 --cost-bps 10
"""

from __future__ import annotations

import argparse
import os

import pandas as pd

from portfolio.backtest import run_backtest
from portfolio.data import download_prices, get_sp500_tickers
from portfolio.metrics import summary_table

OUTPUT_DIR = "output"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S&P 500 초과수익 모멘텀 포트폴리오")
    p.add_argument("--start", default="2015-01-01", help="백테스트 시작일")
    p.add_argument("--end", default=None, help="백테스트 종료일 (기본: 오늘)")
    p.add_argument("--top-n", type=int, default=20, help="보유 종목 수")
    p.add_argument("--cost-bps", type=float, default=10.0, help="편도 거래비용(bp)")
    p.add_argument("--defensive", default="IEF", help="하락 국면 방어 자산 (예: IEF, SHY)")
    p.add_argument(
        "--no-regime-filter",
        action="store_true",
        help="절대 모멘텀(시장 국면) 필터 비활성화",
    )
    return p.parse_args()


def plot_results(result, path: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True, height_ratios=[2, 1]
    )
    result.equity_curve.plot(ax=ax1, label="Momentum Strategy", linewidth=1.5)
    result.benchmark_curve.plot(ax=ax1, label="S&P 500 (SPY)", linewidth=1.5)
    ax1.set_ylabel("Growth of $1")
    ax1.set_yscale("log")
    ax1.legend()
    ax1.grid(alpha=0.3)

    for series, label in [
        (result.returns, "Strategy"),
        (result.benchmark_returns, "SPY"),
    ]:
        curve = (1 + series).cumprod()
        dd = curve / curve.cummax() - 1
        dd.plot(ax=ax2, label=label, linewidth=1)
    ax2.set_ylabel("Drawdown")
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"차트 저장: {path}")


def main() -> None:
    args = parse_args()

    print("S&P 500 구성종목 조회 중...")
    tickers = get_sp500_tickers()
    print(f"유니버스: {len(tickers)}종목")

    # 모멘텀 lookback 워밍업을 위해 시작일보다 18개월 먼저 다운로드
    dl_start = (pd.Timestamp(args.start) - pd.DateOffset(months=18)).strftime(
        "%Y-%m-%d"
    )
    print("가격 데이터 다운로드 중... (수 분 소요될 수 있음)")
    prices = download_prices(tickers, dl_start, args.end, cache_key="universe")
    spy = download_prices(["SPY"], dl_start, args.end, cache_key="spy")["SPY"]
    defensive = None
    if args.defensive:
        defensive = download_prices(
            [args.defensive], dl_start, args.end, cache_key=args.defensive
        )[args.defensive]

    print("백테스트 실행 중...")
    result = run_backtest(
        prices,
        spy,
        defensive_prices=defensive,
        top_n=args.top_n,
        cost_bps=args.cost_bps,
        use_regime_filter=not args.no_regime_filter,
    )

    table = summary_table(result.returns, result.benchmark_returns)
    pd.set_option("display.float_format", lambda x: f"{x:.4f}")
    print("\n===== 성과 요약 =====")
    print(table)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    table.to_csv(os.path.join(OUTPUT_DIR, "summary.csv"))
    plot_results(result, os.path.join(OUTPUT_DIR, "performance.png"))

    latest = list(result.holdings.values())[-1]
    print("\n===== 최신 리밸런싱 포트폴리오 =====")
    print(latest.to_string())


if __name__ == "__main__":
    main()
