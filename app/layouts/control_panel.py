"""
컨트롤 패널 레이아웃
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
from config import (
    DATA_TYPE_OPTIONS,
    PERIOD_BUTTONS,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE
)


def create_control_panel() -> dbc.Card:
    """
    컨트롤 패널 생성

    Returns:
        Dash Bootstrap Card 컴포넌트
    """
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # 데이터 타입 선택
                dbc.Col([
                    html.Label("데이터 타입", className="control-label"),
                    dcc.Dropdown(
                        id='data-type-dropdown',
                        options=DATA_TYPE_OPTIONS,
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
                            date=DEFAULT_START_DATE,
                            display_format='YYYY-MM-DD',
                            style={'display': 'inline-block', 'marginRight': '5px'}
                        ),
                        html.Span("~", style={'display': 'inline-block', 'margin': '0 5px'}),
                        dcc.DatePickerSingle(
                            id='end-date',
                            date=DEFAULT_END_DATE,
                            display_format='YYYY-MM-DD',
                            style={'display': 'inline-block', 'marginLeft': '5px'}
                        ),
                        dbc.ButtonGroup([
                            dbc.Button(
                                btn['label'],
                                id=btn['id'],
                                size="sm",
                                outline=True,
                                color="secondary",
                                style={'marginLeft': '10px'} if idx == 0 else {}
                            )
                            for idx, btn in enumerate(PERIOD_BUTTONS)
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
    ], className="control-panel mb-4")
