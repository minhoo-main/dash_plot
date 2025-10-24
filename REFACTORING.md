# 리팩토링 문서

## 개요

2025-10-24에 dash_plot 프로젝트를 대대적으로 리팩토링하여 모놀리식 구조에서 모듈화된 구조로 개선했습니다.

## 리팩토링 목표

1. **모듈화**: 697줄의 단일 파일을 기능별로 분리
2. **재사용성**: 차트와 컴포넌트를 독립적으로 사용 가능하도록 개선
3. **테스트 가능성**: 각 모듈을 독립적으로 테스트할 수 있도록 구조화
4. **유지보수성**: 코드 수정 및 확장이 용이하도록 개선
5. **가독성**: 명확한 관심사 분리로 코드 이해도 향상

## 변경 사항

### 이전 구조 (모놀리식)

```
dash_plot/
├── app.py (697줄)           # 모든 기능이 한 파일에 집중
├── src/
│   ├── api_client.py
│   └── db_config.py
└── assets/
```

### 새로운 구조 (모듈화)

```
dash_plot/
├── app.py (68줄)            # 메인 엔트리포인트 (간결화, 90% 감소)
├── config.py                # 전역 설정 및 상수
├── app/
│   ├── __init__.py
│   ├── layouts/             # UI 레이아웃
│   │   ├── __init__.py
│   │   ├── main_layout.py
│   │   ├── control_panel.py
│   │   └── charts_section.py
│   ├── components/          # 재사용 가능한 컴포넌트
│   │   ├── __init__.py
│   │   ├── charts.py
│   │   └── tables.py
│   ├── callbacks/           # 콜백 함수
│   │   ├── __init__.py
│   │   ├── ui_callbacks.py
│   │   ├── data_callbacks.py
│   │   └── chart_callbacks.py
│   └── utils/               # 유틸리티 함수
│       ├── __init__.py
│       ├── data_utils.py
│       └── chart_utils.py
├── src/                     # 기존 유지
│   ├── api_client.py
│   └── db_config.py
├── tests/                   # 테스트 (새로 추가)
│   ├── __init__.py
│   └── test_utils.py
└── assets/                  # 기존 유지
```

## 모듈별 설명

### 1. config.py
- 애플리케이션 전역 설정 및 상수 정의
- 데이터 타입 옵션, 차트 설정, 색상 등
- 하드코딩된 값들을 중앙 집중화

### 2. app/layouts/
레이아웃 관련 모듈:
- `main_layout.py`: 메인 레이아웃 구성
- `control_panel.py`: 컨트롤 패널 (필터, 날짜 선택 등)
- `charts_section.py`: 차트 섹션 레이아웃

### 3. app/components/
재사용 가능한 컴포넌트:
- `charts.py`: 차트 생성 함수
  - `create_timeseries_chart()`: 시계열 차트 + 히스토그램
  - `create_spread_chart()`: 스프레드 차트 + 히스토그램
- `tables.py`: 테이블 컴포넌트
  - `create_statistics_table()`: 통계 테이블
  - `create_spread_statistics_table()`: 스프레드 통계 테이블

### 4. app/callbacks/
콜백 함수를 기능별로 분류:
- `ui_callbacks.py`: UI 상태 관련 콜백 (드롭다운, 버튼 등)
- `data_callbacks.py`: 데이터 로드 콜백
- `chart_callbacks.py`: 차트 업데이트 콜백

### 5. app/utils/
유틸리티 함수:
- `data_utils.py`: 데이터 처리 함수
  - `normalize_data()`: 데이터 정규화
  - `calculate_spread()`: 스프레드 계산
  - `calculate_spread_statistics()`: 스프레드 통계
  - `classify_items_by_type()`: 항목 분류
- `chart_utils.py`: 차트 관련 유틸리티
  - `should_use_secondary_axis()`: 보조 축 사용 여부 결정
  - `get_chart_colors()`: 차트 색상 가져오기

### 6. tests/
테스트 코드 추가:
- `test_utils.py`: 유틸리티 함수 테스트
  - 모든 데이터 처리 함수 테스트
  - 차트 유틸리티 함수 테스트

## 주요 개선사항

### 1. 코드 라인 수 감소
- app.py: 697줄 → 68줄 (90% 감소)
- 기능별로 분산되어 각 모듈은 50-150줄 수준

### 2. 관심사 분리 (Separation of Concerns)
- 레이아웃과 로직 분리
- UI와 데이터 처리 분리
- 차트 생성과 콜백 분리

### 3. 재사용성 향상
- 차트 컴포넌트를 독립적으로 사용 가능
- 유틸리티 함수를 다른 프로젝트에서도 활용 가능

### 4. 테스트 가능성
- 각 모듈을 독립적으로 테스트 가능
- 단위 테스트 작성 및 통과 확인

### 5. 유지보수성
- 기능 추가/수정 시 해당 모듈만 수정
- 명확한 파일 구조로 코드 찾기 쉬움

### 6. 확장성
- 새로운 차트 타입 추가 용이
- 새로운 콜백 추가 용이
- 설정 변경 용이

## 마이그레이션 가이드

### 기존 코드 백업
원본 파일은 `app_old_monolith.py`로 백업되었습니다.

### 사용 방법 (변경 없음)
```bash
# 동일하게 실행
python app.py
```

### API 변경 사항
없음 - 내부 구조만 변경되었으며 외부 인터페이스는 동일합니다.

## 테스트 실행

```bash
# 유틸리티 함수 테스트
python tests/test_utils.py

# 출력 예시:
# ==================================================
# Running utility function tests...
# ==================================================
#
# Testing normalize_data...
# ✓ normalize_data passed
# Testing calculate_spread...
# ✓ calculate_spread passed
# ...
# ==================================================
# All tests passed! ✓
# ==================================================
```

## 향후 개선 계획

1. **추가 테스트**
   - 콜백 함수 테스트
   - 통합 테스트
   - UI 테스트

2. **타입 힌팅**
   - 모든 함수에 타입 힌트 추가
   - mypy를 사용한 정적 타입 검사

3. **로깅**
   - 구조화된 로깅 추가
   - 디버깅 개선

4. **에러 처리**
   - 통일된 에러 처리 메커니즘
   - 사용자 친화적 에러 메시지

5. **성능 최적화**
   - 데이터 캐싱
   - 차트 렌더링 최적화

## 기여자

- 리팩토링 수행: 2025-10-24
- 테스트 통과: ✓

## 라이선스

MIT License (기존과 동일)
