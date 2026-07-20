# 실습 2 - 파일 입출력, 예외 처리, Pydantic 검증 파이프라인
# 광주캠퍼스 4반 권경현
#
# Python_Practice2_Data.json(Sales 데이터)을 읽어 Pydantic으로 검증하고,
# 통과한 레코드와 실패한 레코드를 나눠 각각 CSV와 JSON으로 저장한 뒤 다시 읽어 확인한다.
#   1) safe_load_csv: 파일을 읽되 없으면 None을 돌려주는 안전한 로더
#   2) SalesRecord: region과 month는 필수, amount는 양수, category는 선택인 스키마
#   3) 검증 파이프라인: 통과는 valid, 실패는 errors로 분리
#   4) valid는 CSV로, errors는 JSON으로 저장하고 다시 읽어 건수 확인
#
# 실행: python 광주캠퍼스_4반_권경현.py

import csv
import json
import logging
import sys
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(message)s", stream=sys.stdout
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Python_Practice2_Data.json"
VALID_CSV = BASE_DIR / "valid_records.csv"
ERRORS_JSON = BASE_DIR / "errors.json"


def safe_load_csv(path):
    """파일을 읽어 dict 리스트로 반환한다. 파일이 없거나 형식이 잘못되면 None을 반환한다."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        logger.info("로딩 성공: %s (%d건)", Path(path).name, len(data))
        return data
    except FileNotFoundError:
        logger.error("파일이 없습니다: %s", path)
        return None
    except json.JSONDecodeError as e:
        logger.error("JSON 형식 오류: %s", e)
        return None
    finally:
        print("로딩 종료")


class SalesRecord(BaseModel):
    """매출 레코드 스키마. region과 month는 비어있으면 안 되고, amount는 0보다 커야 하며 category는 선택이다."""

    region: str = Field(min_length=1)
    category: str | None = None
    amount: int = Field(gt=0)
    month: str = Field(min_length=1)


def validate_records(raw_data):
    """raw_data를 하나씩 SalesRecord로 변환해 통과분(valid)과 실패분(errors)으로 나눈다."""
    valid = []
    errors = []
    for row in raw_data:
        try:
            valid.append(SalesRecord(**row))
        except ValidationError as e:
            errors.append({"row": row, "error": e.errors()})
    return valid, errors


def save_valid_csv(valid, path):
    """검증을 통과한 레코드를 CSV로 저장한다. 모델을 model_dump()로 dict 변환해서 기록."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["region", "category", "amount", "month"])
        writer.writeheader()
        for record in valid:
            writer.writerow(record.model_dump())


def save_errors_json(errors, path):
    """실패한 레코드를 JSON으로 저장한다. 한글이 깨지지 않도록 ensure_ascii=False로 저장."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(errors, f, ensure_ascii=False, indent=2, default=str)


def main():
    # 1) 안전한 로더로 원본 데이터 읽기
    raw = safe_load_csv(DATA_FILE)
    if raw is None:
        return
    print(f"불러온 원본 레코드: {len(raw)}건\n")

    # 없는 파일을 주면 None을 반환하는지 확인
    print("[없는 파일 로딩 시도]")
    missing = safe_load_csv(BASE_DIR / "없는파일.json")
    print("반환값:", missing, "\n")

    # 원본은 모두 정상이라, 검증이 잘못된 입력을 제대로 걸러내는지 보기 위해
    # 문제가 있는 예시(빈 region, 음수 amount, 빈 month)를 함께 넣어 파이프라인을 돌린다.
    sample_errors = [
        {"region": "", "category": "전자", "amount": 1500, "month": "2024-01"},
        {"region": "부산", "category": "의류", "amount": -200, "month": "2024-02"},
        {"region": "대구", "category": "식품", "amount": 500, "month": ""},
    ]
    raw_data = raw + sample_errors

    # 3) 검증 후 valid / errors 분리
    valid, errors = validate_records(raw_data)
    print(f"검증 결과: valid {len(valid)}건, errors {len(errors)}건\n")

    # 실패한 레코드의 오류 내용 출력
    print("[검증 실패 상세]")
    for item in errors:
        detail = item["error"][0]
        field = detail["loc"][0]
        print(f"  입력 {item['row']} -> {field}: {detail['msg']}")
    print()

    # 4) 저장하고 다시 읽어 건수 확인
    save_valid_csv(valid, VALID_CSV)
    save_errors_json(errors, ERRORS_JSON)
    with open(VALID_CSV, encoding="utf-8") as f:
        reloaded = list(csv.DictReader(f))
    print(f"CSV 저장 후 재로딩: {len(reloaded)}건")
    print(f"저장 파일: {VALID_CSV.name}, {ERRORS_JSON.name}")

    # 결과 확인용 검증
    assert missing is None
    assert len(valid) == len(raw)
    assert len(errors) == len(sample_errors)
    assert len(reloaded) == len(valid)
    print("\n검증 통과")


if __name__ == "__main__":
    main()
