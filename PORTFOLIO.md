# 실전 포트폴리오 — 2026년 8월 리밸런싱

> 목표: S&P 500(SPY) 수익률 초과. 전략 규칙(12-1 모멘텀 + 절대 모멘텀 필터)에 따라 구성.
> 기준일: 2026-08-10 · 다음 리밸런싱: 2026-08-31 (매월 말)

## 시장 국면 판단

- S&P 500은 사상 최고치(약 7,757pt) 부근, 올해 25번째 신고가 경신 중 → **절대 모멘텀 필터: 상승 국면 → 주식 100%**
- Q2 어닝 시즌 전년 대비 +47% 성장, AI 인프라 투자 주도 강세장
- 12개월 모멘텀 상위권은 AI 데이터센터향 메모리·스토리지 반도체에 집중

## 포트폴리오 구성 (총 100%)

### ① 모멘텀 주도주 — 60% (12종목 × 5%)

12개월 수익률 상위 확인 종목. 전략의 핵심 수익원.

| 종목 | 티커 | 비중 | 확인된 성과 (2026 YTD/1년) |
|---|---|---|---|
| SanDisk | SNDK | 5% | +707% YTD (S&P 500 1위, NAND 공급부족) |
| Micron | MU | 5% | +243% YTD (순이익 15배 급증) |
| Western Digital | WDC | 5% | +238% YTD (HDD/SSD, AI 데이터센터) |
| Seagate | STX | 5% | +231% YTD |
| Dell Technologies | DELL | 5% | +246% YTD (AI 서버) |
| Intel | INTC | 5% | +198~278% YTD |
| Marvell | MRVL | 5% | +177% YTD |
| AMD | AMD | 5% | +161% YTD |
| Lumentum | LITE | 5% | +1,420% 1년 (광통신/AI 네트워킹) |
| KLA Corp | KLAC | 5% | +136% 1년 (반도체 장비) |
| Monolithic Power | MPWR | 5% | +132% 1년 (전력반도체) |
| APA Corp | APA | 5% | +136% 1년 (에너지 — 테마 분산) |

### ② AI 플랫폼 대형주 — 25%

주도 테마의 안정적 축. 개별 종목 변동성이 ①보다 낮으면서 AI 사이클 노출 유지.

| 종목 | 티커 | 비중 | 역할 |
|---|---|---|---|
| NVIDIA | NVDA | 6% | AI 가속기 지배력 |
| Broadcom | AVGO | 5% | 커스텀 AI 칩 + 네트워킹 |
| Microsoft | MSFT | 5% | 클라우드/AI 플랫폼 |
| Meta | META | 5% | AI 활용 광고 수익화 |
| Oracle | ORCL | 4% | AI 클라우드 인프라 |

### ③ 방어·헤지 — 15%

모멘텀 상위가 한 테마(메모리/AI 하드웨어)에 집중된 데 따른 급락 위험 완화.

| 자산 | 티커 | 비중 | 역할 |
|---|---|---|---|
| 미국 중기채 ETF | IEF | 10% | 주식 급락 시 완충, 하락 국면 대피처 |
| 금 ETF | GLD | 5% | 인플레이션·시스템 리스크 헤지 |

## 운용 규칙

1. **매월 말 리밸런싱** — `python main.py` 실행으로 최신 12-1 모멘텀 상위 종목을 재계산해 ①을 교체
2. **하락 국면 전환 시** — SPY의 12개월 수익률이 음수로 돌아서면 ①+②를 전량 IEF로 회피
3. **비중 이탈 허용폭** — 개별 종목이 목표 비중의 ±2%p를 벗어나면 리밸런싱일에 복원
4. **거래비용 관리** — 월 1회만 매매, 시장가 대신 지정가 사용 권장

## 반드시 알아야 할 리스크

- **모멘텀 크래시**: 주도주가 급반전하면 (2000년 닷컴, 2022년처럼) 시장보다 크게 하락할 수 있음. ③과 월별 리밸런싱이 완충 장치.
- **밸류에이션**: SNDK(+707%), LITE(+1,420%) 같은 종목은 이미 큰 폭 상승 후라 변동성이 극심함. 5% 균등비중을 초과해 담지 말 것.
- **테마 집중**: ①의 대부분이 AI 하드웨어 사이클 하나에 의존. 메모리 가격이 꺾이면 동반 하락.
- 과거 성과는 미래를 보장하지 않으며, 이 문서는 투자 자문이 아닌 연구 목적임.

## 근거 자료 (2026-08-10 조사)

- [The 20 best-performing stocks in the S&P 500 for the first half of 2026 (Yahoo Finance)](https://finance.yahoo.com/markets/stocks/articles/20-best-performing-stocks-p-211300290.html)
- [The S&P 500 Hit Another Record High in 2026 (Bloomberg)](https://www.bloomberg.com/news/newsletters/2026-08-06/the-s-p-500-hit-another-record-high-in-2026-so-what-money)
- [Dow surges 900 points, S&P 500 closes above 7,700 (CNBC)](https://www.cnbc.com/2026/08/03/stock-market-today-live-updates.html)
- [Sandisk Is the Best-Performing S&P 500 Stock During the First Half of 2026 (Motley Fool)](https://www.fool.com/investing/2026/07/03/sandisk-is-the-best-performing-sp-500-stock-during/)
- [10 Best Performing S&P 500 Stocks So Far in 2026 (Insider Monkey)](https://www.insidermonkey.com/blog/10-best-performing-sp-500-stocks-so-far-in-2026-1747803/)
- [The State of the Markets, August 2026 (Charlie Bilello)](https://bilello.blog/2026/the-state-of-the-markets-august-2026)
