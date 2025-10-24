"""
애플리케이션 설정 및 상수
"""

from datetime import datetime, timedelta

# 애플리케이션 설정
APP_CONFIG = {
    'title': '금리/환율 데이터 분석 대시보드',
    'subtitle': 'Oracle DB 기반 시계열 데이터 분석 및 시각화',
    'host': '0.0.0.0',
    'port': 8050,
    'debug': True
}

# 데이터 타입 옵션
DATA_TYPE_OPTIONS = [
    {'label': '📈 금리', 'value': 'interest_rate'},
    {'label': '💱 환율', 'value': 'exchange_rate'},
    {'label': '📊 전체', 'value': 'all'}
]

# 스프레드 연산 옵션
SPREAD_OPERATIONS = [
    {'label': '차이 (A - B)', 'value': 'subtract'},
    {'label': '비율 (A / B)', 'value': 'divide'},
]

# 기간 선택 버튼
PERIOD_BUTTONS = [
    {'id': 'period-1y', 'label': '1Y', 'days': 365},
    {'id': 'period-3y', 'label': '3Y', 'days': 365 * 3},
    {'id': 'period-5y', 'label': '5Y', 'days': 365 * 5},
    {'id': 'period-10y', 'label': '10Y', 'days': 365 * 10},
]

# 기본 날짜 범위
DEFAULT_START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')

# 차트 설정
CHART_CONFIG = {
    'timeseries': {
        'height': 500,
        'template': 'plotly_white',
        'hovermode': 'x unified',
        'column_widths': [0.85, 0.15],
        'horizontal_spacing': 0.02
    },
    'spread': {
        'height': 400,
        'template': 'plotly_white',
        'hovermode': 'x unified',
        'column_widths': [0.85, 0.15],
        'horizontal_spacing': 0.02
    }
}

# 차트 색상
CHART_COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'spread': 'rgb(0, 176, 80)',
    'mean_line': 'red'
}

# 스케일 차이 임계값 (보조 축 사용 여부 결정)
SCALE_DIFF_THRESHOLD = 5

# 통계 컬럼 한글명
STATS_COLUMN_NAMES = {
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

# 스프레드 통계 키 목록
SPREAD_STATS_KEYS = ['현재값', '평균', '표준편차', '최소', '최대', '중앙값', '25% 분위', '75% 분위']
