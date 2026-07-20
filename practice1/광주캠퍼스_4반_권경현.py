# 실습 1 - 자료구조 집계, 컴프리헨션, 제너레이터
# 광주캠퍼스 4반 권경현
#
# Python_Practice1_Data.json(Sales 데이터 100건)을 읽어서 다음 네 가지를 처리한다.
#   1) 리스트, 딕셔너리 컴프리헨션으로 amount 1000 이상 필터링과 지역별 총매출 집계
#   2) Counter와 defaultdict로 지역별 거래 건수와 카테고리별 amount 목록 구하기
#   3) 제너레이터로 amount 1000 초과 행만 만들어 리스트와 메모리 크기 비교
#   4) month와 category 기준으로 총매출 집계
#
# 데이터 필드: region, category, amount, month
# 실행: python 광주캠퍼스_4반_권경현.py

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# 데이터 파일 경로. 스크립트 위치를 기준으로 잡아 실행 위치와 상관없이 찾도록 함
DATA_PATH = Path(__file__).resolve().parent / "data" / "Python_Practice1_Data.json"

# amount 기준값. 요구사항 1은 1000 이상, 요구사항 3은 1000 초과
THRESHOLD_GTE = 1000
THRESHOLD_GT = 1000


def load_sales(path: Path) -> list[dict]:
    """Sales JSON 파일을 읽어 dict 리스트로 반환한다.

    파일이 없거나 형식이 잘못된 경우 메시지를 남기고 프로그램을 종료한다.
    """
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("데이터 파일을 찾을 수 없습니다:", path)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print("JSON 파싱에 실패했습니다:", exc)
        sys.exit(1)


def region_total_over_threshold(sales: list[dict]) -> dict[str, int]:
    """amount 1000 이상 거래만 걸러서 지역별 총매출 dict를 만든다.

    먼저 리스트 컴프리헨션으로 조건에 맞는 거래를 뽑고,
    딕셔너리 컴프리헨션으로 지역별 합계를 계산한다.
    """
    big = [s for s in sales if s["amount"] >= THRESHOLD_GTE]
    regions = {s["region"] for s in big}
    return {
        region: sum(s["amount"] for s in big if s["region"] == region)
        for region in regions
    }


def count_by_region(sales: list[dict]) -> Counter:
    """지역별 거래 건수를 Counter로 센다."""
    return Counter(s["region"] for s in sales)


def amounts_by_category(sales: list[dict]) -> defaultdict[str, list[int]]:
    """카테고리별 amount 목록을 defaultdict(list)로 모은다."""
    bucket: defaultdict[str, list[int]] = defaultdict(list)
    for s in sales:
        bucket[s["category"]].append(s["amount"])
    return bucket


def big_amount_generator(sales: list[dict]):
    """amount 1000 초과 거래만 하나씩 내보내는 제너레이터.

    리스트로 미리 쌓지 않고 필요할 때 하나씩 넘겨서 메모리를 아낀다.
    """
    for s in sales:
        if s["amount"] > THRESHOLD_GT:
            yield s


def monthly_category_total(sales: list[dict]) -> dict[str, int]:
    """month와 category 기준으로 총매출을 집계한다.

    defaultdict(int)로 그룹별 합계를 누적한 다음,
    딕셔너리 컴프리헨션으로 보기 좋은 키 형태의 dict로 정리한다.
    """
    acc: defaultdict[tuple[str, str], int] = defaultdict(int)
    for s in sales:
        acc[(s["month"], s["category"])] += s["amount"]
    return {f"{month} {category}": total for (month, category), total in acc.items()}


def main() -> None:
    sales = load_sales(DATA_PATH)
    print("데이터 로딩 완료:", len(sales), "건\n")

    # 1) 지역별 총매출과 상위 3개 지역
    region_total = region_total_over_threshold(sales)
    ranked = sorted(region_total.items(), key=lambda kv: kv[1], reverse=True)
    print("[지역별 총매출 amount 1000 이상]")
    for region, total in ranked:
        print(f"  {region}: {total:,}")
    top3 = ranked[:3]
    print("  상위 3개:", top3, "\n")

    # 2) 지역별 거래 건수와 카테고리별 금액
    region_count = count_by_region(sales)
    print("[지역별 거래 건수]")
    print(" ", region_count.most_common())
    print("[카테고리별 건수와 합계]")
    for category, amounts in amounts_by_category(sales).items():
        print(f"  {category}: {len(amounts)}건, 합계 {sum(amounts):,}")
    print()

    # 3) 제너레이터와 리스트 메모리 비교
    # 제너레이터는 객체 그대로 크기를 재야 의미가 있으므로 list로 바꾸지 않는다
    gen = big_amount_generator(sales)
    big_list = [s for s in sales if s["amount"] > THRESHOLD_GT]
    gen_size = sys.getsizeof(gen)
    list_size = sys.getsizeof(big_list)
    print("[메모리 비교 amount 1000 초과]")
    print(f"  generator {gen_size} bytes, list {list_size} bytes ({len(big_list)}건)\n")

    # 4) 월과 카테고리별 총매출
    print("[월별 카테고리 매출]")
    for key, total in sorted(monthly_category_total(sales).items()):
        print(f"  {key}: {total:,}")

    # 결과 확인용 검증
    expected_sum = sum(s["amount"] for s in sales if s["amount"] >= THRESHOLD_GTE)
    assert sum(region_total.values()) == expected_sum
    mc = region_count.most_common()
    assert all(mc[i][1] >= mc[i + 1][1] for i in range(len(mc) - 1))
    assert gen_size < list_size
    assert all(top3[i][1] >= top3[i + 1][1] for i in range(len(top3) - 1))
    print("\n검증 통과")


if __name__ == "__main__":
    main()
