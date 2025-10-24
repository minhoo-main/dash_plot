"""
FastAPI 서버 클라이언트 (개선 버전)
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime

from src.exceptions import (
    APIConnectionError,
    APITimeoutError,
    APIResponseError,
    DataNotFoundError
)
from src.logging_config import get_logger
from src.validators import validate_date_range, validate_api_response

# 로거 설정
logger = get_logger(__name__)


class APIClient:
    """FastAPI 서버와 통신하는 클라이언트"""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Args:
            base_url: FastAPI 서버 URL
            timeout: 요청 타임아웃 (초)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        logger.info(f"API Client initialized with base_url: {self.base_url}")

    def get_categories(self) -> Dict[str, Dict[str, List[str]]]:
        """
        카테고리 목록 조회

        Returns:
            {
                "금리": {"국고채": [...], "중앙은행": [...]},
                "환율": {"주요통화": [...], ...}
            }

        Raises:
            APIConnectionError: 서버 연결 실패
            APITimeoutError: 요청 타임아웃
            APIResponseError: 잘못된 응답
        """
        logger.debug("Fetching categories")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/categories",
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            validate_api_response(result)

            if result['status'] == 'success':
                logger.info(f"Successfully fetched categories")
                return result['data']
            else:
                error_msg = result.get('message', 'Unknown error')
                logger.error(f"API returned error: {error_msg}")
                raise APIResponseError(error_msg)

        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise APIConnectionError(f"서버에 연결할 수 없습니다: {self.base_url}")
        except requests.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise APITimeoutError(f"요청 시간 초과 ({self.timeout}초)")
        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise APIResponseError(f"HTTP 오류: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise APIResponseError(f"예상치 못한 오류: {e}")

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

        Raises:
            ValidationError: 입력 데이터 검증 실패
            APIConnectionError: 서버 연결 실패
            APITimeoutError: 요청 타임아웃
            DataNotFoundError: 데이터 없음
        """
        validate_date_range(start_date, end_date)
        logger.debug(f"Fetching interest rates: items={items}, start={start_date}, end={end_date}")
        
        return self._get_timeseries_data(
            endpoint='api/interest-rates',
            param_name='items',
            items=items,
            start_date=start_date,
            end_date=end_date,
            data_type='금리'
        )

    def get_exchange_rates(self,
                          pairs: List[str],
                          start_date: str,
                          end_date: str) -> pd.DataFrame:
        """
        환율 데이터 조회

        Args:
            pairs: 통화쌍 리스트 (예: ['USD/KRW', 'EUR/KRW'])
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)

        Returns:
            DataFrame (인덱스: 날짜, 컬럼: 각 통화쌍)

        Raises:
            ValidationError: 입력 데이터 검증 실패
            APIConnectionError: 서버 연결 실패
            APITimeoutError: 요청 타임아웃
            DataNotFoundError: 데이터 없음
        """
        validate_date_range(start_date, end_date)
        logger.debug(f"Fetching exchange rates: pairs={pairs}, start={start_date}, end={end_date}")
        
        return self._get_timeseries_data(
            endpoint='api/exchange-rates',
            param_name='pairs',
            items=pairs,
            start_date=start_date,
            end_date=end_date,
            data_type='환율'
        )

    def get_statistics(self,
                      data_type: str,
                      items: List[str],
                      start_date: str,
                      end_date: str) -> Dict[str, Dict[str, float]]:
        """
        통계 데이터 조회

        Args:
            data_type: 'interest_rate' or 'exchange_rate'
            items: 항목 리스트
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)

        Returns:
            {item: {stat_name: value}} 딕셔너리

        Raises:
            ValidationError: 입력 데이터 검증 실패
            APIConnectionError: 서버 연결 실패
            APITimeoutError: 요청 타임아웃
        """
        validate_date_range(start_date, end_date)
        logger.debug(f"Fetching statistics: type={data_type}, items={items}")
        
        try:
            params = {
                'data_type': data_type,
                'items': ','.join(items),
                'start_date': start_date,
                'end_date': end_date
            }

            response = self.session.get(
                f"{self.base_url}/api/statistics",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            validate_api_response(result)

            if result['status'] == 'success':
                logger.info(f"Successfully fetched statistics for {len(items)} items")
                return result['data']
            else:
                error_msg = result.get('message', 'Unknown error')
                logger.error(f"API returned error: {error_msg}")
                raise APIResponseError(error_msg)

        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise APIConnectionError(f"서버에 연결할 수 없습니다: {self.base_url}")
        except requests.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise APITimeoutError(f"요청 시간 초과 ({self.timeout}초)")
        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise APIResponseError(f"HTTP 오류: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise APIResponseError(f"예상치 못한 오류: {e}")

    def _get_timeseries_data(self,
                            endpoint: str,
                            param_name: str,
                            items: List[str],
                            start_date: str,
                            end_date: str,
                            data_type: str) -> pd.DataFrame:
        """
        시계열 데이터 조회 공통 로직

        Args:
            endpoint: API 엔드포인트
            param_name: 파라미터 이름 ('items' or 'pairs')
            items: 항목 리스트
            start_date: 시작 날짜
            end_date: 종료 날짜
            data_type: 데이터 타입 (로깅용)

        Returns:
            DataFrame

        Raises:
            APIConnectionError: 서버 연결 실패
            APITimeoutError: 요청 타임아웃
            APIResponseError: 잘못된 응답
            DataNotFoundError: 데이터 없음
        """
        try:
            params = {
                param_name: ','.join(items),
                'start_date': start_date,
                'end_date': end_date
            }

            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            validate_api_response(result)

            if result['status'] == 'success':
                df = self._parse_timeseries_response(result['data'])
                
                if df.empty:
                    logger.warning(f"No data returned for {data_type}")
                    raise DataNotFoundError(f"{data_type} 데이터를 찾을 수 없습니다.")
                
                logger.info(f"Successfully fetched {data_type} data: {df.shape}")
                return df
            else:
                error_msg = result.get('message', 'Unknown error')
                logger.error(f"API returned error: {error_msg}")
                raise APIResponseError(error_msg)

        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise APIConnectionError(f"서버에 연결할 수 없습니다: {self.base_url}")
        except requests.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise APITimeoutError(f"요청 시간 초과 ({self.timeout}초)")
        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise APIResponseError(f"HTTP 오류: {e}")
        except Exception as e:
            if isinstance(e, (APIConnectionError, APITimeoutError, APIResponseError, DataNotFoundError)):
                raise
            logger.error(f"Unexpected error: {e}")
            raise APIResponseError(f"예상치 못한 오류: {e}")

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
        try:
            dates = pd.to_datetime(data['dates'])
            series_data = {}

            for item_name, item_data in data['series'].items():
                series_data[item_name] = item_data['values']

            df = pd.DataFrame(series_data, index=dates)
            return df
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse timeseries response: {e}")
            raise APIResponseError(f"응답 파싱 실패: {e}")

    def close(self) -> None:
        """세션 종료"""
        self.session.close()
        logger.info("API Client session closed")


# Mock 클라이언트 (FastAPI 서버 없이 테스트용)
class MockAPIClient(APIClient):
    """테스트용 Mock 클라이언트"""

    def __init__(self):
        # 부모 클래스의 __init__ 호출하지 않음
        self.base_url = "mock://localhost"
        self.timeout = 30
        logger.info("Mock API Client initialized")

    def get_categories(self) -> Dict[str, Dict[str, List[str]]]:
        """Mock 카테고리 데이터"""
        logger.debug("Returning mock categories")
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

        validate_date_range(start_date, end_date)
        logger.debug(f"Generating mock interest rates: {len(items)} items")

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

        validate_date_range(start_date, end_date)
        logger.debug(f"Generating mock exchange rates: {len(pairs)} pairs")

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

    def get_statistics(self, data_type: str, items: List[str], start_date: str, end_date: str) -> Dict[str, Dict[str, float]]:
        """Mock 통계 데이터"""
        logger.debug(f"Generating mock statistics for {len(items)} items")
        
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

    # 로깅 설정
    from src.logging_config import setup_logging
    setup_logging('INFO')

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
