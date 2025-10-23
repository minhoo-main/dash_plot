"""
Oracle DB 연결 설정
"""

import os

# Oracle DB 연결 정보
DB_CONFIG = {
    'user': os.getenv('ORACLE_USER', 'your_username'),
    'password': os.getenv('ORACLE_PASSWORD', 'your_password'),
    'dsn': os.getenv('ORACLE_DSN', 'localhost:1521/ORCL'),
}

# SQLAlchemy 연결 문자열
def get_connection_string():
    """SQLAlchemy 연결 문자열 생성"""
    return f"oracle+cx_oracle://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['dsn']}"


# 샘플 테이블 구조 (실제 테이블에 맞게 수정 필요)
"""
예상 테이블 구조:

1. 금리 데이터 (INTEREST_RATES)
   - DATE_VALUE      DATE
   - RATE_TYPE       VARCHAR2(50)    -- 예: 'US_10Y', 'KR_3Y', 'FED_RATE'
   - RATE_VALUE      NUMBER(10,4)
   - CATEGORY        VARCHAR2(50)    -- 예: 'Government Bond', 'Central Bank Rate'

2. 환율 데이터 (EXCHANGE_RATES)
   - DATE_VALUE      DATE
   - CURRENCY_PAIR   VARCHAR2(20)    -- 예: 'USD/KRW', 'EUR/USD'
   - RATE_VALUE      NUMBER(15,4)
   - CATEGORY        VARCHAR2(50)    -- 예: 'Major', 'Emerging'
"""

# 카테고리 정의
CATEGORIES = {
    '금리': {
        '국고채': ['US_10Y', 'KR_3Y', 'KR_5Y', 'KR_10Y', 'JP_10Y'],
        '중앙은행': ['FED_RATE', 'BOK_RATE', 'ECB_RATE', 'BOJ_RATE'],
        '회사채': ['KR_AAA_3Y', 'KR_AA_3Y', 'US_CORP_BBB'],
    },
    '환율': {
        '주요통화': ['USD/KRW', 'EUR/KRW', 'JPY/KRW', 'CNY/KRW'],
        '달러기준': ['EUR/USD', 'GBP/USD', 'JPY/USD', 'AUD/USD'],
        '신흥국': ['USD/BRL', 'USD/INR', 'USD/MXN', 'USD/ZAR'],
    }
}
