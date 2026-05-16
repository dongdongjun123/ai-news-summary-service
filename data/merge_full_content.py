"""
bigkinds_full_news.csv (모달 크롤 풀텍스트) 를 DB 적재용 cleaned_news.csv 로 변환.

이 스크립트는 다른 CSV 를 읽지 않습니다. 오직 bigkinds_full_news.csv 한 개만
입력으로 받아 PostgreSQL COPY 에 그대로 들어갈 수 있는 cleaned_news.csv 를 생성합니다.

흐름:
  1) bigkinds_full_news.csv 로드 (utf-8-sig, ',' 구분)
  2) 컬럼 매핑:
        news_id          -> news_id
        published_date   -> date
        press            -> press
        title            -> title
        full_content     -> content   (boilerplate cutoff + 한 줄 정제)
        category         -> main_category
  3) 필수값 누락 행 제거 / news_id 기준 중복 제거
  4) 기존 cleaned_news.csv 가 있으면 자동 백업(.bak) 후 덮어쓰기
  5) 저장된 CSV 의 컬럼 개수 검증 (실패 시 백업에서 자동 복구)

산출물:
  cleaned_news.csv   (utf-8, '|' 구분, QUOTE_NONE, escapechar='\\\\')
"""

import csv
import shutil
from pathlib import Path

import pandas as pd

from preprocess_news_excel import clean_text, strip_body_boilerplate


BASE_DIR = Path(__file__).resolve().parent
FULL_CSV = BASE_DIR / "bigkinds_full_news.csv"
OUTPUT_CSV = BASE_DIR / "cleaned_news.csv"
BACKUP_CSV = BASE_DIR / "cleaned_news.csv.bak"


def load_full_csv() -> pd.DataFrame:
    df = pd.read_csv(
        FULL_CSV,
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )
    print(f"bigkinds_full_news.csv 로드: {len(df)}건 / 컬럼 {list(df.columns)}")

    required = ["news_id", "published_date", "press", "title", "full_content", "category"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"bigkinds_full_news.csv 에 필수 컬럼 누락: {missing}")

    return df


def transform(full_df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "news_id": full_df["news_id"].apply(clean_text),
        "date": full_df["published_date"].apply(clean_text),
        "press": full_df["press"].apply(clean_text),
        "title": full_df["title"].apply(clean_text),
        # 본문: 저작권/안내 cutoff -> CSV 안전 정제
        "content": full_df["full_content"].apply(
            lambda x: clean_text(strip_body_boilerplate(x))
        ),
        "main_category": full_df["category"].apply(clean_text),
    })

    # 필수값 누락 행 제거
    before = len(out)
    out = out.dropna(subset=["news_id", "date", "title", "content", "main_category"])
    out = out[
        (out["news_id"] != "")
        & (out["title"] != "")
        & (out["content"] != "")
        & (out["main_category"] != "")
    ]
    after = len(out)
    if before != after:
        print(f"필수값 누락 {before - after}건 제거 ({before} -> {after})")

    # news_id 중복 제거
    before = len(out)
    out = out.drop_duplicates(subset=["news_id"], keep="first")
    after = len(out)
    if before != after:
        print(f"news_id 중복 {before - after}건 제거 ({before} -> {after})")

    return out


def save_cleaned_csv(df: pd.DataFrame) -> None:
    df.to_csv(
        OUTPUT_CSV,
        index=False,
        sep="|",
        encoding="utf-8",
        quoting=csv.QUOTE_NONE,
        escapechar="\\",
        lineterminator="\n",
    )


def verify_pipe_count(expected_pipes: int) -> list:
    bad = []
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if line.count("|") != expected_pipes:
                bad.append((line_no, line[:200]))
                if len(bad) >= 10:
                    break
    return bad


def main() -> None:
    if not FULL_CSV.exists():
        raise FileNotFoundError(f"bigkinds_full_news.csv 가 없습니다: {FULL_CSV}")

    full_df = load_full_csv()
    out_df = transform(full_df)

    if OUTPUT_CSV.exists():
        shutil.copy2(OUTPUT_CSV, BACKUP_CSV)
        print(f"기존 cleaned_news.csv 백업: {BACKUP_CSV}")

    save_cleaned_csv(out_df)

    expected_pipes = len(out_df.columns) - 1
    bad = verify_pipe_count(expected_pipes)
    if bad:
        print("\n[경고] 구분자 개수 불일치 라인 발견:")
        for line_no, sample in bad:
            print(f"  line {line_no}: {sample}")
        if BACKUP_CSV.exists():
            shutil.copy2(BACKUP_CSV, OUTPUT_CSV)
            raise ValueError(
                "CSV 구분자 검증 실패. cleaned_news.csv 를 백업에서 자동 복구했습니다."
            )
        raise ValueError("CSV 구분자 검증 실패. 백업 파일이 없어 복구 불가.")

    print(f"\n변환 완료: {OUTPUT_CSV}")
    print(f"최종 행 수: {len(out_df)}")


if __name__ == "__main__":
    main()
