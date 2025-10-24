"""
차트 섹션 레이아웃
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
from config import SPREAD_OPERATIONS


def create_timeseries_section() -> dbc.Card:
    """
    시계열 차트 섹션 생성

    Returns:
        Dash Bootstrap Card 컴포넌트
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H4("시계열 차트", className="card-header",
                       style={'display': 'inline-block'}),
                dbc.Checklist(
                    id='normalize-toggle',
                    options=[{'label': ' 정규화 (시작=100)', 'value': 'normalize'}],
                    value=[],
                    inline=True,
                    switch=True,
                    style={'display': 'inline-block', 'marginLeft': '20px',
                          'verticalAlign': 'middle'}
                )
            ]),
            dcc.Graph(id='timeseries-chart', config={'displayModeBar': True}),
            html.Div(id='statistics-table', className="mt-3")
        ])
    ], className="chart-container mb-4")


def create_spread_section() -> html.Div:
    """
    스프레드 차트 섹션 생성

    Returns:
        Dash HTML Div 컴포넌트
    """
    return html.Div(id='spread-section', children=[
        dbc.Card([
            dbc.CardBody([
                html.H4("스프레드 차트", className="card-header"),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Label("기준 항목 (분자)", className="control-label"),
                            dcc.Dropdown(id='spread-item1',
                                       placeholder="항목 선택...")
                        ], md=3),
                        dbc.Col([
                            html.Label("비교 항목 (분모)", className="control-label"),
                            dcc.Dropdown(id='spread-item2',
                                       placeholder="항목 선택...")
                        ], md=3),
                        dbc.Col([
                            html.Label("연산", className="control-label"),
                            dcc.Dropdown(
                                id='spread-operation',
                                options=SPREAD_OPERATIONS,
                                value='subtract',
                                clearable=False
                            )
                        ], md=2),
                        dbc.Col([
                            html.Label("\u00a0", className="control-label"),
                            dbc.Button("계산", id="calc-spread-button",
                                     color="success", className="w-100")
                        ], md=2),
                    ], className="mb-3"),
                ]),
                dcc.Graph(id='spread-chart'),
                html.Div(id='spread-stats', className="mt-3")
            ])
        ], className="chart-container mb-4")
    ], style={'display': 'none'})
