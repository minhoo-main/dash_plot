"""
금융 데이터 로드 및 처리 모듈
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional


class FinancialDataLoader:
    """금융 데이터 로더 클래스"""

    def __init__(self):
        self.data = None
        self.tickers = []

    def load_stock_data(self, tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        야후 파이낸스에서 주식 데이터 로드

        Args:
            tickers: 티커 심볼 리스트 (예: ['AAPL', 'GOOGL'])
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)

        Returns:
            DataFrame with multi-index columns (ticker, price_type)
        """
        self.tickers = tickers

        if isinstance(tickers, str):
            tickers = [tickers]

        # 야후 파이낸스에서 데이터 다운로드
        data = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            progress=False,
            group_by='ticker'
        )

        self.data = data
        return data

    def calculate_returns(self, data: pd.DataFrame, period: str = 'daily') -> pd.DataFrame:
        """
        수익률 계산

        Args:
            data: 가격 데이터
            period: 'daily', 'weekly', 'monthly'

        Returns:
            수익률 DataFrame
        """
        close_prices = self._extract_close_prices(data)

        if period == 'daily':
            returns = close_prices.pct_change()
        elif period == 'weekly':
            returns = close_prices.resample('W').last().pct_change()
        elif period == 'monthly':
            returns = close_prices.resample('M').last().pct_change()
        else:
            raise ValueError(f"Unknown period: {period}")

        return returns.dropna()

    def calculate_cumulative_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """누적 수익률 계산"""
        returns = self.calculate_returns(data, period='daily')
        cumulative_returns = (1 + returns).cumprod() - 1
        return cumulative_returns

    def calculate_moving_averages(self, data: pd.DataFrame,
                                   windows: List[int] = [20, 50, 200]) -> Dict[int, pd.DataFrame]:
        """
        이동평균 계산

        Args:
            data: 가격 데이터
            windows: 이동평균 기간 리스트

        Returns:
            {window: MA DataFrame} 딕셔너리
        """
        close_prices = self._extract_close_prices(data)
        mas = {}

        for window in windows:
            mas[window] = close_prices.rolling(window=window).mean()

        return mas

    def calculate_volatility(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        변동성 계산 (rolling standard deviation)

        Args:
            data: 가격 데이터
            window: 윈도우 크기

        Returns:
            변동성 DataFrame
        """
        returns = self.calculate_returns(data, period='daily')
        volatility = returns.rolling(window=window).std() * np.sqrt(252)  # 연율화
        return volatility

    def calculate_bollinger_bands(self, data: pd.DataFrame,
                                    window: int = 20,
                                    num_std: float = 2.0) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        볼린저 밴드 계산

        Args:
            data: 가격 데이터
            window: 이동평균 기간
            num_std: 표준편차 배수

        Returns:
            (middle_band, upper_band, lower_band) 튜플
        """
        close_prices = self._extract_close_prices(data)

        middle_band = close_prices.rolling(window=window).mean()
        std = close_prices.rolling(window=window).std()

        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)

        return middle_band, upper_band, lower_band

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        RSI (Relative Strength Index) 계산

        Args:
            data: 가격 데이터
            period: RSI 기간

        Returns:
            RSI DataFrame
        """
        close_prices = self._extract_close_prices(data)

        # 가격 변화
        delta = close_prices.diff()

        # 상승/하락 분리
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 평균 상승/하락
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        # RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_statistics(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        기본 통계 지표 계산

        Returns:
            {ticker: {stat_name: value}} 딕셔너리
        """
        close_prices = self._extract_close_prices(data)
        returns = self.calculate_returns(data, period='daily')

        stats = {}

        for ticker in close_prices.columns:
            ticker_returns = returns[ticker].dropna()

            stats[ticker] = {
                'current_price': close_prices[ticker].iloc[-1],
                'mean_return': ticker_returns.mean() * 252,  # 연율화
                'volatility': ticker_returns.std() * np.sqrt(252),  # 연율화
                'sharpe_ratio': (ticker_returns.mean() / ticker_returns.std()) * np.sqrt(252) if ticker_returns.std() != 0 else 0,
                'max_drawdown': self._calculate_max_drawdown(close_prices[ticker]),
                'ytd_return': self._calculate_ytd_return(close_prices[ticker]),
            }

        return stats

    def _extract_close_prices(self, data: pd.DataFrame) -> pd.DataFrame:
        """종가 데이터 추출"""
        if isinstance(data.columns, pd.MultiIndex):
            # Multi-ticker 데이터
            if len(self.tickers) == 1:
                # 단일 티커인 경우
                return data['Close']
            else:
                # 여러 티커인 경우
                close_prices = pd.DataFrame()
                for ticker in self.tickers:
                    if ticker in data.columns.get_level_values(0):
                        close_prices[ticker] = data[ticker]['Close']
                return close_prices
        else:
            # Single ticker 데이터
            if 'Close' in data.columns:
                return data['Close'].to_frame(name=self.tickers[0] if self.tickers else 'Close')
            else:
                return data

    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """최대 낙폭 계산"""
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        return drawdown.min()

    def _calculate_ytd_return(self, prices: pd.Series) -> float:
        """연초 대비 수익률 계산"""
        current_year = datetime.now().year
        year_start = pd.Timestamp(f'{current_year}-01-01')

        if prices.index[0] > year_start:
            # 데이터가 연초 이후부터 시작하면 첫 데이터 사용
            start_price = prices.iloc[0]
        else:
            # 연초 가격 찾기
            year_prices = prices[prices.index >= year_start]
            if len(year_prices) > 0:
                start_price = year_prices.iloc[0]
            else:
                return 0.0

        current_price = prices.iloc[-1]
        return (current_price - start_price) / start_price


# 샘플 티커 리스트
SAMPLE_TICKERS = {
    'US Stocks': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT'],
    'Indices': ['^GSPC', '^DJI', '^IXIC', '^RUT'],  # S&P 500, Dow Jones, NASDAQ, Russell 2000
    'Crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD'],
    'Commodities': ['GC=F', 'CL=F', 'SI=F'],  # Gold, Crude Oil, Silver
}


if __name__ == "__main__":
    # 테스트
    loader = FinancialDataLoader()

    # 애플 주식 데이터 로드
    data = loader.load_stock_data(
        tickers=['AAPL'],
        start_date='2023-01-01',
        end_date='2024-10-23'
    )

    print("데이터 shape:", data.shape)
    print("\n최근 5일 데이터:")
    print(data.tail())

    # 통계 계산
    stats = loader.calculate_statistics(data)
    print("\n통계:")
    for ticker, stat in stats.items():
        print(f"\n{ticker}:")
        for key, value in stat.items():
            print(f"  {key}: {value:.4f}")
