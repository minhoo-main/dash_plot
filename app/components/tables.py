"""
테이블 컴포넌트
"""

from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from config import STATS_COLUMN_NAMES, SPREAD_STATS_KEYS


def create_statistics_table(stats: dict) -> html.Div:
    """
    통계 테이블 생성

    Args:
        stats: 통계 데이터 딕셔너리

    Returns:
        Dash HTML 컴포넌트
    """
    if not stats:
        return html.Div()

    # 통계 데이터프레임 생성
    stats_df = pd.DataFrame(stats).T
    stats_df = stats_df.round(4)

    # 테이블 생성
    table = dbc.Table([
        html.Thead(
            html.Tr([html.Th("항목")] +
                   [html.Th(STATS_COLUMN_NAMES.get(col, col))
                    for col in stats_df.columns if col != 'unit'])
        ),
        html.Tbody([
            html.Tr([html.Td(idx)] +
                   [html.Td(f"{val:.4f}" if isinstance(val, (int, float)) else val)
                    for col, val in row.items() if col != 'unit'])
            for idx, row in stats_df.iterrows()
        ])
    ], bordered=True, hover=True, striped=True, responsive=True, size='sm')

    return table


def create_spread_statistics_table(stats_data: dict, spread_label: str = "스프레드") -> html.Div:
    """
    스프레드 통계 테이블 생성 (가로 형식 - 시계열 차트와 동일)

    Args:
        stats_data: 통계 데이터 딕셔너리
        spread_label: 스프레드 항목명

    Returns:
        Dash HTML 컴포넌트
    """
    # DataFrame으로 변환 (시계열 차트 통계와 동일한 형태)
    stats_df = pd.DataFrame({spread_label: stats_data}).T
    stats_df = stats_df.round(4)

    # 테이블 생성 (가로 형태)
    stats_table = html.Div([
        dbc.Table([
            html.Thead(
                html.Tr([html.Th("항목")] +
                       [html.Th(STATS_COLUMN_NAMES.get(col, col))
                        for col in stats_df.columns])
            ),
            html.Tbody([
                html.Tr([html.Td(idx)] +
                       [html.Td(f"{val:.4f}" if isinstance(val, (int, float)) else val)
                        for col, val in row.items()])
                for idx, row in stats_df.iterrows()
            ])
        ], bordered=True, striped=True, hover=True, responsive=True, size='sm',
           style={'marginTop': '10px'})
    ])

    return stats_table
