"""
금리/환율 데이터 시계열 분석 Dash 애플리케이션
FastAPI 서버에서 데이터 조회

리팩토링된 모듈화 버전
"""

import dash
import dash_bootstrap_components as dbc
import sys

# 로컬 모듈 import
sys.path.append('src')
from src.api_client import MockAPIClient  # 실제 서버 사용 시: APIClient

# 애플리케이션 모듈 import
from app.layouts import create_layout
from app.callbacks import (
    register_ui_callbacks,
    register_data_callbacks,
    register_chart_callbacks
)
from config import APP_CONFIG


def create_app():
    """
    Dash 애플리케이션 생성 및 초기화

    Returns:
        Dash 앱 인스턴스
    """
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
    categories = client.get_categories()

    # 레이아웃 설정
    app.layout = create_layout()

    # 콜백 등록
    register_ui_callbacks(app, categories)
    register_data_callbacks(app, client, categories)
    register_chart_callbacks(app)

    return app


if __name__ == '__main__':
    # 앱 생성 및 실행
    app = create_app()
    app.run_server(
        debug=APP_CONFIG['debug'],
        host=APP_CONFIG['host'],
        port=APP_CONFIG['port']
    )
