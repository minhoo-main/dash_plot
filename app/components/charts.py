"""
재사용 가능한 차트 컴포넌트
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional
from app.utils.chart_utils import should_use_secondary_axis, get_chart_colors
from config import CHART_CONFIG


def create_timeseries_chart(df: pd.DataFrame, is_normalized: bool = False) -> go.Figure:
    """
    시계열 차트 생성 (히스토그램 포함)

    Args:
        df: 데이터 DataFrame
        is_normalized: 정규화 여부

    Returns:
        Plotly Figure
    """
    colors = get_chart_colors()
    config = CHART_CONFIG['timeseries']

    # 정규화되면 단일 축, 아니면 스케일 차이 확인하여 보조 축 사용 결정
    if is_normalized:
        use_secondary = False
        sorted_cols = list(df.columns)
    else:
        use_secondary, sorted_cols = should_use_secondary_axis(df)

    # 히스토그램이 있는 서브플롯 생성
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=config['column_widths'],
        horizontal_spacing=config['horizontal_spacing'],
        specs=[[{"type": "xy"}, {"type": "bar"}]],
        shared_yaxes=True
    )

    if use_secondary and len(df.columns) >= 2:
        # 첫 번째 항목은 주 축
        col = sorted_cols[0]
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col,
            line=dict(width=2),
            yaxis='y',
            hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.2f}<extra></extra>'
        ), row=1, col=1)

        # 나머지는 보조 축
        for col in sorted_cols[1:]:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                mode='lines',
                name=col,
                line=dict(width=2),
                yaxis='y3',
                hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.2f}<extra></extra>'
            ), row=1, col=1)

        # 히스토그램 추가
        for col in df.columns:
            fig.add_trace(go.Histogram(
                y=df[col],
                name=col,
                showlegend=False
            ), row=1, col=2)

        # 레이아웃 설정 (이중 축)
        fig.update_layout(
            template=config['template'],
            hovermode=config['hovermode'],
            xaxis_title="날짜",
            yaxis=dict(
                title=sorted_cols[0],
                titlefont=dict(color=colors['primary']),
                tickfont=dict(color=colors['primary'])
            ),
            yaxis3=dict(
                title="기타 항목",
                titlefont=dict(color=colors['secondary']),
                tickfont=dict(color=colors['secondary']),
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
            height=config['height'],
            bargap=0.1
        )
    else:
        # 단일 축 사용
        for col in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                mode='lines',
                name=col,
                line=dict(width=2),
                hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.2f}<extra></extra>'
            ), row=1, col=1)

        # 히스토그램 추가
        for col in df.columns:
            fig.add_trace(go.Histogram(
                y=df[col],
                name=col,
                showlegend=False
            ), row=1, col=2)

        yaxis_title = "지수 (시작=100)" if is_normalized else "값"

        fig.update_layout(
            template=config['template'],
            hovermode=config['hovermode'],
            xaxis_title="날짜",
            yaxis_title=yaxis_title,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=0.85
            ),
            height=config['height'],
            bargap=0.1
        )

    # X축 레이블 숨김 (히스토그램)
    fig.update_xaxes(title_text="", showticklabels=False, row=1, col=2)

    return fig


def create_spread_chart(spread: pd.Series, label: str, yaxis_title: str) -> go.Figure:
    """
    스프레드 차트 생성 (히스토그램 포함)

    Args:
        spread: 스프레드 데이터 Series
        label: 차트 라벨
        yaxis_title: Y축 제목

    Returns:
        Plotly Figure
    """
    colors = get_chart_colors()
    config = CHART_CONFIG['spread']

    # 히스토그램이 있는 서브플롯 생성
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=config['column_widths'],
        horizontal_spacing=config['horizontal_spacing'],
        specs=[[{"type": "scatter"}, {"type": "bar"}]],
        shared_yaxes=True
    )

    # 라인 플롯
    fig.add_trace(go.Scatter(
        x=spread.index,
        y=spread,
        mode='lines',
        name=label,
        line=dict(width=2, color=colors['spread']),
        hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>값: %{y:.4f}<extra></extra>'
    ), row=1, col=1)

    # 히스토그램 추가
    fig.add_trace(go.Histogram(
        y=spread,
        name=label,
        showlegend=False,
        marker=dict(color=colors['spread'])
    ), row=1, col=2)

    # 평균선 추가
    mean_val = spread.mean()
    fig.add_hline(
        y=mean_val,
        line_dash="dash",
        line_color=colors['mean_line'],
        annotation_text=f"평균: {mean_val:.4f}",
        annotation_position="right",
        row=1, col=1
    )

    fig.update_layout(
        template=config['template'],
        hovermode=config['hovermode'],
        xaxis_title="날짜",
        yaxis_title=yaxis_title,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.85
        ),
        height=config['height'],
        bargap=0.1
    )

    # X축 레이블 숨김
    fig.update_xaxes(title_text="", showticklabels=False, row=1, col=2)

    return fig
