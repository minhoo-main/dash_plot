"""
메인 레이아웃
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
from config import APP_CONFIG
from .control_panel import create_control_panel
from .charts_section import create_timeseries_section, create_spread_section


def create_layout() -> dbc.Container:
    """
    애플리케이션 메인 레이아웃 생성

    Returns:
        Dash Bootstrap Container 컴포넌트
    """
    return dbc.Container([
        # 헤더
        html.Div([
            html.H1(f"📊 {APP_CONFIG['title']}", className="display-4"),
            html.P(APP_CONFIG['subtitle'], className="lead")
        ], className="header"),

        # 컨트롤 패널
        create_control_panel(),

        # 로딩 인디케이터
        dcc.Loading(
            id="loading",
            type="default",
            children=[
                # 메인 시계열 차트
                create_timeseries_section(),

                # 스프레드 차트
                create_spread_section(),
            ]
        ),

        # 데이터 저장소
        dcc.Store(id='data-store'),
        dcc.Store(id='stats-store'),

    ], fluid=True, style={'padding': '0'})
