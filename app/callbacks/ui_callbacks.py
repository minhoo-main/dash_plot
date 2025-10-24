"""
UI 상태 관련 콜백
"""

import dash
from dash import Input, Output, State
from datetime import datetime, timedelta
from config import PERIOD_BUTTONS


def register_ui_callbacks(app, categories):
    """
    UI 관련 콜백 등록

    Args:
        app: Dash 앱 인스턴스
        categories: 카테고리 딕셔너리
    """

    # 콜백: 기간 빠른 선택
    @app.callback(
        [Output('start-date', 'date'),
         Output('period-1y', 'outline'),
         Output('period-3y', 'outline'),
         Output('period-5y', 'outline'),
         Output('period-10y', 'outline'),
         Output('period-1y', 'color'),
         Output('period-3y', 'color'),
         Output('period-5y', 'color'),
         Output('period-10y', 'color')],
        [Input('period-1y', 'n_clicks'),
         Input('period-3y', 'n_clicks'),
         Input('period-5y', 'n_clicks'),
         Input('period-10y', 'n_clicks'),
         Input('start-date', 'date')],
        [State('end-date', 'date')],
        prevent_initial_call=True
    )
    def update_period(n1, n3, n5, n10, start_date, end_date):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # 날짜가 수동으로 변경된 경우 모든 버튼 비활성화
        if button_id == 'start-date':
            return dash.no_update, True, True, True, True, 'secondary', 'secondary', 'secondary', 'secondary'

        # 버튼 클릭 시
        new_start_date = None
        active_buttons = [True, True, True, True]
        button_colors = ['secondary', 'secondary', 'secondary', 'secondary']

        # 버튼별 처리
        for idx, btn in enumerate(PERIOD_BUTTONS):
            if button_id == btn['id']:
                new_start_date = (datetime.now() - timedelta(days=btn['days'])).strftime('%Y-%m-%d')
                active_buttons[idx] = False
                button_colors[idx] = 'primary'
                break

        return new_start_date, *active_buttons, *button_colors

    # 콜백: 카테고리 드롭다운 업데이트
    @app.callback(
        Output('category-dropdown', 'options'),
        Input('data-type-dropdown', 'value')
    )
    def update_category_dropdown(data_type):
        if data_type == 'interest_rate':
            cats = categories['금리']
        elif data_type == 'exchange_rate':
            cats = categories['환율']
        else:  # 'all'
            cats = {}
            cats.update(categories['금리'])
            cats.update(categories['환율'])

        return [{'label': cat, 'value': cat} for cat in cats.keys()]

    # 콜백: 항목 드롭다운 업데이트
    @app.callback(
        Output('item-dropdown', 'options'),
        [Input('data-type-dropdown', 'value'),
         Input('category-dropdown', 'value')]
    )
    def update_item_dropdown(data_type, selected_categories):
        if not selected_categories:
            return []

        if data_type == 'interest_rate':
            all_cats = categories['금리']
        elif data_type == 'exchange_rate':
            all_cats = categories['환율']
        else:  # 'all'
            all_cats = {}
            all_cats.update(categories['금리'])
            all_cats.update(categories['환율'])

        items = []
        for cat in selected_categories:
            if cat in all_cats:
                items.extend(all_cats[cat])

        return [{'label': item, 'value': item} for item in items]

    # 콜백: 스프레드 섹션 표시 여부
    @app.callback(
        [Output('spread-section', 'style'),
         Output('spread-item1', 'options'),
         Output('spread-item2', 'options')],
        Input('data-store', 'data'),
        prevent_initial_call=True
    )
    def update_spread_section(data_json):
        import pandas as pd

        if not data_json:
            return {'display': 'none'}, [], []

        df = pd.read_json(data_json)

        # 2개 이상의 항목이 있을 때만 스프레드 섹션 표시
        if len(df.columns) < 2:
            return {'display': 'none'}, [], []

        options = [{'label': col, 'value': col} for col in df.columns]
        return {'display': 'block'}, options, options
