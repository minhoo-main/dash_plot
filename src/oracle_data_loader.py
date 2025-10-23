"""
Oracle DB 금리/환율 데이터 로더
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import cx_Oracle
from sqlalchemy import create_engine, text
from db_config import DB_CONFIG, get_connection_string, CATEGORIES


class OracleDataLoader:
    """Oracle DB에서 금리/환율 데이터 로드"""

    def __init__(self):
        self.engine = None
        self.connection = None
        self.data = None

    def connect(self):
        """데이터베이스 연결"""
        try:
            # SQLAlchemy 엔진 생성
            connection_string = get_connection_string()
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()

    def load_interest_rates(self,
                           rate_types: List[str],
                           start_date: str,
                           end_date: str,
                           table_name: str = 'INTEREST_RATES') -> pd.DataFrame:
        """
        금리 데이터 로드

        Args:
            rate_types: 금리 타입 리스트 (예: ['US_10Y', 'KR_3Y'])
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            table_name: 테이블 이름

        Returns:
            DataFrame with columns: DATE_VALUE, RATE_TYPE, RATE_VALUE
        """
        if not self.connection:
            if not self.connect():
                return pd.DataFrame()

        # SQL 쿼리
        rate_types_str = "','".join(rate_types)
        query = f"""
            SELECT
                DATE_VALUE,
                RATE_TYPE,
                RATE_VALUE,
                CATEGORY
            FROM {table_name}
            WHERE RATE_TYPE IN ('{rate_types_str}')
              AND DATE_VALUE BETWEEN TO_DATE('{start_date}', 'YYYY-MM-DD')
                                 AND TO_DATE('{end_date}', 'YYYY-MM-DD')
            ORDER BY DATE_VALUE, RATE_TYPE
        """

        try:
            df = pd.read_sql(query, self.connection)
            df['DATE_VALUE'] = pd.to_datetime(df['DATE_VALUE'])
            self.data = df
            return df
        except Exception as e:
            print(f"Query error: {e}")
            return pd.DataFrame()

    def load_exchange_rates(self,
                           currency_pairs: List[str],
                           start_date: str,
                           end_date: str,
                           table_name: str = 'EXCHANGE_RATES') -> pd.DataFrame:
        """
        환율 데이터 로드

        Args:
            currency_pairs: 통화쌍 리스트 (예: ['USD/KRW', 'EUR/USD'])
            start_date: 시작 날짜
            end_date: 종료 날짜
            table_name: 테이블 이름

        Returns:
            DataFrame
        """
        if not self.connection:
            if not self.connect():
                return pd.DataFrame()

        pairs_str = "','".join(currency_pairs)
        query = f"""
            SELECT
                DATE_VALUE,
                CURRENCY_PAIR,
                RATE_VALUE,
                CATEGORY
            FROM {table_name}
            WHERE CURRENCY_PAIR IN ('{pairs_str}')
              AND DATE_VALUE BETWEEN TO_DATE('{start_date}', 'YYYY-MM-DD')
                                 AND TO_DATE('{end_date}', 'YYYY-MM-DD')
            ORDER BY DATE_VALUE, CURRENCY_PAIR
        """

        try:
            df = pd.read_sql(query, self.connection)
            df['DATE_VALUE'] = pd.to_datetime(df['DATE_VALUE'])
            self.data = df
            return df
        except Exception as e:
            print(f"Query error: {e}")
            return pd.DataFrame()

    def pivot_data(self, df: pd.DataFrame, data_type: str = 'interest_rate') -> pd.DataFrame:
        """
        데이터를 pivot하여 wide format으로 변환

        Args:
            df: 원본 데이터프레임
            data_type: 'interest_rate' or 'exchange_rate'

        Returns:
            Pivoted DataFrame (날짜가 인덱스, 각 타입/통화쌍이 컬럼)
        """
        if df.empty:
            return pd.DataFrame()

        if data_type == 'interest_rate':
            pivot_df = df.pivot(
                index='DATE_VALUE',
                columns='RATE_TYPE',
                values='RATE_VALUE'
            )
        else:  # exchange_rate
            pivot_df = df.pivot(
                index='DATE_VALUE',
                columns='CURRENCY_PAIR',
                values='RATE_VALUE'
            )

        return pivot_df

    def calculate_changes(self, df: pd.DataFrame, period: int = 1) -> pd.DataFrame:
        """
        변화량 계산

        Args:
            df: Pivoted 데이터프레임
            period: 비교 기간 (일)

        Returns:
            변화량 DataFrame
        """
        return df.diff(periods=period)

    def calculate_percentage_changes(self, df: pd.DataFrame, period: int = 1) -> pd.DataFrame:
        """
        퍼센트 변화율 계산

        Args:
            df: Pivoted 데이터프레임
            period: 비교 기간 (일)

        Returns:
            변화율 DataFrame (%)
        """
        return df.pct_change(periods=period) * 100

    def calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        기본 통계 지표 계산

        Args:
            df: Pivoted 데이터프레임

        Returns:
            {column: {stat_name: value}} 딕셔너리
        """
        stats = {}

        for col in df.columns:
            data = df[col].dropna()

            if len(data) == 0:
                continue

            stats[col] = {
                'current': data.iloc[-1] if len(data) > 0 else np.nan,
                'mean': data.mean(),
                'std': data.std(),
                'min': data.min(),
                'max': data.max(),
                'median': data.median(),
                'q25': data.quantile(0.25),
                'q75': data.quantile(0.75),
                'change_1d': data.iloc[-1] - data.iloc[-2] if len(data) > 1 else 0,
                'change_1w': data.iloc[-1] - data.iloc[-5] if len(data) > 5 else 0,
                'change_1m': data.iloc[-1] - data.iloc[-20] if len(data) > 20 else 0,
                'pct_change_1d': ((data.iloc[-1] - data.iloc[-2]) / data.iloc[-2] * 100) if len(data) > 1 and data.iloc[-2] != 0 else 0,
            }

        return stats

    def calculate_correlation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        상관계수 행렬 계산

        Args:
            df: Pivoted 데이터프레임

        Returns:
            상관계수 DataFrame
        """
        return df.corr()

    def resample_data(self, df: pd.DataFrame, freq: str = 'W') -> pd.DataFrame:
        """
        데이터 리샘플링

        Args:
            df: Pivoted 데이터프레임
            freq: 'D' (daily), 'W' (weekly), 'M' (monthly)

        Returns:
            리샘플링된 DataFrame
        """
        return df.resample(freq).last()


# 샘플 데이터 생성 함수 (Oracle DB가 없을 때 테스트용)
def generate_sample_data(data_type: str = 'interest_rate',
                        items: List[str] = None,
                        start_date: str = '2023-01-01',
                        end_date: str = '2024-10-23') -> pd.DataFrame:
    """
    샘플 데이터 생성 (Oracle DB 없이 테스트용)

    Args:
        data_type: 'interest_rate' or 'exchange_rate'
        items: 아이템 리스트
        start_date: 시작 날짜
        end_date: 종료 날짜

    Returns:
        샘플 DataFrame
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    if data_type == 'interest_rate':
        if items is None:
            items = ['US_10Y', 'KR_3Y', 'KR_10Y', 'FED_RATE']

        # 금리 샘플 데이터 (현실적인 범위)
        base_rates = {
            'US_10Y': 4.0,
            'KR_3Y': 3.2,
            'KR_10Y': 3.5,
            'FED_RATE': 5.25,
            'BOK_RATE': 3.5,
        }

        data = []
        for date in dates:
            for item in items:
                base = base_rates.get(item, 3.0)
                # 랜덤 워크로 금리 변동 시뮬레이션
                noise = np.random.normal(0, 0.02)
                value = base + noise

                data.append({
                    'DATE_VALUE': date,
                    'RATE_TYPE': item,
                    'RATE_VALUE': round(value, 4),
                    'CATEGORY': 'Government Bond' if '10Y' in item or '3Y' in item else 'Central Bank Rate'
                })

    else:  # exchange_rate
        if items is None:
            items = ['USD/KRW', 'EUR/KRW', 'JPY/KRW']

        # 환율 샘플 데이터
        base_rates = {
            'USD/KRW': 1350.0,
            'EUR/KRW': 1450.0,
            'JPY/KRW': 9.5,
            'CNY/KRW': 185.0,
        }

        data = []
        for date in dates:
            for item in items:
                base = base_rates.get(item, 1000.0)
                # 랜덤 워크
                noise = np.random.normal(0, base * 0.005)
                value = base + noise

                data.append({
                    'DATE_VALUE': date,
                    'CURRENCY_PAIR': item,
                    'RATE_VALUE': round(value, 2),
                    'CATEGORY': 'Major'
                })

    return pd.DataFrame(data)


if __name__ == "__main__":
    # 테스트 - 샘플 데이터 생성
    print("=== 샘플 금리 데이터 생성 ===")
    df_rates = generate_sample_data(
        data_type='interest_rate',
        items=['US_10Y', 'KR_3Y', 'FED_RATE'],
        start_date='2024-01-01',
        end_date='2024-10-23'
    )

    loader = OracleDataLoader()
    loader.data = df_rates

    # Pivot
    pivot_df = loader.pivot_data(df_rates, data_type='interest_rate')
    print("\nPivoted 데이터:")
    print(pivot_df.head())

    # 통계
    stats = loader.calculate_statistics(pivot_df)
    print("\n통계:")
    for item, stat in stats.items():
        print(f"\n{item}:")
        print(f"  현재값: {stat['current']:.4f}")
        print(f"  평균: {stat['mean']:.4f}")
        print(f"  1일 변화: {stat['change_1d']:+.4f}")

    print("\n=== 샘플 환율 데이터 생성 ===")
    df_fx = generate_sample_data(
        data_type='exchange_rate',
        items=['USD/KRW', 'EUR/KRW'],
        start_date='2024-01-01',
        end_date='2024-10-23'
    )
    print(df_fx.head())
