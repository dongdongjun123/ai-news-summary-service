"""
news_cleaned/ 폴더의 모든 cleaned_news_*.csv 파일을 하나로 병합.

입력:
  ai-news-summary-service/data/news_cleaned/cleaned_news_*.csv
  (각각 merge_full_content.py 가 만들어낸 동일 포맷)
    utf-8, '|' 구분, QUOTE_NONE, escapechar='\\'
    컬럼: news_id, date, press, title, content, main_category

처리:
  - 모든 CSV 를 같은 포맷 옵션으로 읽어 concat
  - news_id 기준 중복 제거
  - 기존 cleaned_news.csv 가 있으면 자동 백업(.bak) 후 덮어쓰기
  - 저장 후 컬럼 개수 검증, 실패 시 백업에서 자동 복구

출력:
  ai-news-summary-service/data/cleaned_news.csv  (DB 적재용)
"""

import csv
import shutil
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "news_cleaned"
OUTPUT_CSV = BASE_DIR / "cleaned_news.csv"
BACKUP_CSV = BASE_DIR / "cleaned_news.csv.bak"


def load_one(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep="|",
        encoding="utf-8",
        dtype=str,
        keep_default_na=False,
        quoting=csv.QUOTE_NONE,
        escapechar="\\",
    )


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"입력 폴더가 없습니다: {INPUT_DIR}")

    csv_files = sorted(INPUT_DIR.glob("cleaned_news_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"병합할 CSV 가 없습니다: {INPUT_DIR}")

    print(f"발견된 CSV: {len(csv_files)}개")

    dfs = []
    for path in csv_files:
        df = load_one(path)
        print(f"  - {path.name}: {len(df)}건")
        dfs.append(df)

    merged = pd.concat(dfs, ignore_index=True)
    print(f"\n병합 직후 행 수: {len(merged)}")

    # news_id 기준 중복 제거 (다른 카테고리/날짜로 크롤된 동일 기사 통합)
    before = len(merged)
    merged = merged.drop_duplicates(subset=["news_id"], keep="first")
    after = len(merged)
    if before != after:
        print(f"news_id 중복 {before - after}건 제거 ({before} -> {after})")

    # 기존 cleaned_news.csv 백업
    if OUTPUT_CSV.exists():
        shutil.copy2(OUTPUT_CSV, BACKUP_CSV)
        print(f"기존 cleaned_news.csv 백업: {BACKUP_CSV}")

    # 같은 포맷으로 저장
    merged.to_csv(
        OUTPUT_CSV,
        index=False,
        sep="|",
        encoding="utf-8",
        quoting=csv.QUOTE_NONE,
        escapechar="\\",
        lineterminator="\n",
    )

    # 컬럼 개수 검증
    expected_pipes = len(merged.columns) - 1
    bad = []
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if line.count("|") != expected_pipes:
                bad.append((line_no, line[:200]))
                if len(bad) >= 10:
                    break

    if bad:
        print("\n[경고] 구분자 개수 불일치 라인 발견:")
        for line_no, sample in bad:
            print(f"  line {line_no}: {sample}")
        if BACKUP_CSV.exists():
            shutil.copy2(BACKUP_CSV, OUTPUT_CSV)
            raise ValueError(
                "CSV 구분자 검증 실패. cleaned_news.csv 를 백업에서 자동 복구했습니다."
            )
        raise ValueError("CSV 구분자 검증 실패. 백업이 없어 복구 불가.")

    print(f"\n병합 완료: {OUTPUT_CSV}")
    print(f"최종 행 수: {len(merged)}")
    print("\n카테고리 분포:")
    print(merged["main_category"].value_counts())


if __name__ == "__main__":
    main()
