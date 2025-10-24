"""
차트 업데이트 관련 콜백
"""

from dash import Input, Output, State, html
import pandas as pd
from app.components.charts import create_timeseries_chart, create_spread_chart
from app.components.tables import create_statistics_table, create_spread_statistics_table
from app.utils.data_utils import normalize_data, calculate_spread, calculate_spread_statistics


def register_chart_callbacks(app):
    """
    차트 관련 콜백 등록

    Args:
        app: Dash 앱 인스턴스
    """

    # 콜백: 시계열 차트
    @app.callback(
        Output('timeseries-chart', 'figure'),
        [Input('data-store', 'data'),
         Input('normalize-toggle', 'value')],
        prevent_initial_call=True
    )
    def update_timeseries_chart(data_json, normalize):
        if not data_json:
            return {}

        df = pd.read_json(data_json)

        # 정규화 옵션
        is_normalized = 'normalize' in (normalize or [])

        # 정규화: 첫 번째 값을 100으로
        if is_normalized:
            df_plot = normalize_data(df)
        else:
            df_plot = df

        return create_timeseries_chart(df_plot, is_normalized)

    # 콜백: 스프레드 차트 및 통계 (자동 업데이트)
    @app.callback(
        [Output('spread-chart', 'figure'),
         Output('spread-stats', 'children')],
        [Input('spread-item1', 'value'),
         Input('spread-item2', 'value'),
         Input('spread-operation', 'value')],
        State('data-store', 'data'),
        prevent_initial_call=True
    )
    def update_spread_chart(item1, item2, operation, data_json):
        if not data_json or not item1 or not item2:
            return {}, html.Div()

        df = pd.read_json(data_json)

        # 스프레드 계산
        spread, label, yaxis_title = calculate_spread(df, item1, item2, operation)

        # 차트 생성
        fig = create_spread_chart(spread, label, yaxis_title)

        # 통계 정보 생성
        stats_data = calculate_spread_statistics(spread)
        stats_table = create_spread_statistics_table(stats_data, spread_label=label)

        return fig, stats_table

    # 콜백: 통계표
    @app.callback(
        Output('statistics-table', 'children'),
        Input('stats-store', 'data'),
        prevent_initial_call=True
    )
    def update_statistics_table(stats):
        if not stats:
            return html.Div()

        return create_statistics_table(stats)
