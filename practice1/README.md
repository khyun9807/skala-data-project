# 실습 1 — 자료구조 집계 · 컴프리헨션 · 제너레이터

> SKALA 데이터분석 및 AIOps / Python 이해 · **Practice 1**
> 과제 명세: [../docs/실습과제_정리/실습_과제_정리.md](../docs/실습과제_정리/실습_과제_정리.md#practice-1--자료구조-집계-컴프리헨션-제너레이터)

## 디렉토리 구조

```
practice1/
├── 광주캠퍼스_4반_권경현.py          # 실습 1 제출 파일 (캠퍼스명_반_이름.py 규칙)
├── data/
│   └── Python_Practice1_Data.json   # Sales 데이터 100건 (원본: source/Python_Practice2_Data.json)
├── output/
│   └── 실행결과.txt                  # 실행 결과 캡처
└── README.md
```

> **데이터 출처 메모:** 원본 파일은 `source/Python_Practice2_Data.json` 이나, 내용(필드 `region·category·amount·month`)이 실습 1 명세의 `Python_Practice1_Data.json`(Sales)과 동일하여 스펙 파일명으로 복사해 사용했습니다.

## 실행 방법

```bash
# 프로젝트 루트의 가상환경 사용
../.venv/bin/python 광주캠퍼스_4반_권경현.py
# 또는 practice1 디렉토리에서
python 광주캠퍼스_4반_권경현.py
```

## 구현 내용 (요구사항 4가지)

| # | 항목 | 사용 자료구조/기법 | 함수 |
|---|------|------------------|------|
| 1 | amount≥1000 필터 + 지역별 총매출 | 리스트/딕셔너리 **컴프리헨션** | `region_total_over_threshold` |
| 2 | 지역별 거래 건수 / 카테고리별 amount | **Counter** / **defaultdict** | `count_by_region`, `amounts_by_category` |
| 3 | amount>1000 행만 yield, 메모리 비교 | **제너레이터** + `sys.getsizeof` | `big_amount_generator` |
| 4 | month·category 총매출 집계 | **컴프리헨션 + defaultdict** | `monthly_category_total` |

## 체크포인트 (실행 시 assert 로 자동 검증)

- ✅ `region_total` 값 정확 — 지역별 합계 총합 == amount≥1000 전체 합계
- ✅ `Counter.most_common()` 건수 내림차순 정렬
- ✅ generator `sys.getsizeof` < list `sys.getsizeof` (208 < 472 bytes)
- ✅ TOP3 금액 내림차순 정렬 정확

실행 마지막에 `검증 통과` 가 출력되면 정상입니다.

## 감점 요소 대응

| 감점 대상 (감점) | 대응 |
|-----------------|------|
| 컴프리헨션 대신 for 루프만 사용 (-2) | 요구사항 1·4를 컴프리헨션으로 구현 |
| defaultdict 대신 `if key not in dict` (-1) | `defaultdict(list)` / `defaultdict(int)` 사용 |
| 제너레이터를 list로 변환해 비교 (-2) | 제너레이터 **객체 자체**의 크기를 리스트와 비교 (`list()` 변환 없음) |
| Counter 대신 직접 루프 카운팅 (-1) | `collections.Counter` 사용 |

## 평가 기준 대응 (Practice Rule 100점)

- **Code의 Comm.(20):** 파일 상단 머리말(개요·데이터·실행방법) + 함수별 docstring
- **코드 간결성(35):** 컴프리헨션/표준 라이브러리 활용, 불필요한 반복 지양
- **오류/예외 처리(35):** `load_sales()` 에서 `FileNotFoundError`·`JSONDecodeError` 처리
- **납기(10):** 기한 내 제출

> 제출 파일명은 규칙(`캠퍼스명_반_이름.py`)에 맞춰 `광주캠퍼스_4반_권경현.py` 로 되어 있습니다.
