# 📊 금리/환율 데이터 분석 대시보드

Python Dash를 사용한 금리/환율 시계열 데이터 분석 대시보드
FastAPI 서버에서 Oracle DB 데이터를 조회하여 시각화

## ✨ 주요 기능

### 📈 데이터 타입
- **금리 데이터** - 국고채, 중앙은행 금리, 회사채
- **환율 데이터** - 주요통화, 달러기준, 신흥국 통화

### 🎯 카테고리별 필터링
- **금리**
  - 국고채: US_10Y, KR_3Y, KR_5Y, KR_10Y, JP_10Y
  - 중앙은행: FED_RATE, BOK_RATE, ECB_RATE, BOJ_RATE
  - 회사채: KR_AAA_3Y, KR_AA_3Y, US_CORP_BBB

- **환율**
  - 주요통화: USD/KRW, EUR/KRW, JPY/KRW, CNY/KRW
  - 달러기준: EUR/USD, GBP/USD, JPY/USD, AUD/USD
  - 신흥국: USD/BRL, USD/INR, USD/MXN, USD/ZAR

### 📊 시각화
1. **시계열 그래프** - 추세 및 패턴 분석
2. **일간 변화량 차트** - 변동성 확인
3. **히스토그램** - 데이터 분포 분석
4. **상관관계 히트맵** - 항목간 상관관계
5. **박스플롯** - 분산 및 이상치 비교

### 📈 통계 지표
- 현재값, 평균, 표준편차
- 최소/최대, 중앙값, 사분위수
- 1일/1주/1개월 변화량
- 변화율 (%)

## 🏗️ 아키텍처

```
┌─────────────┐      HTTP API       ┌──────────────┐      SQL Query      ┌──────────┐
│             │ ──────────────────> │              │ ──────────────────> │          │
│  Dash App   │                     │  FastAPI     │                     │ Oracle   │
│  (Frontend) │                     │  Server      │                     │    DB    │
│             │ <────────────────── │  (Backend)   │ <────────────────── │          │
└─────────────┘      JSON Data      └──────────────┘      Result Set     └──────────┘
```

## 📁 프로젝트 구조

```
dash_plot/
├── app.py                       # 메인 Dash 애플리케이션
├── app_old.py                   # 이전 버전 (주식 데이터)
├── src/
│   ├── api_client.py            # FastAPI 클라이언트
│   ├── db_config.py             # DB 설정 (참고용)
│   └── oracle_data_loader.py    # Oracle 로더 (참고용)
├── assets/
│   └── styles.css               # 커스텀 CSS
├── data/                        # 데이터 저장 디렉토리
├── requirements.txt             # Python 패키지
├── API_SPEC.md                  # FastAPI 서버 API 명세
├── README.md                    # 이 파일
└── .gitignore
```

## 🚀 빠른 시작

### 1. 설치

```bash
git clone https://github.com/minhoo-main/dash_plot.git
cd dash_plot

# 패키지 설치
pip install -r requirements.txt
```

### 2. FastAPI 서버 설정

**API 명세는 `API_SPEC.md` 참고**

FastAPI 서버가 다음 엔드포인트를 제공해야 합니다:

- `GET /api/categories` - 카테고리 목록
- `GET /api/interest-rates` - 금리 데이터
- `GET /api/exchange-rates` - 환율 데이터
- `GET /api/statistics` - 통계 데이터

### 3. Dash 앱 실행

```bash
# Mock 데이터로 테스트 (FastAPI 서버 불필요)
python app.py

# 실제 FastAPI 서버와 연결
# app.py 파일에서 다음 라인 수정:
# client = APIClient(base_url="http://localhost:8000")  # 실제 서버 URL
```

브라우저에서 http://localhost:8050 접속

## 🔌 FastAPI 서버 연동

### app.py에서 클라이언트 변경

```python
# Mock 클라이언트 (테스트용)
from api_client import MockAPIClient
client = MockAPIClient()

# ↓ 실제 서버 사용 시

from api_client import APIClient
client = APIClient(base_url="http://localhost:8000")
```

### FastAPI 서버 응답 형식

**금리 데이터 예시:**
```json
{
  "status": "success",
  "data": {
    "dates": ["2024-01-01", "2024-01-02", "..."],
    "series": {
      "US_10Y": {
        "name": "US 10-Year Treasury",
        "category": "국고채",
        "values": [4.05, 4.03, "..."],
        "unit": "%"
      }
    },
    "metadata": {
      "total_records": 297,
      "start_date": "2024-01-01",
      "end_date": "2024-10-23"
    }
  }
}
```

자세한 API 명세는 `API_SPEC.md` 참고

## 📊 사용 방법

1. **데이터 타입 선택**: 금리 또는 환율
2. **카테고리 선택**: 원하는 카테고리 선택 (다중 선택 가능)
3. **항목 선택**: 분석할 구체적 항목 선택
4. **날짜 범위 설정**: 시작일/종료일 지정
5. **데이터 로드 버튼 클릭**: FastAPI 서버에서 데이터 조회
6. **차트 및 통계 확인**: 다양한 시각화 및 통계 지표 분석

## 🎨 화면 구성

### 상단
- 통계 카드: 각 항목의 현재값, 변화량, 기본 통계

### 중간
- 시계열 차트: 추세 분석
- 일간 변화량 차트: 변동성 확인
- 히스토그램: 분포 분석

### 하단
- 상관관계 히트맵: 항목간 관계
- 박스플롯: 분산 비교
- 통계표: 상세 통계 지표

## 🛠️ 기술 스택

### Frontend (Dash App)
- **Dash 2.14.2** - 웹 애플리케이션 프레임워크
- **Plotly 5.18.0** - 인터랙티브 차트
- **dash-bootstrap-components** - UI 컴포넌트
- **pandas, numpy** - 데이터 처리

### Backend (FastAPI Server) - 별도 구현 필요
- **FastAPI** - API 서버
- **cx_Oracle** - Oracle DB 연결
- **pandas** - 데이터 처리

### Database
- **Oracle Database** - 금리/환율 데이터 저장

## 📋 FastAPI 서버 구현 가이드

`API_SPEC.md` 파일에 상세한 API 명세가 있습니다.

주요 구현 사항:
1. Oracle DB 연결 설정
2. 4개의 API 엔드포인트 구현
3. 데이터 쿼리 및 변환
4. JSON 응답 생성

## 🧪 테스트

### Mock 클라이언트 테스트

```bash
cd src
python api_client.py
```

샘플 데이터로 API 클라이언트 기능 테스트

### Dash 앱 테스트

```bash
python app.py
```

Mock 데이터로 전체 대시보드 기능 테스트

## 📝 환경 변수

FastAPI 서버에서 사용할 환경 변수:

```bash
export ORACLE_USER=your_username
export ORACLE_PASSWORD=your_password
export ORACLE_DSN=localhost:1521/ORCL
```

## 🔧 커스터마이징

### 새로운 카테고리 추가

`src/db_config.py`에서 `CATEGORIES` 딕셔너리 수정

### 새로운 통계 지표 추가

`src/api_client.py`의 `get_statistics()` 메서드 확장

### 차트 스타일 변경

`assets/styles.css` 파일 수정

## ⚠️ 주의사항

- FastAPI 서버가 실행 중이어야 실제 데이터 조회 가능
- Mock 클라이언트는 랜덤 데이터 생성 (테스트용)
- Oracle DB 연결 정보는 환경 변수로 관리 권장
- 대량 데이터 조회 시 로딩 시간 고려

## 🚧 향후 개발 계획

- [ ] 실시간 데이터 업데이트
- [ ] 데이터 내보내기 (CSV, Excel)
- [ ] 사용자 정의 지표 추가
- [ ] 알림 기능 (임계값 도달 시)
- [ ] 다크 모드
- [ ] 모바일 최적화

## 📄 라이선스

MIT License

## 🤝 기여

Issue 및 Pull Request 환영합니다!

## 📧 문의

GitHub Issues: https://github.com/minhoo-main/dash_plot/issues

---

**마지막 업데이트:** 2025-10-23
**Made with** ❤️ **and Python Dash**
