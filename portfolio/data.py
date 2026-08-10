"""데이터 수집 모듈: S&P 500 유니버스 및 가격 데이터 다운로드 (로컬 캐시 지원)."""

from __future__ import annotations

import os

import pandas as pd

CACHE_DIR = "data_cache"

# Wikipedia 스크래핑 실패 시 사용하는 대형주 스냅샷 (시총 상위권 위주)
FALLBACK_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "AVGO", "TSLA",
    "LLY", "JPM", "V", "UNH", "XOM", "MA", "COST", "HD", "PG", "JNJ", "WMT",
    "NFLX", "ABBV", "CRM", "BAC", "ORCL", "CVX", "MRK", "KO", "AMD", "PEP",
    "ADBE", "TMO", "LIN", "WFC", "CSCO", "ACN", "MCD", "ABT", "GE", "IBM",
    "PM", "TXN", "QCOM", "INTU", "DHR", "AMGN", "ISRG", "CAT", "VZ", "DIS",
    "PFE", "NOW", "GS", "SPGI", "CMCSA", "UNP", "AXP", "T", "RTX", "MS",
    "NEE", "PGR", "LOW", "ETN", "HON", "UBER", "BKNG", "SYK", "ELV", "TJX",
    "BLK", "COP", "VRTX", "LMT", "PLD", "REGN", "BSX", "C", "PANW", "ADP",
    "MDT", "CB", "AMAT", "MMC", "SBUX", "GILD", "ADI", "BA", "DE", "BMY",
    "FI", "MU", "SO", "MO", "KLAC", "LRCX", "DUK", "SHW", "ICE", "INTC",
]


def get_sp500_tickers() -> list[str]:
    """Wikipedia에서 S&P 500 구성종목을 가져온다. 실패하면 내장 스냅샷을 사용한다."""
    try:
        tables = pd.read_html(
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        )
        tickers = tables[0]["Symbol"].str.replace(".", "-", regex=False).tolist()
        if len(tickers) < 400:
            raise ValueError("스크래핑 결과가 비정상적으로 적음")
        return tickers
    except Exception as e:  # noqa: BLE001
        print(f"[경고] S&P 500 목록 스크래핑 실패 ({e}) — 내장 대형주 스냅샷 사용")
        return list(FALLBACK_TICKERS)


def download_prices(
    tickers: list[str],
    start: str,
    end: str | None = None,
    cache_key: str | None = None,
) -> pd.DataFrame:
    """수정주가(Adj Close) 일별 데이터를 다운로드한다. 캐시가 있으면 재사용."""
    import yfinance as yf

    if cache_key:
        os.makedirs(CACHE_DIR, exist_ok=True)
        path = os.path.join(CACHE_DIR, f"{cache_key}.parquet")
        if os.path.exists(path):
            return pd.read_parquet(path)

    raw = yf.download(
        tickers, start=start, end=end, progress=False, auto_adjust=True
    )["Close"]
    if isinstance(raw, pd.Series):
        raw = raw.to_frame(tickers[0])

    # 결측이 과도한 종목(상장기간 짧음 등) 제거
    prices = raw.dropna(axis=1, thresh=int(len(raw) * 0.7)).ffill()

    if cache_key:
        prices.to_parquet(path)
    return prices
