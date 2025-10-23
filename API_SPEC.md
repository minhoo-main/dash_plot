# FastAPI 서버 API 명세

Dash 앱에서 호출할 FastAPI 서버의 API 엔드포인트 정의

## 📋 목차
1. [카테고리 목록 조회](#1-카테고리-목록-조회)
2. [금리 데이터 조회](#2-금리-데이터-조회)
3. [환율 데이터 조회](#3-환율-데이터-조회)
4. [통계 데이터 조회](#4-통계-데이터-조회)

---

## 1. 카테고리 목록 조회

### Endpoint
```
GET /api/categories
```

### 설명
사용 가능한 모든 카테고리와 항목 목록 반환

### Request
파라미터 없음

### Response
```json
{
  "status": "success",
  "data": {
    "금리": {
      "국고채": ["US_10Y", "KR_3Y", "KR_5Y", "KR_10Y", "JP_10Y"],
      "중앙은행": ["FED_RATE", "BOK_RATE", "ECB_RATE", "BOJ_RATE"],
      "회사채": ["KR_AAA_3Y", "KR_AA_3Y", "US_CORP_BBB"]
    },
    "환율": {
      "주요통화": ["USD/KRW", "EUR/KRW", "JPY/KRW", "CNY/KRW"],
      "달러기준": ["EUR/USD", "GBP/USD", "JPY/USD", "AUD/USD"],
      "신흥국": ["USD/BRL", "USD/INR", "USD/MXN", "USD/ZAR"]
    }
  }
}
```

---

## 2. 금리 데이터 조회

### Endpoint
```
GET /api/interest-rates
```

### 설명
지정된 금리 항목들의 시계열 데이터 반환

### Request Parameters

| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---------|------|------|------|------|
| `items` | string | Yes | 쉼표로 구분된 금리 항목 | `US_10Y,KR_3Y,FED_RATE` |
| `start_date` | string | Yes | 시작 날짜 (YYYY-MM-DD) | `2023-01-01` |
| `end_date` | string | Yes | 종료 날짜 (YYYY-MM-DD) | `2024-10-23` |

### Request Example
```
GET /api/interest-rates?items=US_10Y,KR_3Y,FED_RATE&start_date=2024-01-01&end_date=2024-10-23
```

### Response
```json
{
  "status": "success",
  "data": {
    "dates": ["2024-01-01", "2024-01-02", "2024-01-03", "..."],
    "series": {
      "US_10Y": {
        "name": "US 10-Year Treasury",
        "category": "국고채",
        "values": [4.05, 4.03, 4.08, "..."],
        "unit": "%"
      },
      "KR_3Y": {
        "name": "한국 국고채 3년",
        "category": "국고채",
        "values": [3.25, 3.26, 3.24, "..."],
        "unit": "%"
      },
      "FED_RATE": {
        "name": "Federal Funds Rate",
        "category": "중앙은행",
        "values": [5.25, 5.25, 5.25, "..."],
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

---

## 3. 환율 데이터 조회

### Endpoint
```
GET /api/exchange-rates
```

### 설명
지정된 통화쌍들의 환율 시계열 데이터 반환

### Request Parameters

| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---------|------|------|------|------|
| `pairs` | string | Yes | 쉼표로 구분된 통화쌍 | `USD/KRW,EUR/KRW,JPY/KRW` |
| `start_date` | string | Yes | 시작 날짜 (YYYY-MM-DD) | `2023-01-01` |
| `end_date` | string | Yes | 종료 날짜 (YYYY-MM-DD) | `2024-10-23` |

### Request Example
```
GET /api/exchange-rates?pairs=USD/KRW,EUR/KRW,JPY/KRW&start_date=2024-01-01&end_date=2024-10-23
```

### Response
```json
{
  "status": "success",
  "data": {
    "dates": ["2024-01-01", "2024-01-02", "2024-01-03", "..."],
    "series": {
      "USD/KRW": {
        "name": "미국 달러/원",
        "category": "주요통화",
        "values": [1305.5, 1308.2, 1310.0, "..."],
        "unit": "KRW"
      },
      "EUR/KRW": {
        "name": "유로/원",
        "category": "주요통화",
        "values": [1425.3, 1428.5, 1430.2, "..."],
        "unit": "KRW"
      },
      "JPY/KRW": {
        "name": "일본 엔/원",
        "category": "주요통화",
        "values": [9.15, 9.18, 9.20, "..."],
        "unit": "KRW"
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

---

## 4. 통계 데이터 조회

### Endpoint
```
GET /api/statistics
```

### 설명
지정된 항목들의 통계 지표 반환

### Request Parameters

| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---------|------|------|------|------|
| `data_type` | string | Yes | 데이터 타입 | `interest_rate` 또는 `exchange_rate` |
| `items` | string | Yes | 쉼표로 구분된 항목 | `US_10Y,KR_3Y` 또는 `USD/KRW,EUR/KRW` |
| `start_date` | string | Yes | 시작 날짜 | `2024-01-01` |
| `end_date` | string | Yes | 종료 날짜 | `2024-10-23` |

### Request Example
```
GET /api/statistics?data_type=interest_rate&items=US_10Y,KR_3Y&start_date=2024-01-01&end_date=2024-10-23
```

### Response
```json
{
  "status": "success",
  "data": {
    "US_10Y": {
      "current": 4.08,
      "mean": 4.12,
      "std": 0.15,
      "min": 3.78,
      "max": 4.50,
      "median": 4.10,
      "q25": 4.00,
      "q75": 4.22,
      "change_1d": -0.02,
      "change_1w": 0.05,
      "change_1m": 0.15,
      "pct_change_1d": -0.49,
      "pct_change_ytd": 8.24,
      "unit": "%"
    },
    "KR_3Y": {
      "current": 3.24,
      "mean": 3.28,
      "std": 0.08,
      "min": 3.10,
      "max": 3.45,
      "median": 3.27,
      "q25": 3.22,
      "q75": 3.35,
      "change_1d": -0.01,
      "change_1w": 0.02,
      "change_1m": 0.05,
      "pct_change_1d": -0.31,
      "pct_change_ytd": 4.52,
      "unit": "%"
    }
  }
}
```

---

## 📝 공통 응답 형식

### 성공 응답
```json
{
  "status": "success",
  "data": { ... }
}
```

### 에러 응답
```json
{
  "status": "error",
  "message": "에러 메시지",
  "code": "ERROR_CODE"
}
```

### 에러 코드

| 코드 | HTTP Status | 설명 |
|------|-------------|------|
| `INVALID_DATE` | 400 | 잘못된 날짜 형식 |
| `INVALID_ITEMS` | 400 | 잘못된 항목 |
| `NO_DATA` | 404 | 데이터 없음 |
| `DATABASE_ERROR` | 500 | 데이터베이스 에러 |
| `INTERNAL_ERROR` | 500 | 서버 내부 에러 |

---

## 🔧 FastAPI 서버 구현 예시

```python
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from datetime import datetime
import pandas as pd

app = FastAPI()

@app.get("/api/categories")
def get_categories():
    """카테고리 목록 반환"""
    return {
        "status": "success",
        "data": {
            "금리": {
                "국고채": ["US_10Y", "KR_3Y", "KR_5Y", "KR_10Y", "JP_10Y"],
                "중앙은행": ["FED_RATE", "BOK_RATE", "ECB_RATE", "BOJ_RATE"],
                "회사채": ["KR_AAA_3Y", "KR_AA_3Y", "US_CORP_BBB"]
            },
            "환율": {
                "주요통화": ["USD/KRW", "EUR/KRW", "JPY/KRW", "CNY/KRW"],
                "달러기준": ["EUR/USD", "GBP/USD", "JPY/USD", "AUD/USD"],
                "신흥국": ["USD/BRL", "USD/INR", "USD/MXN", "USD/ZAR"]
            }
        }
    }

@app.get("/api/interest-rates")
def get_interest_rates(
    items: str = Query(..., description="쉼표로 구분된 금리 항목"),
    start_date: str = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="종료 날짜 (YYYY-MM-DD)")
):
    """금리 데이터 조회"""
    try:
        # Oracle DB에서 데이터 조회
        items_list = [item.strip() for item in items.split(',')]

        # TODO: 실제 DB 쿼리 로직
        # df = query_interest_rates(items_list, start_date, end_date)

        # 응답 데이터 구성
        response = {
            "status": "success",
            "data": {
                "dates": [...],  # 날짜 리스트
                "series": {...},  # 시계열 데이터
                "metadata": {...}  # 메타데이터
            }
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/exchange-rates")
def get_exchange_rates(
    pairs: str = Query(..., description="쉼표로 구분된 통화쌍"),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """환율 데이터 조회"""
    # 위와 유사한 구조
    pass

@app.get("/api/statistics")
def get_statistics(
    data_type: str = Query(..., description="interest_rate or exchange_rate"),
    items: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """통계 데이터 조회"""
    # 통계 계산 로직
    pass
```

---

## 🧪 테스트 데이터

개발/테스트를 위한 샘플 응답 데이터는 다음과 같이 생성할 수 있습니다:

```python
import pandas as pd
import numpy as np

def generate_sample_response(item_name, start_date, end_date, base_value, category):
    """샘플 응답 데이터 생성"""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    values = base_value + np.cumsum(np.random.randn(len(dates)) * 0.02)

    return {
        "name": item_name,
        "category": category,
        "values": values.tolist(),
        "unit": "%"
    }
```

---

## 📌 주요 포인트

1. **날짜 형식**: 모든 날짜는 `YYYY-MM-DD` 형식 (ISO 8601)
2. **데이터 구조**: `dates` 배열과 `series` 딕셔너리로 분리하여 중복 제거
3. **메타데이터**: 총 레코드 수, 날짜 범위 등 부가 정보 제공
4. **에러 처리**: 명확한 에러 메시지와 상태 코드
5. **단위**: 각 시리즈에 단위 정보 포함 (%, KRW 등)

---

**작성일:** 2025-10-23
**버전:** 1.0
