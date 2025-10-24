"""
차트 유틸리티 함수
"""

import pandas as pd
from typing import Tuple
from config import SCALE_DIFF_THRESHOLD, CHART_COLORS


def should_use_secondary_axis(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    스케일 차이에 따라 보조 축 사용 여부 결정

    Args:
        df: 데이터 DataFrame

    Returns:
        (보조 축 사용 여부, 중앙값 기준 정렬된 컬럼 리스트) 튜플
    """
    if len(df.columns) < 2:
        return False, list(df.columns)

    # 중앙값 계산
    medians = [df[col].median() for col in df.columns]
    max_median = max(medians) if medians else 1
    min_median = min([m for m in medians if m > 0]) if any(m > 0 for m in medians) else 1

    # 중앙값 차이가 임계값 이상이면 보조 축 사용
    use_secondary = (max_median / min_median > SCALE_DIFF_THRESHOLD) if min_median > 0 else False

    # 범위 기준으로 컬럼 정렬
    sorted_cols = sorted(df.columns, key=lambda x: df[x].max() - df[x].min(), reverse=True)

    return use_secondary, sorted_cols


def get_chart_colors():
    """
    차트 색상 설정 반환

    Returns:
        색상 딕셔너리
    """
    return CHART_COLORS


def get_subplot_specs(has_histogram: bool = True):
    """
    서브플롯 사양 반환

    Args:
        has_histogram: 히스토그램 포함 여부

    Returns:
        서브플롯 사양 딕셔너리
    """
    if has_histogram:
        return {
            'rows': 1,
            'cols': 2,
            'column_widths': [0.85, 0.15],
            'horizontal_spacing': 0.02,
            'specs': [[{"type": "xy"}, {"type": "bar"}]],
            'shared_yaxes': True
        }
    else:
        return {
            'rows': 1,
            'cols': 1,
            'specs': [[{"type": "xy"}]]
        }
