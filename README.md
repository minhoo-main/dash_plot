# 📈 Financial Time Series Analysis Dashboard

Python Dash를 사용한 인터랙티브 금융 데이터 시계열 분석 대시보드

## ✨ 주요 기능

### 📊 차트 및 시각화
- **가격 차트** - 실시간 주식 가격 추적
- **수익률 분석** - 일간/누적 수익률 계산 및 시각화
- **변동성 분석** - Rolling volatility (20-day window)
- **이동평균** - MA20, MA50, MA200
- **RSI (Relative Strength Index)** - 과매수/과매도 지표
- **볼린저 밴드** - 가격 변동 범위 시각화
- **상관관계 히트맵** - 여러 종목간 상관관계 분석

### 📈 지원 데이터
- **미국 주식** - AAPL, GOOGL, MSFT, AMZN, TSLA 등
- **지수** - S&P 500, Dow Jones, NASDAQ, Russell 2000
- **암호화폐** - BTC-USD, ETH-USD, BNB-USD
- **원자재** - Gold, Crude Oil, Silver

### 🎯 통계 지표
- 현재 가격
- 연초 대비 수익률 (YTD Return)
- 연율화 변동성 (Annualized Volatility)
- 샤프 비율 (Sharpe Ratio)
- 최대 낙폭 (Max Drawdown)

## 🚀 빠른 시작

### 1. 설치

```bash
git clone https://github.com/minhoo-main/dash_plot.git
cd dash_plot

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 실행

```bash
python app.py
```

브라우저에서 http://localhost:8050 접속

### 3. 사용 방법

1. **티커 선택**: 드롭다운에서 원하는 주식/지수/암호화폐 선택 (다중 선택 가능)
2. **날짜 범위**: 시작일과 종료일 설정
3. **Load Data**: 버튼 클릭하여 데이터 로드
4. **차트 타입**: Price, Returns, Cumulative Returns, Volatility 중 선택
5. **인터랙티브 차트**: 줌, 팬, 호버 등 Plotly 기능 사용

## 📁 프로젝트 구조

```
dash_plot/
├── app.py                  # 메인 Dash 애플리케이션
├── src/
│   └── data_loader.py      # 데이터 로드 및 처리 모듈
├── assets/
│   └── styles.css          # 커스텀 CSS 스타일
├── data/                   # 데이터 저장 디렉토리
├── requirements.txt        # Python 패키지 의존성
├── .gitignore
└── README.md
```

## 📊 기능 상세

### 데이터 로더 (`src/data_loader.py`)

```python
from data_loader import FinancialDataLoader

loader = FinancialDataLoader()

# 데이터 로드
data = loader.load_stock_data(
    tickers=['AAPL', 'GOOGL'],
    start_date='2023-01-01',
    end_date='2024-10-23'
)

# 수익률 계산
returns = loader.calculate_returns(data, period='daily')

# 이동평균
mas = loader.calculate_moving_averages(data, windows=[20, 50, 200])

# RSI
rsi = loader.calculate_rsi(data, period=14)

# 볼린저 밴드
middle, upper, lower = loader.calculate_bollinger_bands(data)

# 통계
stats = loader.calculate_statistics(data)
```

### 지원 함수

| 함수 | 설명 |
|------|------|
| `load_stock_data()` | Yahoo Finance에서 데이터 다운로드 |
| `calculate_returns()` | 일간/주간/월간 수익률 계산 |
| `calculate_cumulative_returns()` | 누적 수익률 |
| `calculate_moving_averages()` | 이동평균 (MA20, MA50, MA200) |
| `calculate_volatility()` | Rolling volatility (연율화) |
| `calculate_bollinger_bands()` | 볼린저 밴드 (중간, 상한, 하한) |
| `calculate_rsi()` | RSI (14일 기준) |
| `calculate_statistics()` | 종합 통계 지표 |

## 🎨 스크린샷

### 메인 대시보드
- 통계 카드: 각 종목의 주요 지표 요약
- 가격 차트: 인터랙티브 시계열 차트
- 기술적 지표: MA, RSI, 볼린저 밴드
- 상관관계: 다중 종목간 상관관계 히트맵

## 🛠️ 기술 스택

- **Dash 2.14.2** - 웹 애플리케이션 프레임워크
- **Plotly 5.18.0** - 인터랙티브 차트 라이브러리
- **pandas 2.1.4** - 데이터 처리
- **yfinance 0.2.33** - 금융 데이터 다운로드
- **dash-bootstrap-components 1.5.0** - UI 컴포넌트
- **numpy, scipy** - 수치 계산

## 📈 데이터 소스

- **Yahoo Finance** - yfinance 라이브러리를 통한 무료 금융 데이터
- 실시간 데이터는 15-20분 지연될 수 있음
- 과거 데이터는 정확함

## 🔧 커스터마이징

### 새로운 티커 추가

`src/data_loader.py`의 `SAMPLE_TICKERS` 딕셔너리 수정:

```python
SAMPLE_TICKERS = {
    'US Stocks': ['AAPL', 'GOOGL', 'YOUR_TICKER'],
    'Indices': ['^GSPC', '^DJI'],
    'Crypto': ['BTC-USD', 'ETH-USD'],
}
```

### 새로운 지표 추가

`src/data_loader.py`에 새로운 메서드 추가 후 `app.py`에서 차트로 시각화

### 스타일 변경

`assets/styles.css` 파일에서 CSS 커스터마이징

## ⚠️ 주의사항

- 너무 많은 티커를 동시에 로드하면 속도가 느려질 수 있음 (권장: 3-5개)
- 과거 데이터가 긴 기간일수록 로딩 시간 증가
- Yahoo Finance API 제한으로 인해 과도한 요청 시 일시적으로 차단될 수 있음

## 🚧 향후 개발 계획

- [ ] 포트폴리오 분석 기능
- [ ] 백테스팅 모듈
- [ ] 머신러닝 기반 가격 예측
- [ ] 실시간 데이터 스트리밍
- [ ] 알림 기능 (가격 알림, RSI 알림 등)
- [ ] 데이터 내보내기 (CSV, Excel)
- [ ] 사용자 정의 지표 추가
- [ ] 다크 모드

## 📄 라이선스

MIT License

## 🤝 기여

Issue 및 Pull Request 환영합니다!

## 📧 문의

GitHub Issues: https://github.com/minhoo-main/dash_plot/issues

---

**마지막 업데이트:** 2025년 10월 23일
**Made with** ❤️ **and Python Dash**
