"""
데이터 로드 관련 콜백
"""

from dash import Input, Output, State
import pandas as pd
from app.utils.data_utils import classify_items_by_type


def register_data_callbacks(app, client, categories):
    """
    데이터 로드 관련 콜백 등록

    Args:
        app: Dash 앱 인스턴스
        client: API 클라이언트
        categories: 카테고리 딕셔너리
    """

    # 콜백: 데이터 로드
    @app.callback(
        [Output('data-store', 'data'),
         Output('stats-store', 'data')],
        Input('load-button', 'n_clicks'),
        [State('data-type-dropdown', 'value'),
         State('item-dropdown', 'value'),
         State('start-date', 'date'),
         State('end-date', 'date')],
        prevent_initial_call=True
    )
    def load_data(n_clicks, data_type, items, start_date, end_date):
        if not items:
            return None, None

        # 항목별로 금리/환율 분류
        if data_type == 'all':
            interest_items, exchange_items = classify_items_by_type(items, categories)
        elif data_type == 'interest_rate':
            interest_items = items
            exchange_items = []
        else:  # exchange_rate
            interest_items = []
            exchange_items = items

        # 데이터 조회 및 병합
        dfs = []
        all_stats = {}

        if interest_items:
            df_interest = client.get_interest_rates(interest_items, start_date, end_date)
            dfs.append(df_interest)
            stats_interest = client.get_statistics('interest_rate', interest_items, start_date, end_date)
            all_stats.update(stats_interest)

        if exchange_items:
            df_exchange = client.get_exchange_rates(exchange_items, start_date, end_date)
            dfs.append(df_exchange)
            stats_exchange = client.get_statistics('exchange_rate', exchange_items, start_date, end_date)
            all_stats.update(stats_exchange)

        # DataFrame 병합
        if len(dfs) > 1:
            df = pd.concat(dfs, axis=1)
        elif len(dfs) == 1:
            df = dfs[0]
        else:
            return None, None

        # JSON으로 변환
        return df.to_json(date_format='iso'), all_stats
