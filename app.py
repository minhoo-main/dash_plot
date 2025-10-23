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
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 로컬 모듈 import
import sys
sys.path.append('src')
from api_client import MockAPIClient  # 실제 서버 사용 시: APIClient

# Dash 앱 초기화
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
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
                            {'label': '💱 환율', 'value': 'exchange_rate'}
                        ],
                        value='interest_rate',
                        clearable=False
                    )
                ], md=2),

                # 카테고리 선택
                dbc.Col([
                    html.Label("카테고리", className="control-label"),
                    dcc.Dropdown(
                        id='category-dropdown',
                        multi=True,
                        placeholder="카테고리 선택..."
                    )
                ], md=3),

                # 항목 선택
                dbc.Col([
                    html.Label("항목", className="control-label"),
                    dcc.Dropdown(
                        id='item-dropdown',
                        multi=True,
                        placeholder="항목 선택..."
                    )
                ], md=3),

                # 날짜 범위
                dbc.Col([
                    html.Label("시작일", className="control-label"),
                    dcc.DatePickerSingle(
                        id='start-date',
                        date=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
                        display_format='YYYY-MM-DD'
                    )
                ], md=2),

                dbc.Col([
                    html.Label("종료일", className="control-label"),
                    dcc.DatePickerSingle(
                        id='end-date',
                        date=datetime.now().strftime('%Y-%m-%d'),
                        display_format='YYYY-MM-DD'
                    )
                ], md=2),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "📊 데이터 로드",
                        id="load-button",
                        color="primary",
                        size="lg",
                        className="w-100"
                    )
                ], md=3),
            ])
        ])
    ], className="control-panel mb-4"),

    # 로딩 인디케이터
    dcc.Loading(
        id="loading",
        type="default",
        children=[
            # 통계 카드
            html.Div(id='stats-cards', className="mb-4"),

            # 메인 시계열 차트
            dbc.Card([
                dbc.CardBody([
                    html.H4("시계열 차트", className="card-header"),
                    dcc.Graph(id='timeseries-chart', config={'displayModeBar': True})
                ])
            ], className="chart-container mb-4"),

            # 하단 차트 행
            dbc.Row([
                # 변화량 차트
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("일간 변화량", className="card-header"),
                            dcc.Graph(id='change-chart')
                        ])
                    ], className="chart-container")
                ], md=6),

                # 히스토그램
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("분포 (히스토그램)", className="card-header"),
                            dcc.Graph(id='histogram-chart')
                        ])
                    ], className="chart-container")
                ], md=6),
            ], className="mb-4"),

            # 상관관계 및 박스플롯
            dbc.Row([
                # 상관관계 히트맵
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("상관관계", className="card-header"),
                            dcc.Graph(id='correlation-chart')
                        ])
                    ], className="chart-container")
                ], md=6),

                # 박스플롯
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("박스플롯 (분산 비교)", className="card-header"),
                            dcc.Graph(id='boxplot-chart')
                        ])
                    ], className="chart-container")
                ], md=6),
            ], className="mb-4"),

            # 통계표
            dbc.Card([
                dbc.CardBody([
                    html.H5("기술 통계", className="card-header"),
                    html.Div(id='statistics-table')
                ])
            ], className="mb-4"),
        ]
    ),

    # 데이터 저장소
    dcc.Store(id='data-store'),
    dcc.Store(id='stats-store'),

], fluid=True, style={'padding': '0'})


# 콜백: 카테고리 드롭다운 업데이트
@app.callback(
    Output('category-dropdown', 'options'),
    Input('data-type-dropdown', 'value')
)
def update_category_dropdown(data_type):
    if data_type == 'interest_rate':
        categories = CATEGORIES['금리']
    else:
        categories = CATEGORIES['환율']

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
    else:
        all_categories = CATEGORIES['환율']

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

    # API 호출
    if data_type == 'interest_rate':
        df = client.get_interest_rates(items, start_date, end_date)
    else:
        df = client.get_exchange_rates(items, start_date, end_date)

    # 통계 조회
    stats = client.get_statistics(data_type, items, start_date, end_date)

    # JSON으로 변환
    return df.to_json(date_format='iso'), stats


# 콜백: 통계 카드 업데이트
@app.callback(
    Output('stats-cards', 'children'),
    Input('stats-store', 'data'),
    prevent_initial_call=True
)
def update_stats_cards(stats):
    if not stats:
        return html.Div()

    cards = []
    for item, stat in stats.items():
        # 변화량에 따른 색상
        change_class = "stats-positive" if stat['change_1d'] >= 0 else "stats-negative"
        change_icon = "↑" if stat['change_1d'] >= 0 else "↓"

        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(item, className="stats-label"),
                    html.H3(f"{stat['current']:.2f}", className="stats-value"),
                    html.P([
                        html.Span(f"{change_icon} {abs(stat['change_1d']):.2f} ({stat['pct_change_1d']:+.2f}%)",
                                 className=change_class),
                        html.Br(),
                        html.Small(f"평균: {stat['mean']:.2f} | 표준편차: {stat['std']:.2f}",
                                  className="text-muted")
                    ])
                ])
            ], className="stats-card")
        ], md=6, lg=3)
        cards.append(card)

    return dbc.Row(cards)


# 콜백: 시계열 차트
@app.callback(
    Output('timeseries-chart', 'figure'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_timeseries_chart(data_json):
    if not data_json:
        return {}

    df = pd.read_json(data_json)

    fig = go.Figure()

    for col in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col,
            line=dict(width=2),
            hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.2f}<extra></extra>'
        ))

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title="날짜",
        yaxis_title="값",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500
    )

    return fig


# 콜백: 변화량 차트
@app.callback(
    Output('change-chart', 'figure'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_change_chart(data_json):
    if not data_json:
        return {}

    df = pd.read_json(data_json)
    df_change = df.diff()

    fig = go.Figure()

    for col in df_change.columns:
        fig.add_trace(go.Bar(
            x=df_change.index,
            y=df_change[col],
            name=col,
            opacity=0.7
        ))

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title="날짜",
        yaxis_title="일간 변화량",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode='group',
        height=350
    )

    return fig


# 콜백: 히스토그램
@app.callback(
    Output('histogram-chart', 'figure'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_histogram(data_json):
    if not data_json:
        return {}

    df = pd.read_json(data_json)

    fig = go.Figure()

    for col in df.columns:
        fig.add_trace(go.Histogram(
            x=df[col],
            name=col,
            opacity=0.7,
            nbinsx=30
        ))

    fig.update_layout(
        template='plotly_white',
        barmode='overlay',
        xaxis_title="값",
        yaxis_title="빈도",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=350
    )

    return fig


# 콜백: 상관관계 히트맵
@app.callback(
    Output('correlation-chart', 'figure'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_correlation_chart(data_json):
    if not data_json:
        return {}

    df = pd.read_json(data_json)
    corr = df.corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="상관계수")
    ))

    fig.update_layout(
        template='plotly_white',
        height=400
    )

    return fig


# 콜백: 박스플롯
@app.callback(
    Output('boxplot-chart', 'figure'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_boxplot(data_json):
    if not data_json:
        return {}

    df = pd.read_json(data_json)

    fig = go.Figure()

    for col in df.columns:
        fig.add_trace(go.Box(
            y=df[col],
            name=col,
            boxmean='sd'
        ))

    fig.update_layout(
        template='plotly_white',
        yaxis_title="값",
        showlegend=True,
        height=400
    )

    return fig


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
