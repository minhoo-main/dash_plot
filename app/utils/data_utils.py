"""
데이터 처리 유틸리티 함수
"""

import pandas as pd
from typing import Tuple


def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    데이터를 정규화 (첫 번째 값을 100으로)

    Args:
        df: 원본 DataFrame

    Returns:
        정규화된 DataFrame
    """
    df_normalized = df.copy()
    for col in df_normalized.columns:
        first_val = df_normalized[col].iloc[0]
        if first_val != 0:
            df_normalized[col] = (df_normalized[col] / first_val) * 100
    return df_normalized


def calculate_spread(df: pd.DataFrame,
                     item1: str,
                     item2: str,
                     operation: str) -> Tuple[pd.Series, str, str]:
    """
    두 항목 간의 스프레드 계산

    Args:
        df: 데이터 DataFrame
        item1: 기준 항목 (분자)
        item2: 비교 항목 (분모)
        operation: 연산 타입 ('subtract' 또는 'divide')

    Returns:
        (스프레드 Series, 라벨, y축 제목) 튜플
    """
    if operation == 'subtract':
        spread = df[item1] - df[item2]
        label = f"{item1} - {item2}"
        yaxis_title = "차이"
    else:  # divide
        spread = df[item1] / df[item2]
        label = f"{item1} / {item2}"
        yaxis_title = "비율"

    return spread, label, yaxis_title


def calculate_spread_statistics(spread: pd.Series) -> dict:
    """
    스프레드 통계 계산 (시계열 차트 통계와 동일한 형태)

    Args:
        spread: 스프레드 Series

    Returns:
        통계 딕셔너리
    """
    data = spread.dropna()

    return {
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
        'change_3m': float(data.iloc[-1] - data.iloc[-60]) if len(data) > 60 else 0,
    }


def classify_items_by_type(items: list, categories: dict) -> Tuple[list, list]:
    """
    항목들을 금리/환율로 분류

    Args:
        items: 항목 리스트
        categories: 카테고리 딕셔너리

    Returns:
        (금리 항목 리스트, 환율 항목 리스트) 튜플
    """
    interest_items = []
    exchange_items = []

    # 전체 금리/환율 항목 목록 생성
    all_interest_items = []
    for cat_items in categories.get('금리', {}).values():
        all_interest_items.extend(cat_items)

    all_exchange_items = []
    for cat_items in categories.get('환율', {}).values():
        all_exchange_items.extend(cat_items)

    # 항목 분류
    for item in items:
        if item in all_interest_items:
            interest_items.append(item)
        elif item in all_exchange_items:
            exchange_items.append(item)

    return interest_items, exchange_items
