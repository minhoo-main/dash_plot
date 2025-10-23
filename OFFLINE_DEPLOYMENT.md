# 오프라인 환경 배포 가이드

## 개요

이 Dash 애플리케이션은 인터넷 연결이 없는 환경에서도 완전히 동작하도록 설계되었습니다.

## ✅ 오프라인 동작 확인 완료

### 로컬 리소스
- ✅ **Bootstrap CSS**: `assets/bootstrap.min.css` (163KB)
- ✅ **커스텀 CSS**: `assets/styles.css` (3KB)
- ✅ **Dash/Plotly**: Python 패키지 설치 (로컬)
- ✅ **모든 JavaScript**: Dash 패키지에 포함됨

### CDN 의존성 제거
```python
# 이전 (CDN 사용)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 현재 (로컬 사용)
app = dash.Dash(__name__)
# assets/bootstrap.min.css 자동 로드
```

## 📦 배포 패키지 준비

### 1단계: 프로젝트 파일 확인

```bash
dash_plot/
├── app.py                      # 메인 애플리케이션
├── requirements.txt            # Python 패키지 목록
├── src/
│   ├── api_client.py          # API 클라이언트
│   ├── db_config.py           # DB 설정
│   └── oracle_data_loader.py  # Oracle 로더
├── assets/
│   ├── bootstrap.min.css      # ⭐ 로컬 Bootstrap CSS
│   └── styles.css             # ⭐ 커스텀 CSS
└── data/                       # 데이터 디렉토리 (선택사항)
```

### 2단계: Python 패키지 다운로드 (온라인 환경에서)

```bash
# 패키지 디렉토리 생성
mkdir packages

# 모든 의존성 패키지 다운로드
pip download -r requirements.txt -d packages/

# 다운로드된 패키지 확인
ls packages/
```

### 3단계: 배포 패키지 압축

```bash
# 전체 프로젝트 압축
tar -czf dash_plot_offline.tar.gz dash_plot/

# 또는 zip 형식
zip -r dash_plot_offline.zip dash_plot/
```

## 🚀 오프라인 환경 설치

### 1단계: 파일 전송

오프라인 환경으로 파일 전송:
- USB 드라이브
- 내부 네트워크 공유
- 물리적 파일 전송

```bash
# 압축 해제
tar -xzf dash_plot_offline.tar.gz
cd dash_plot
```

### 2단계: Python 패키지 설치

```bash
# 로컬 패키지에서 설치 (인터넷 불필요)
pip install --no-index --find-links=packages/ -r requirements.txt

# 또는 개별 패키지 설치
pip install --no-index --find-links=packages/ dash dash-bootstrap-components plotly pandas numpy scipy requests
```

### 3단계: 애플리케이션 실행

```bash
python3 app.py
```

브라우저에서 `http://localhost:8050` 접속

## 🔍 동작 확인

### CSS 로딩 확인

브라우저 개발자 도구 (F12) → Network 탭:
- ✅ `bootstrap.min.css`: 200 OK (from disk cache)
- ✅ `styles.css`: 200 OK (from disk cache)
- ❌ CDN 요청 없음

### 오프라인 테스트

```bash
# 네트워크 차단 후 테스트
# 방법 1: 네트워크 케이블 분리
# 방법 2: 방화벽 규칙 추가

# 앱 실행
python3 app.py

# 브라우저에서 확인
# - UI가 정상적으로 표시되는가?
# - 버튼, 드롭다운이 스타일링되어 있는가?
# - 차트가 정상적으로 그려지는가?
```

## ⚙️ 추가 설정 (선택사항)

### FastAPI 서버 연동

오프라인 환경에서 실제 데이터를 사용하려면:

1. **FastAPI 서버도 동일 환경에 배포**
```bash
# FastAPI 서버 패키지
fastapi
uvicorn
cx_Oracle
```

2. **app.py에서 클라이언트 변경**
```python
# Mock 클라이언트 (인터넷 불필요)
from api_client import MockAPIClient
client = MockAPIClient()

# 또는 실제 FastAPI 서버 (동일 네트워크 내)
from api_client import APIClient
client = APIClient(base_url="http://192.168.1.100:8000")
```

### Oracle DB 연결

```bash
# Oracle Instant Client 설치 (오프라인)
# 1. Oracle 웹사이트에서 Instant Client 다운로드
# 2. 오프라인 환경으로 전송
# 3. 설치 및 환경 변수 설정

export ORACLE_HOME=/path/to/instantclient
export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
```

## 🐛 트러블슈팅

### 문제: CSS 스타일이 적용되지 않음

**확인 사항:**
```bash
# assets 디렉토리 확인
ls -la assets/

# 출력 예시:
# -rw-r--r-- 1 user user 163873 Oct 23 17:03 bootstrap.min.css
# -rw-r--r-- 1 user user   3191 Oct 23 13:02 styles.css
```

**해결 방법:**
```bash
# Bootstrap CSS 다시 다운로드 (온라인 환경에서)
curl -o assets/bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css
```

### 문제: Python 패키지 의존성 오류

**확인:**
```bash
pip list | grep dash
pip list | grep plotly
```

**해결:**
```bash
# 패키지 재설치
pip install --force-reinstall --no-index --find-links=packages/ dash plotly
```

### 문제: 차트가 표시되지 않음

**확인:**
- 브라우저 콘솔 (F12) 에러 메시지 확인
- Plotly JavaScript가 로드되었는지 확인

**해결:**
```bash
# Dash 재설치
pip install --upgrade --no-index --find-links=packages/ dash
```

## 📋 체크리스트

배포 전 확인:

- [ ] `assets/bootstrap.min.css` 파일 존재 (163KB)
- [ ] `assets/styles.css` 파일 존재
- [ ] `packages/` 디렉토리에 모든 Python 패키지 다운로드
- [ ] `requirements.txt` 파일 포함
- [ ] `src/` 디렉토리 전체 포함
- [ ] `app.py`에서 CDN 링크 제거 확인
- [ ] 테스트: 네트워크 차단 후 정상 동작 확인

## 🔒 보안 고려사항

오프라인 환경 특성상:
- ✅ 외부 CDN 호출 없음 → 데이터 유출 위험 없음
- ✅ 모든 리소스 로컬 → 네트워크 의존성 없음
- ⚠️ DB 연결 정보는 환경 변수로 관리
- ⚠️ `.env` 파일은 버전 관리에 포함하지 말것

## 📞 지원

문제 발생 시:
1. 로그 파일 확인: `app.py` 실행 시 콘솔 출력
2. 브라우저 개발자 도구 (F12) → Console 탭
3. GitHub Issues: https://github.com/minhoo-main/dash_plot/issues

---

**작성일:** 2025-10-23
**테스트 환경:** Ubuntu 20.04, Python 3.8+
