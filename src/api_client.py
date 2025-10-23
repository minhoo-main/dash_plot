"""
FastAPI 서버 클라이언트
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime


class APIClient:
    """FastAPI 서버와 통신하는 클라이언트"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Args:
            base_url: FastAPI 서버 URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def get_categories(self) -> Dict:
        """
        카테고리 목록 조회

        Returns:
            {
                "금리": {"국고채": [...], "중앙은행": [...]},
                "환율": {"주요통화": [...], ...}
            }
        """
        try:
            response = self.session.get(f"{self.base_url}/api/categories")
            response.raise_for_status()

            result = response.json()
            if result['status'] == 'success':
                return result['data']
            else:
                print(f"API Error: {result.get('message', 'Unknown error')}")
                return {}

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return {}

    def get_interest_rates(self,
                          items: List[str],
                          start_date: str,
                          end_date: str) -> pd.DataFrame:
        """
        금리 데이터 조회

        Args:
            items: 금리 항목 리스트 (예: ['US_10Y', 'KR_3Y'])
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)

        Returns:
            DataFrame (인덱스: 날짜, 컬럼: 각 금리 항목)
        """
        try:
            params = {
                'items': ','.join(items),
                'start_date': start_date,
                'end_date': end_date
            }

            response = self.session.get(
                f"{self.base_url}/api/interest-rates",
                params=params
            )
            response.raise_for_status()

            result = response.json()

            if result['status'] == 'success':
                return self._parse_timeseries_response(result['data'])
            else:
                print(f"API Error: {result.get('message', 'Unknown error')}")
                return pd.DataFrame()

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return pd.DataFrame()

    def get_exchange_rates(self,
                          pairs: List[str],
                          start_date: str,
                          end_date: str) -> pd.DataFrame:
        """
        환율 데이터 조회

        Args:
            pairs: 통화쌍 리스트 (예: ['USD/KRW', 'EUR/KRW'])
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            DataFrame
        """
        try:
            params = {
                'pairs': ','.join(pairs),
                'start_date': start_date,
                'end_date': end_date
            }

            response = self.session.get(
                f"{self.base_url}/api/exchange-rates",
                params=params
            )
            response.raise_for_status()

            result = response.json()

            if result['status'] == 'success':
                return self._parse_timeseries_response(result['data'])
            else:
                print(f"API Error: {result.get('message', 'Unknown error')}")
                return pd.DataFrame()

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return pd.DataFrame()

    def get_statistics(self,
                      data_type: str,
                      items: List[str],
                      start_date: str,
                      end_date: str) -> Dict:
        """
        통계 데이터 조회

        Args:
            data_type: 'interest_rate' or 'exchange_rate'
            items: 항목 리스트
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            {item: {stat_name: value}} 딕셔너리
        """
        try:
            params = {
                'data_type': data_type,
                'items': ','.join(items),
                'start_date': start_date,
                'end_date': end_date
            }

            response = self.session.get(
                f"{self.base_url}/api/statistics",
                params=params
            )
            response.raise_for_status()

            result = response.json()

            if result['status'] == 'success':
                return result['data']
            else:
                print(f"API Error: {result.get('message', 'Unknown error')}")
                return {}

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return {}

    def _parse_timeseries_response(self, data: Dict) -> pd.DataFrame:
        """
        API 응답을 DataFrame으로 변환

        Args:
            data: API 응답 데이터
                {
                    "dates": [...],
                    "series": {
                        "US_10Y": {"values": [...], ...},
                        ...
                    }
                }

        Returns:
            DataFrame (인덱스: 날짜, 컬럼: 각 항목)
        """
        dates = pd.to_datetime(data['dates'])
        series_data = {}

        for item_name, item_data in data['series'].items():
            series_data[item_name] = item_data['values']

        df = pd.DataFrame(series_data, index=dates)
        return df

    def close(self):
        """세션 종료"""
        self.session.close()


# Mock 클라이언트 (FastAPI 서버 없이 테스트용)
class MockAPIClient(APIClient):
    """테스트용 Mock 클라이언트"""

    def __init__(self):
        # 부모 클래스의 __init__ 호출하지 않음
        self.base_url = "mock://localhost"

    def get_categories(self) -> Dict:
        """Mock 카테고리 데이터"""
        return {
            "금리": {
                "국고채": ["US_10Y", "KR_3Y", "KR_5Y", "KR_10Y", "JP_10Y"],
                "중앙은행": ["FED_RATE", "BOK_RATE", "ECB_RATE", "BOJ_RATE"],
                "회사채": ["KR_AAA_3Y", "KR_AA_3Y", "US_CORP_BBB"]
            },
            "환율": {
                "주요통화": ["USD/KRW", "EUR/KRW", "JPY/KRW", "CNY/KRW"],
                "달러기준": ["EUR/USD", "GBP/USD", "JPY/USD", "AUD/USD"],
                "신흥국": ["USD/BRL", "USD/INR", "USD/MXN", "USD/ZAR"]
            }
        }

    def get_interest_rates(self, items: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Mock 금리 데이터 생성"""
        import numpy as np

        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # 기본 금리값
        base_rates = {
            'US_10Y': 4.0,
            'KR_3Y': 3.2,
            'KR_5Y': 3.3,
            'KR_10Y': 3.5,
            'JP_10Y': 0.8,
            'FED_RATE': 5.25,
            'BOK_RATE': 3.5,
            'ECB_RATE': 4.0,
            'BOJ_RATE': -0.1,
            'KR_AAA_3Y': 3.6,
            'KR_AA_3Y': 3.9,
            'US_CORP_BBB': 5.2,
        }

        data = {}
        for item in items:
            base = base_rates.get(item, 3.0)
            # 랜덤 워크 시뮬레이션
            random_walk = np.cumsum(np.random.randn(len(dates)) * 0.02)
            data[item] = base + random_walk

        return pd.DataFrame(data, index=dates)

    def get_exchange_rates(self, pairs: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Mock 환율 데이터 생성"""
        import numpy as np

        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # 기본 환율값
        base_rates = {
            'USD/KRW': 1350.0,
            'EUR/KRW': 1450.0,
            'JPY/KRW': 9.5,
            'CNY/KRW': 185.0,
            'EUR/USD': 1.08,
            'GBP/USD': 1.27,
            'JPY/USD': 142.0,
            'AUD/USD': 0.66,
            'USD/BRL': 5.0,
            'USD/INR': 83.0,
            'USD/MXN': 17.0,
            'USD/ZAR': 18.5,
        }

        data = {}
        for pair in pairs:
            base = base_rates.get(pair, 1000.0)
            # 랜덤 워크
            volatility = base * 0.005
            random_walk = np.cumsum(np.random.randn(len(dates)) * volatility)
            data[pair] = base + random_walk

        return pd.DataFrame(data, index=dates)

    def get_statistics(self, data_type: str, items: List[str], start_date: str, end_date: str) -> Dict:
        """Mock 통계 데이터"""
        if data_type == 'interest_rate':
            df = self.get_interest_rates(items, start_date, end_date)
        else:
            df = self.get_exchange_rates(items, start_date, end_date)

        stats = {}
        for col in df.columns:
            data = df[col].dropna()

            stats[col] = {
                'current': float(data.iloc[-1]),
                'mean': float(data.mean()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max()),
                'median': float(data.median()),
                'q25': float(data.quantile(0.25)),
                'q75': float(data.quantile(0.75)),
                'change_1d': float(data.iloc[-1] - data.iloc[-2]) if len(data) > 1 else 0,
                'change_1w': float(data.iloc[-1] - data.iloc[-5]) if len(data) > 5 else 0,
                'change_1m': float(data.iloc[-1] - data.iloc[-20]) if len(data) > 20 else 0,
                'pct_change_1d': float((data.iloc[-1] - data.iloc[-2]) / data.iloc[-2] * 100) if len(data) > 1 else 0,
                'unit': '%' if data_type == 'interest_rate' else 'KRW'
            }

        return stats


if __name__ == "__main__":
    # Mock 클라이언트 테스트
    print("=== Mock API Client 테스트 ===\n")

    client = MockAPIClient()

    # 카테고리 조회
    print("1. 카테고리 조회:")
    categories = client.get_categories()
    print(f"금리 카테고리: {list(categories['금리'].keys())}")
    print(f"환율 카테고리: {list(categories['환율'].keys())}\n")

    # 금리 데이터 조회
    print("2. 금리 데이터 조회:")
    df_rates = client.get_interest_rates(
        items=['US_10Y', 'KR_3Y', 'FED_RATE'],
        start_date='2024-10-01',
        end_date='2024-10-23'
    )
    print(df_rates.head())
    print(f"\nShape: {df_rates.shape}\n")

    # 환율 데이터 조회
    print("3. 환율 데이터 조회:")
    df_fx = client.get_exchange_rates(
        pairs=['USD/KRW', 'EUR/KRW'],
        start_date='2024-10-01',
        end_date='2024-10-23'
    )
    print(df_fx.head())
    print(f"\nShape: {df_fx.shape}\n")

    # 통계 데이터 조회
    print("4. 통계 데이터:")
    stats = client.get_statistics(
        data_type='interest_rate',
        items=['US_10Y', 'KR_3Y'],
        start_date='2024-10-01',
        end_date='2024-10-23'
    )
    for item, stat in stats.items():
        print(f"\n{item}:")
        print(f"  현재값: {stat['current']:.4f}")
        print(f"  평균: {stat['mean']:.4f}")
        print(f"  1일 변화: {stat['change_1d']:+.4f}")
        print(f"  1일 변화율: {stat['pct_change_1d']:+.2f}%")
