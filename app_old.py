"""
금융 데이터 시계열 분석 Dash 애플리케이션
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 로컬 모듈 import
import sys
sys.path.append('src')
from data_loader import FinancialDataLoader, SAMPLE_TICKERS

# Dash 앱 초기화
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# 데이터 로더 초기화
loader = FinancialDataLoader()

# 레이아웃
app.layout = dbc.Container([
    # 헤더
    html.Div([
        html.H1("📈 Financial Time Series Analysis", className="display-4"),
        html.P("Interactive dashboard for stock market analysis and visualization",
               className="lead")
    ], className="header"),

    # 컨트롤 패널
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # 티커 선택
                dbc.Col([
                    html.Label("Select Tickers", className="control-label"),
                    dcc.Dropdown(
                        id='ticker-dropdown',
                        options=[
                            {'label': f'{category}: {ticker}', 'value': ticker}
                            for category, tickers in SAMPLE_TICKERS.items()
                            for ticker in tickers
                        ],
                        value=['AAPL', 'GOOGL', 'MSFT'],
                        multi=True,
                        placeholder="Select stock tickers..."
                    )
                ], md=4),

                # 날짜 범위
                dbc.Col([
                    html.Label("Start Date", className="control-label"),
                    dcc.DatePickerSingle(
                        id='start-date',
                        date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                        display_format='YYYY-MM-DD'
                    )
                ], md=2),

                dbc.Col([
                    html.Label("End Date", className="control-label"),
                    dcc.DatePickerSingle(
                        id='end-date',
                        date=datetime.now().strftime('%Y-%m-%d'),
                        display_format='YYYY-MM-DD'
                    )
                ], md=2),

                # 버튼
                dbc.Col([
                    html.Label("  ", className="control-label"),  # Spacer
                    html.Br(),
                    dbc.Button(
                        "Load Data",
                        id="load-button",
                        color="primary",
                        className="w-100"
                    )
                ], md=2),

                # 차트 타입
                dbc.Col([
                    html.Label("Chart Type", className="control-label"),
                    dcc.Dropdown(
                        id='chart-type',
                        options=[
                            {'label': 'Price', 'value': 'price'},
                            {'label': 'Returns', 'value': 'returns'},
                            {'label': 'Cumulative Returns', 'value': 'cumulative'},
                            {'label': 'Volatility', 'value': 'volatility'},
                        ],
                        value='price'
                    )
                ], md=2),
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

            # 메인 차트
            dbc.Card([
                dbc.CardBody([
                    html.H4("Price Chart", id='chart-title', className="card-header"),
                    dcc.Graph(id='main-chart', config={'displayModeBar': True})
                ])
            ], className="chart-container mb-4"),

            # 기술적 지표 차트
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Moving Averages", className="card-header"),
                            dcc.Graph(id='ma-chart')
                        ])
                    ], className="chart-container")
                ], md=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("RSI (Relative Strength Index)", className="card-header"),
                            dcc.Graph(id='rsi-chart')
                        ])
                    ], className="chart-container")
                ], md=6),
            ], className="mb-4"),

            # 볼린저 밴드 차트
            dbc.Card([
                dbc.CardBody([
                    html.H5("Bollinger Bands", className="card-header"),
                    dcc.Graph(id='bollinger-chart')
                ])
            ], className="chart-container mb-4"),

            # 상관관계 히트맵
            dbc.Card([
                dbc.CardBody([
                    html.H5("Correlation Heatmap", className="card-header"),
                    dcc.Graph(id='correlation-chart')
                ])
            ], className="chart-container"),
        ]
    ),

    # 데이터 저장소
    dcc.Store(id='data-store'),

], fluid=True, style={'padding': '0'})


# 콜백: 데이터 로드
@app.callback(
    Output('data-store', 'data'),
    Input('load-button', 'n_clicks'),
    State('ticker-dropdown', 'value'),
    State('start-date', 'date'),
    State('end-date', 'date'),
    prevent_initial_call=True
)
def load_data(n_clicks, tickers, start_date, end_date):
    if not tickers:
        return None

    # 데이터 로드
    data = loader.load_stock_data(tickers, start_date, end_date)

    # JSON으로 변환하여 저장
    return data.to_json(date_format='iso')


# 콜백: 통계 카드 업데이트
@app.callback(
    Output('stats-cards', 'children'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_stats(data_json):
    if not data_json:
        return html.Div()

    data = pd.read_json(data_json)
    stats = loader.calculate_statistics(data)

    cards = []
    for ticker, stat in stats.items():
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(ticker, className="stats-label"),
                    html.H3(f"${stat['current_price']:.2f}", className="stats-value"),
                    html.P([
                        html.Span(f"YTD: {stat['ytd_return']*100:+.2f}%",
                                 className="stats-positive" if stat['ytd_return'] > 0 else "stats-negative"),
                        html.Br(),
                        html.Small(f"Vol: {stat['volatility']*100:.1f}% | Sharpe: {stat['sharpe_ratio']:.2f}",
                                  className="text-muted")
                    ])
                ])
            ], className="stats-card")
        ], md=6, lg=3)
        cards.append(card)

    return dbc.Row(cards)


# 콜백: 메인 차트 업데이트
@app.callback(
    [Output('main-chart', 'figure'),
     Output('chart-title', 'children')],
    [Input('data-store', 'data'),
     Input('chart-type', 'value')],
    prevent_initial_call=True
)
def update_main_chart(data_json, chart_type):
    if not data_json:
        return {}, "Chart"

    data = pd.read_json(data_json)

    if chart_type == 'price':
        close_prices = loader._extract_close_prices(data)
        fig = go.Figure()
        for col in close_prices.columns:
            fig.add_trace(go.Scatter(
                x=close_prices.index,
                y=close_prices[col],
                mode='lines',
                name=col,
                line=dict(width=2)
            ))
        title = "Stock Prices"
        yaxis_title = "Price ($)"

    elif chart_type == 'returns':
        returns = loader.calculate_returns(data, period='daily')
        fig = go.Figure()
        for col in returns.columns:
            fig.add_trace(go.Scatter(
                x=returns.index,
                y=returns[col] * 100,
                mode='lines',
                name=col,
                line=dict(width=1)
            ))
        title = "Daily Returns"
        yaxis_title = "Return (%)"

    elif chart_type == 'cumulative':
        cum_returns = loader.calculate_cumulative_returns(data)
        fig = go.Figure()
        for col in cum_returns.columns:
            fig.add_trace(go.Scatter(
                x=cum_returns.index,
                y=cum_returns[col] * 100,
                mode='lines',
                name=col,
                line=dict(width=2),
                fill='tonexty' if fig.data else None
            ))
        title = "Cumulative Returns"
        yaxis_title = "Cumulative Return (%)"

    elif chart_type == 'volatility':
        volatility = loader.calculate_volatility(data, window=20)
        fig = go.Figure()
        for col in volatility.columns:
            fig.add_trace(go.Scatter(
                x=volatility.index,
                y=volatility[col] * 100,
                mode='lines',
                name=col,
                line=dict(width=2)
            ))
        title = "Rolling Volatility (20-day)"
        yaxis_title = "Annualized Volatility (%)"

    else:
        fig = go.Figure()
        title = "Chart"
        yaxis_title = ""

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500
    )

    return fig, title


# 콜백: 이동평균 차트
@app.callback(
    Output('ma-chart', 'figure'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_ma_chart(data_json):
    if not data_json:
        return {}

    data = pd.read_json(data_json)
    close_prices = loader._extract_close_prices(data)

    # 첫 번째 티커만 표시
    ticker = close_prices.columns[0]
    prices = close_prices[ticker]

    mas = loader.calculate_moving_averages(data, windows=[20, 50, 200])

    fig = go.Figure()

    # 가격
    fig.add_trace(go.Scatter(
        x=prices.index,
        y=prices,
        mode='lines',
        name='Price',
        line=dict(color='black', width=1)
    ))

    # 이동평균
    colors = ['blue', 'orange', 'red']
    for (window, ma), color in zip(mas.items(), colors):
        fig.add_trace(go.Scatter(
            x=ma.index,
            y=ma[ticker],
            mode='lines',
            name=f'MA{window}',
            line=dict(color=color, width=2, dash='dash')
        ))

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title="Price ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300
    )

    return fig


# 콜백: RSI 차트
@app.callback(
    Output('rsi-chart', 'figure'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_rsi_chart(data_json):
    if not data_json:
        return {}

    data = pd.read_json(data_json)
    rsi = loader.calculate_rsi(data, period=14)

    # 첫 번째 티커
    ticker = rsi.columns[0]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=rsi.index,
        y=rsi[ticker],
        mode='lines',
        name='RSI',
        line=dict(color='purple', width=2)
    ))

    # 과매수/과매도 라인
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100]),
        height=300
    )

    return fig


# 콜백: 볼린저 밴드 차트
@app.callback(
    Output('bollinger-chart', 'figure'),
    Input('data-store', 'data'),
    prevent_initial_call=True
)
def update_bollinger_chart(data_json):
    if not data_json:
        return {}

    data = pd.read_json(data_json)
    close_prices = loader._extract_close_prices(data)

    # 첫 번째 티커
    ticker = close_prices.columns[0]
    prices = close_prices[ticker]

    middle, upper, lower = loader.calculate_bollinger_bands(data, window=20, num_std=2)

    fig = go.Figure()

    # Upper band
    fig.add_trace(go.Scatter(
        x=upper.index,
        y=upper[ticker],
        mode='lines',
        name='Upper Band',
        line=dict(color='rgba(255, 0, 0, 0.2)', width=1)
    ))

    # Lower band (fill between upper and lower)
    fig.add_trace(go.Scatter(
        x=lower.index,
        y=lower[ticker],
        mode='lines',
        name='Lower Band',
        line=dict(color='rgba(255, 0, 0, 0.2)', width=1),
        fill='tonexty',
        fillcolor='rgba(255, 0, 0, 0.1)'
    ))

    # Middle band
    fig.add_trace(go.Scatter(
        x=middle.index,
        y=middle[ticker],
        mode='lines',
        name='Middle Band (MA20)',
        line=dict(color='orange', width=2, dash='dash')
    ))

    # Price
    fig.add_trace(go.Scatter(
        x=prices.index,
        y=prices,
        mode='lines',
        name='Price',
        line=dict(color='black', width=2)
    ))

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title="Price ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
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

    data = pd.read_json(data_json)
    returns = loader.calculate_returns(data, period='daily')

    # 상관관계 행렬
    corr_matrix = returns.corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))

    fig.update_layout(
        template='plotly_white',
        xaxis_title="",
        yaxis_title="",
        height=400
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
