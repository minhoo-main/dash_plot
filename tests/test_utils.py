"""
유틸리티 함수 테스트
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.data_utils import (
    normalize_data,
    calculate_spread,
    calculate_spread_statistics,
    classify_items_by_type
)
from app.utils.chart_utils import should_use_secondary_axis


def test_normalize_data():
    """데이터 정규화 테스트"""
    print("Testing normalize_data...")

    # 테스트 데이터 생성
    df = pd.DataFrame({
        'A': [100, 110, 120, 130],
        'B': [50, 55, 60, 65]
    })

    # 정규화
    df_normalized = normalize_data(df)

    # 첫 번째 값이 100인지 확인
    assert df_normalized['A'].iloc[0] == 100, "First value of A should be 100"
    assert df_normalized['B'].iloc[0] == 100, "First value of B should be 100"

    # 비율이 유지되는지 확인
    assert abs(df_normalized['A'].iloc[1] - 110) < 0.01, "A[1] should be ~110"
    assert abs(df_normalized['B'].iloc[1] - 110) < 0.01, "B[1] should be ~110"

    print("✓ normalize_data passed")


def test_calculate_spread():
    """스프레드 계산 테스트"""
    print("Testing calculate_spread...")

    # 테스트 데이터 생성
    df = pd.DataFrame({
        'US_10Y': [4.0, 4.1, 4.2],
        'KR_10Y': [3.5, 3.6, 3.7]
    })

    # 차이 계산
    spread, label, yaxis = calculate_spread(df, 'US_10Y', 'KR_10Y', 'subtract')
    assert label == "US_10Y - KR_10Y", f"Label should be 'US_10Y - KR_10Y', got {label}"
    assert yaxis == "차이", f"Y-axis should be '차이', got {yaxis}"
    assert abs(spread.iloc[0] - 0.5) < 0.01, "Spread[0] should be ~0.5"

    # 비율 계산
    spread, label, yaxis = calculate_spread(df, 'US_10Y', 'KR_10Y', 'divide')
    assert label == "US_10Y / KR_10Y", f"Label should be 'US_10Y / KR_10Y', got {label}"
    assert yaxis == "비율", f"Y-axis should be '비율', got {yaxis}"
    assert abs(spread.iloc[0] - (4.0 / 3.5)) < 0.01, "Spread[0] should be ~1.14"

    print("✓ calculate_spread passed")


def test_calculate_spread_statistics():
    """스프레드 통계 계산 테스트"""
    print("Testing calculate_spread_statistics...")

    # 테스트 데이터
    spread = pd.Series([0.5, 0.6, 0.7, 0.8, 0.9])

    stats = calculate_spread_statistics(spread)

    # 필수 키 확인
    required_keys = ['현재값', '평균', '표준편차', '최소', '최대', '중앙값', '25% 분위', '75% 분위']
    for key in required_keys:
        assert key in stats, f"Missing key: {key}"

    # 값 확인
    assert stats['현재값'] == 0.9, "Current value should be 0.9"
    assert abs(stats['평균'] - 0.7) < 0.01, "Mean should be ~0.7"
    assert stats['최소'] == 0.5, "Min should be 0.5"
    assert stats['최대'] == 0.9, "Max should be 0.9"

    print("✓ calculate_spread_statistics passed")


def test_classify_items_by_type():
    """항목 분류 테스트"""
    print("Testing classify_items_by_type...")

    categories = {
        '금리': {
            '국고채': ['US_10Y', 'KR_10Y'],
            '중앙은행': ['FED_RATE', 'BOK_RATE']
        },
        '환율': {
            '주요통화': ['USD/KRW', 'EUR/KRW']
        }
    }

    items = ['US_10Y', 'USD/KRW', 'FED_RATE']

    interest_items, exchange_items = classify_items_by_type(items, categories)

    assert 'US_10Y' in interest_items, "US_10Y should be in interest_items"
    assert 'FED_RATE' in interest_items, "FED_RATE should be in interest_items"
    assert 'USD/KRW' in exchange_items, "USD/KRW should be in exchange_items"

    print("✓ classify_items_by_type passed")


def test_should_use_secondary_axis():
    """보조 축 사용 여부 판단 테스트"""
    print("Testing should_use_secondary_axis...")

    # 스케일 차이가 큰 경우
    df_large_diff = pd.DataFrame({
        'A': [1000, 1100, 1200],
        'B': [10, 11, 12]
    })

    use_secondary, sorted_cols = should_use_secondary_axis(df_large_diff)
    assert use_secondary == True, "Should use secondary axis for large scale difference"

    # 스케일 차이가 작은 경우
    df_small_diff = pd.DataFrame({
        'A': [100, 110, 120],
        'B': [90, 100, 110]
    })

    use_secondary, sorted_cols = should_use_secondary_axis(df_small_diff)
    assert use_secondary == False, "Should not use secondary axis for small scale difference"

    print("✓ should_use_secondary_axis passed")


if __name__ == '__main__':
    print("\n" + "="*50)
    print("Running utility function tests...")
    print("="*50 + "\n")

    try:
        test_normalize_data()
        test_calculate_spread()
        test_calculate_spread_statistics()
        test_classify_items_by_type()
        test_should_use_secondary_axis()

        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("="*50 + "\n")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
