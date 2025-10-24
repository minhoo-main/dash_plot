"""
금리/환율 데이터 시계열 분석 Dash 애플리케이션
FastAPI 서버에서 데이터 조회
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 로컬 모듈 import
import sys
sys.path.append('src')
from api_client import MockAPIClient  # 실제 서버 사용 시: APIClient

# Dash 앱 초기화
# 오프라인 환경을 위해 로컬 Bootstrap CSS 사용
# assets/bootstrap.min.css 파일이 자동으로 로드됨
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True
)

# API 클라이언트 초기화
# 실제 FastAPI 서버 사용 시:
# client = APIClient(base_url="http://localhost:8000")
client = MockAPIClient()  # 테스트용 Mock 클라이언트

# 카테고리 데이터 로드
CATEGORIES = client.get_categories()

# 레이아웃
app.layout = dbc.Container([
    # 헤더
    html.Div([
        html.H1("📊 금리/환율 데이터 분석 대시보드", className="display-4"),
        html.P("Oracle DB 기반 시계열 데이터 분석 및 시각화", className="lead")
    ], className="header"),

    # 컨트롤 패널
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # 데이터 타입 선택
                dbc.Col([
                    html.Label("데이터 타입", className="control-label"),
                    dcc.Dropdown(
                        id='data-type-dropdown',
                        options=[
                            {'label': '📈 금리', 'value': 'interest_rate'},
                            {'label': '💱 환율', 'value': 'exchange_rate'},
                            {'label': '📊 전체', 'value': 'all'}
                        ],
                        value='all',
                        clearable=False
                    )
                ], width=2),

                # 카테고리 선택
                dbc.Col([
                    html.Label("카테고리", className="control-label"),
                    dcc.Dropdown(
                        id='category-dropdown',
                        multi=True,
                        placeholder="카테고리 선택..."
                    )
                ], width=2),

                # 항목 선택
                dbc.Col([
                    html.Label("항목", className="control-label"),
                    dcc.Dropdown(
                        id='item-dropdown',
                        multi=True,
                        placeholder="항목 선택..."
                    )
                ], width=2),

                # 날짜 범위 (시작일 + 종료일 + 빠른선택)
                dbc.Col([
                    html.Label("기간", className="control-label"),
                    html.Div([
                        dcc.DatePickerSingle(
                            id='start-date',
                            date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                            display_format='YYYY-MM-DD',
                            style={'display': 'inline-block', 'marginRight': '5px'}
                        ),
                        html.Span("~", style={'display': 'inline-block', 'margin': '0 5px'}),
                        dcc.DatePickerSingle(
                            id='end-date',
                            date=datetime.now().strftime('%Y-%m-%d'),
                            display_format='YYYY-MM-DD',
                            style={'display': 'inline-block', 'marginLeft': '5px'}
                        ),
                        dbc.ButtonGroup([
                            dbc.Button("1Y", id="period-1y", size="sm", outline=True, color="secondary", style={'marginLeft': '10px'}),
                            dbc.Button("3Y", id="period-3y", size="sm", outline=True, color="secondary"),
                            dbc.Button("5Y", id="period-5y", size="sm", outline=True, color="secondary"),
                            dbc.Button("10Y", id="period-10y", size="sm", outline=True, color="secondary"),
                        ], size="sm", style={'display': 'inline-block', 'marginLeft': '10px'})
                    ])
                ], width=4),

                # 데이터 로드 버튼
                dbc.Col([
                    html.Label("\u00a0", className="control-label"),
                    dbc.Button(
                        "데이터 로드",
                        id="load-button",
                        color="primary",
                        size="lg",
                        className="w-100"
                    )
                ], width=2),
            ]),
        ])
    ], className="control-panel mb-4"),

    # 로딩 인디케이터
    dcc.Loading(
        id="loading",
        type="default",
        children=[
            # 메인 시계열 차트 (히스토그램 포함)
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H4("시계열 차트", className="card-header", style={'display': 'inline-block'}),
                        dbc.Checklist(
                            id='normalize-toggle',
                            options=[{'label': ' 정규화 (시작=100)', 'value': 'normalize'}],
                            value=[],
                            inline=True,
                            switch=True,
                            style={'display': 'inline-block', 'marginLeft': '20px', 'verticalAlign': 'middle'}
                        )
                    ]),
                    dcc.Graph(id='timeseries-chart', config={'displayModeBar': True}),
                    html.Div(id='statistics-table', className="mt-3")
                ])
            ], className="chart-container mb-4"),

            # 스프레드 차트 (두 항목 선택 시)
            html.Div(id='spread-section', children=[
                dbc.Card([
                    dbc.CardBody([
                        html.H4("스프레드 차트", className="card-header"),
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("기준 항목 (분자)", className="control-label"),
                                    dcc.Dropdown(id='spread-item1', placeholder="항목 선택...")
                                ], md=3),
                                dbc.Col([
                                    html.Label("비교 항목 (분모)", className="control-label"),
                                    dcc.Dropdown(id='spread-item2', placeholder="항목 선택...")
                                ], md=3),
                                dbc.Col([
                                    html.Label("연산", className="control-label"),
                                    dcc.Dropdown(
                                        id='spread-operation',
                                        options=[
                                            {'label': '차이 (A - B)', 'value': 'subtract'},
                                            {'label': '비율 (A / B)', 'value': 'divide'},
                                        ],
                                        value='subtract',
                                        clearable=False
                                    )
                                ], md=2),
                                dbc.Col([
                                    html.Label("\u00a0", className="control-label"),
                                    dbc.Button("계산", id="calc-spread-button", color="success", className="w-100")
                                ], md=2),
                            ], className="mb-3"),
                        ]),
                        dcc.Graph(id='spread-chart'),
                        html.Div(id='spread-stats', className="mt-3")
                    ])
                ], className="chart-container mb-4")
            ], style={'display': 'none'}),

        ]
    ),

    # 데이터 저장소
    dcc.Store(id='data-store'),
    dcc.Store(id='stats-store'),

], fluid=True, style={'padding': '0'})


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

    if button_id == 'period-1y':
        new_start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        active_buttons[0] = False
        button_colors[0] = 'primary'
    elif button_id == 'period-3y':
        new_start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y-%m-%d')
        active_buttons[1] = False
        button_colors[1] = 'primary'
    elif button_id == 'period-5y':
        new_start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        active_buttons[2] = False
        button_colors[2] = 'primary'
    elif button_id == 'period-10y':
        new_start_date = (datetime.now() - timedelta(days=365*10)).strftime('%Y-%m-%d')
        active_buttons[3] = False
        button_colors[3] = 'primary'

    return new_start_date, *active_buttons, *button_colors


# 콜백: 카테고리 드롭다운 업데이트
@app.callback(
    Output('category-dropdown', 'options'),
    Input('data-type-dropdown', 'value')
)
def update_category_dropdown(data_type):
    if data_type == 'interest_rate':
        categories = CATEGORIES['금리']
    elif data_type == 'exchange_rate':
        categories = CATEGORIES['환율']
    else:  # 'all'
        # 금리와 환율 모두 표시
        all_categories = {}
        all_categories.update(CATEGORIES['금리'])
        all_categories.update(CATEGORIES['환율'])
        categories = all_categories

    return [{'label': cat, 'value': cat} for cat in categories.keys()]


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
        all_categories = CATEGORIES['금리']
    elif data_type == 'exchange_rate':
        all_categories = CATEGORIES['환율']
    else:  # 'all'
        # 금리와 환율 모두 통합
        all_categories = {}
        all_categories.update(CATEGORIES['금리'])
        all_categories.update(CATEGORIES['환율'])

    items = []
    for cat in selected_categories:
        if cat in all_categories:
            items.extend(all_categories[cat])

    return [{'label': item, 'value': item} for item in items]


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
    interest_items = []
    exchange_items = []

    if data_type == 'all':
        # 전체 카테고리에서 항목 분류
        all_interest_items = []
        for cat_items in CATEGORIES['금리'].values():
            all_interest_items.extend(cat_items)

        all_exchange_items = []
        for cat_items in CATEGORIES['환율'].values():
            all_exchange_items.extend(cat_items)

        for item in items:
            if item in all_interest_items:
                interest_items.append(item)
            elif item in all_exchange_items:
                exchange_items.append(item)
    elif data_type == 'interest_rate':
        interest_items = items
    else:  # exchange_rate
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


# 콜백: 스프레드 섹션 표시 여부
@app.callback(
    [Output('spread-section', 'style'),
     Output('spread-item1', 'options'),
     Output('spread-item2', 'options')],
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_spread_section(data_json):
    if not data_json:
        return {'display': 'none'}, [], []

    df = pd.read_json(data_json)

    # 2개 이상의 항목이 있을 때만 스프레드 섹션 표시
    if len(df.columns) < 2:
        return {'display': 'none'}, [], []

    options = [{'label': col, 'value': col} for col in df.columns]
    return {'display': 'block'}, options, options


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
        df_plot = df.copy()
        for col in df_plot.columns:
            first_val = df_plot[col].iloc[0]
            if first_val != 0:
                df_plot[col] = (df_plot[col] / first_val) * 100
    else:
        df_plot = df

    # 정규화되면 단일 축 사용, 아니면 스케일 차이 확인
    if is_normalized:
        use_secondary_axis = False
    else:
        # 스케일 차이 확인 (중앙값 기준으로 판단)
        medians = [df_plot[col].median() for col in df_plot.columns]
        max_median = max(medians) if medians else 1
        min_median = min([m for m in medians if m > 0]) if any(m > 0 for m in medians) else 1

        # 중앙값 차이가 5배 이상이면 보조 축 사용
        use_secondary_axis = (max_median / min_median > 5) if min_median > 0 and len(df_plot.columns) >= 2 else False

        print(f"DEBUG: medians={medians}, max={max_median}, min={min_median}, use_secondary={use_secondary_axis}")

    # 히스토그램이 있는 서브플롯 생성
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.85, 0.15],
        horizontal_spacing=0.02,
        specs=[[{"type": "xy"}, {"type": "bar"}]],
        shared_yaxes=True
    )

    if use_secondary_axis and len(df_plot.columns) >= 2:
        # 범위가 큰 항목과 작은 항목 분리
        sorted_cols = sorted(df_plot.columns, key=lambda x: df_plot[x].max() - df_plot[x].min(), reverse=True)

        # 첫 번째 항목은 주 축
        col = sorted_cols[0]
        fig.add_trace(go.Scatter(
            x=df_plot.index,
            y=df_plot[col],
            mode='lines',
            name=col,
            line=dict(width=2),
            yaxis='y',
            hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.2f}<extra></extra>'
        ), row=1, col=1)

        # 나머지는 보조 축
        for col in sorted_cols[1:]:
            fig.add_trace(go.Scatter(
                x=df_plot.index,
                y=df_plot[col],
                mode='lines',
                name=col,
                line=dict(width=2),
                yaxis='y3',
                hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.2f}<extra></extra>'
            ), row=1, col=1)

        # 히스토그램 추가 (세로 방향)
        for col in df_plot.columns:
            fig.add_trace(go.Histogram(
                y=df_plot[col],
                name=col,
                showlegend=False
            ), row=1, col=2)

        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            xaxis_title="날짜",
            yaxis=dict(
                title=sorted_cols[0],
                titlefont=dict(color='#1f77b4'),
                tickfont=dict(color='#1f77b4')
            ),
            yaxis3=dict(
                title="기타 항목",
                titlefont=dict(color='#ff7f0e'),
                tickfont=dict(color='#ff7f0e'),
                anchor='x',
                overlaying='y',
                side='right'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=0.85
            ),
            height=500,
            bargap=0.1
        )

        # X축 레이블 숨김
        fig.update_xaxes(title_text="", showticklabels=False, row=1, col=2)

    else:
        # 스케일 차이가 크지 않거나 정규화된 경우 단일 축 사용
        for col in df_plot.columns:
            fig.add_trace(go.Scatter(
                x=df_plot.index,
                y=df_plot[col],
                mode='lines',
                name=col,
                line=dict(width=2),
                hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.2f}<extra></extra>'
            ), row=1, col=1)

        # 히스토그램 추가
        for col in df_plot.columns:
            fig.add_trace(go.Histogram(
                y=df_plot[col],
                name=col,
                showlegend=False
            ), row=1, col=2)

        yaxis_title = "지수 (시작=100)" if is_normalized else "값"

        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            xaxis_title="날짜",
            yaxis_title=yaxis_title,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=0.85
            ),
            height=500,
            bargap=0.1
        )

        # X축 레이블 숨김
        fig.update_xaxes(title_text="", showticklabels=False, row=1, col=2)

    return fig


# 콜백: 스프레드 차트 및 통계
@app.callback(
    [Output('spread-chart', 'figure'),
     Output('spread-stats', 'children')],
    Input('calc-spread-button', 'n_clicks'),
    [State('data-store', 'data'),
     State('spread-item1', 'value'),
     State('spread-item2', 'value'),
     State('spread-operation', 'value')],
    prevent_initial_call=True
)
def update_spread_chart(n_clicks, data_json, item1, item2, operation):
    if not data_json or not item1 or not item2:
        return {}, html.Div()

    df = pd.read_json(data_json)

    # 스프레드 계산
    if operation == 'subtract':
        spread = df[item1] - df[item2]
        label = f"{item1} - {item2}"
        yaxis_title = "차이"
    else:  # divide
        spread = df[item1] / df[item2]
        label = f"{item1} / {item2}"
        yaxis_title = "비율"

    # 히스토그램이 있는 서브플롯 생성
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.85, 0.15],
        horizontal_spacing=0.02,
        specs=[[{"type": "scatter"}, {"type": "bar"}]],
        shared_yaxes=True
    )

    # 라인 플롯으로 변경
    fig.add_trace(go.Scatter(
        x=spread.index,
        y=spread,
        mode='lines',
        name=label,
        line=dict(width=2, color='rgb(0, 176, 80)'),
        hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.4f}<extra></extra>'
    ), row=1, col=1)

    # 히스토그램 추가
    fig.add_trace(go.Histogram(
        y=spread,
        name=label,
        showlegend=False,
        marker=dict(color='rgb(0, 176, 80)')
    ), row=1, col=2)

    # 평균선 추가
    mean_val = spread.mean()
    fig.add_hline(y=mean_val, line_dash="dash", line_color="red",
                  annotation_text=f"평균: {mean_val:.4f}",
                  annotation_position="right",
                  row=1, col=1)

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title="날짜",
        yaxis_title=yaxis_title,
        height=400,
        bargap=0.1
    )

    # X축 레이블 숨김
    fig.update_xaxes(title_text="", showticklabels=False, row=1, col=2)

    # 통계 정보 생성 (한 줄로 표시)
    stats_data = {
        '현재값': spread.iloc[-1],
        '평균': spread.mean(),
        '표준편차': spread.std(),
        '최소': spread.min(),
        '최대': spread.max(),
        '중앙값': spread.median(),
        '25% 분위': spread.quantile(0.25),
        '75% 분위': spread.quantile(0.75),
    }

    # 테이블 형태로 표시
    stats_table = html.Div([
        dbc.Table([
            html.Thead(
                html.Tr([html.Th(key) for key in stats_data.keys()])
            ),
            html.Tbody([
                html.Tr([html.Td(f"{val:.4f}") for val in stats_data.values()])
            ])
        ], bordered=True, striped=True, hover=True, size='sm', style={'marginTop': '10px'})
    ])

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

    # 통계 데이터프레임 생성
    stats_df = pd.DataFrame(stats).T
    stats_df = stats_df.round(4)

    # 한글 컬럼명
    column_names = {
        'current': '현재값',
        'mean': '평균',
        'std': '표준편차',
        'min': '최소',
        'max': '최대',
        'median': '중앙값',
        'q25': '25% 분위',
        'q75': '75% 분위',
        'change_1d': '1일 변화',
        'change_1w': '1주 변화',
        'change_1m': '1개월 변화',
        'pct_change_1d': '1일 변화율(%)',
    }

    # 테이블 생성
    table = dbc.Table([
        html.Thead(
            html.Tr([html.Th("항목")] + [html.Th(column_names.get(col, col)) for col in stats_df.columns if col != 'unit'])
        ),
        html.Tbody([
            html.Tr([html.Td(idx)] + [html.Td(f"{val:.4f}" if isinstance(val, (int, float)) else val)
                                       for col, val in row.items() if col != 'unit'])
            for idx, row in stats_df.iterrows()
        ])
    ], bordered=True, hover=True, striped=True, responsive=True, size='sm')

    return table


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
