"""
bigkinds_full_news.csv → PostgreSQL news_articles 적재용 CSV 생성 (신규 스크립트).

기존 merge_full_content.py 는 그대로 두고, 크롤러가 넣은 url / image_urls 가 있을 때
DB 컬럼(url, image_url)까지 맞춘 파이프용 산출물을 만든다.

입력 (필수):
  news_id, published_date, press, title, full_content, category

입력 (선택):
  url, image_urls   — crawl_news_body.py 가 채운 컬럼 (없거나 비었으면 CSV 에서 빈 칸 → 적재 시 NULL)

출력:
  news_articles_import.csv
  컬럼 순서(DB와 COPY 시 맞추기 쉽게):
    news_id, date, press, title, content, main_category, summary,
    image_url, url

용법:
  1) 선택: ai-news-summary-service/backend/sql/add_news_article_url_column.sql 실행(url 컬럼)
  2) data 폴더 기준 기본값은 같은 폴더의 bigkinds_full_news.csv 이다.
     파일이 다른 곳(open 루트 등)이면 --input 으로 전체 경로를 넘긴다.
  예) py run_preprocess_bigkinds.py --input "..\\..\\bigkinds_full_news.csv"
  예) backend 에서: py run_preprocess_bigkinds.py (--input 선택)
  또는) py preprocess_bigkinds_for_news_articles.py --input "경로..."

PostgreSQL / pgAdmin Import 옵션에 맞춤:
  - 구분 문자(Delimiter): | (파이프, 쉼표 아님)
  - 인용 문자(Quote): "
  - 이스케이프(Escape): "
  Encoding: UTF8
  헤더: 예

PostgreSQL \\copy 예 (기본 따옴표·이스케이프 = 가독 위해 생략 가능):
  \\copy news_articles (
    news_id, date, press, title, content, main_category, summary,
    image_url, url
  ) FROM 'news_articles_import.csv' WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER '|',
    NULL ''
  );

IMPORTANT:
  Columns / \\copy 에 지정하는 컬럼 **개수·순서**가 CSV 한 줄 필드 개수와 **반드시 같아야** 합니다.
  (예: 파일 9칸인데 DB 목록만 8칸 지정하면 파싱이 밀려 한글 UTF-8이 깨져 보입니다.)
  url 컬럼이 없거나 CSV에서 omit 하려면: py ... --no-url

이전 백슬래시(\\) 이스케이프·따옴표 없는 CSV 형식은 pgAdmin 기본값과 다릅니다.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_FULL_CSV = BASE_DIR / "bigkinds_full_news.csv"
OUTPUT_CSV = BASE_DIR / "news_articles_import.csv"
BACKUP_CSV = OUTPUT_CSV.with_suffix(OUTPUT_CSV.suffix + ".bak")

# PostgreSQL 타입 길이 (스키마에 맞춤)
PRESS_MAX = 50
MAIN_CAT_MAX = 20


def clean_text(text: str) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = str(text)
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return " ".join(text.split()).strip()


def strip_body_boilerplate(body: str) -> str:
    """본문 끝의 저작권·무단 전재 안내 등을 잘라낸다 (merge_full_content 와 동일 의도)."""
    if not body:
        return ""
    cut_markers = [
        "\n무단 전재",
        "무단 전재",
        "재배포 금지",
        "[저작권자",
        "저작권자 ⓒ",
        "[ⓒ",
        "[COPYRIGHT",
        "기사공유 및 재배포",
        "--- AD ---",
        "▶",
        "※ 기사 제공",
        "※ 본 메일은 정보",
        "※ 국외소재 회사원",
        "※ 무단복제 및 금지",
        "※ 무단 전재 및",
    ]
    t = body.strip()
    cut_at = len(t)
    # 앞쪽 제목 줄의 '무단' 오탐 줄이도록, 탐색은 하반부부터도 가능하지만 간단히 전체 검색 후
    # 가능한 마지막 큰 블록 이전까지 자르기보다 첫 매칭에서 자름 (통상 본문 끝 블록)
    for marker in cut_markers:
        idx = t.find(marker)
        if idx != -1:
            cut_at = min(cut_at, idx)
    t = t[:cut_at].rstrip()
    return t


def normalize_pg_date(raw: str) -> str:
    """YYYY-MM-DD 문자열 반환·실패 시 clean_text 결과 그대로(검증에서 걸림)."""
    s = clean_text(raw)
    m = re.search(r"(20\d{2})\D(\d{1,2})\D(\d{1,2})", s)
    if not m:
        return s
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if mo < 1 or mo > 12 or d < 1 or d > 31:
        return s
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _empty_optional_to_na(val):
    """url / 이미지 / 요약 빈값 → 적재 시 NULL 이 되도록 pd.NA (CSV 에서 빈 칸으로 출력)."""
    if val is None or val is pd.NA:
        return pd.NA
    if isinstance(val, float) and pd.isna(val):
        return pd.NA
    if isinstance(val, str) and val.strip() == "":
        return pd.NA
    return val


def apply_pg_nullable_optional_columns(df: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    out = df.copy()
    for c in columns:
        out[c] = out[c].map(_empty_optional_to_na)
    return out


def clip_len(value: str, max_len: int, label: str, warned: dict) -> str:
    if len(value) <= max_len:
        return value
    if not warned.get(label):
        print(f"[경고] {label} 길이가 {max_len} 초과 행은 잘립니다. (첫 경고만 표시)")
        warned[label] = True
    return value[:max_len]


def load_full_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    print(f"입력 로드 {path}: {len(df)}행 / 컬럼 {list(df.columns)}")
    required = ["news_id", "published_date", "press", "title", "full_content", "category"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    warned: dict[str, bool] = {}

    def col(name: str) -> pd.Series:
        return df[name] if name in df.columns else pd.Series([""] * len(df))

    urls = col("url").map(clean_text)
    imgs = col("image_urls").map(clean_text)

    out = pd.DataFrame({
        "news_id": df["news_id"].map(clean_text),
        "date": df["published_date"].map(normalize_pg_date),
        "press": df["press"].map(lambda x: clip_len(clean_text(x), PRESS_MAX, "press", warned)),
        "title": df["title"].map(clean_text),
        "content": df["full_content"].map(
            lambda x: clean_text(strip_body_boilerplate(str(x)))
        ),
        "main_category": df["category"].map(
            lambda x: clip_len(clean_text(x), MAIN_CAT_MAX, "main_category", warned)
        ),
        "summary": pd.Series([pd.NA] * len(df), dtype=object),
        "image_url": imgs,
        "url": urls,
    })

    # date 패턴 검증
    ok_date = out["date"].str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)

    before = len(out)
    out = out[
        ok_date
        & (out["news_id"] != "")
        & (out["title"] != "")
        & (out["content"] != "")
        & (out["main_category"] != "")
    ].copy()
    after = len(out)
    if before != after:
        print(f"필터 제거 {before - after}건 ({before} -> {after})")

    dup_before = len(out)
    out = out.drop_duplicates(subset=["news_id"], keep="first")
    if len(out) != dup_before:
        print(f"news_id 중복 제거 {dup_before - len(out)}건")

    return out


def save_pipe_csv(df: pd.DataFrame, path: Path) -> None:
    """pgAdmin Import 기본 형식과 맞춤: 구분자 |, 문자열 따옴표 \", \"\" 이스케이프."""
    # QUOTE_NONNUMERIC 안전하게 전부 문자열로 (숫자로 인식돼 따옴표 빠지는 현상 방지)
    out = df.astype("string")
    out.to_csv(
        path,
        index=False,
        sep="|",
        encoding="utf-8",
        quoting=csv.QUOTE_NONNUMERIC,
        doublequote=True,
        lineterminator="\n",
        na_rep="",
    )


def verify_pipe_csv_structure(path: Path, expected_ncols: int) -> bool:
    """
    작성한 CSV(pgAdmin 규격: | 구분·표준 따옴표)을 csv.reader 로 파싱해 필드 개수 검증한다.
    """
    bad: list[tuple[int, int, str]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="|")
        try:
            for row_no, row in enumerate(reader):
                if row_no == 0:
                    if len(row) != expected_ncols:
                        print(
                            f"[경고] 헤더 필드 개수 불일치: {len(row)} (기대 {expected_ncols})"
                        )
                        return False
                    continue
                if len(row) != expected_ncols:
                    hint = row[0][:72] + "..." if row and len(row[0]) > 75 else (
                        row[0] if row else ""
                    )
                    bad.append((row_no + 1, len(row), hint))
                    if len(bad) >= 10:
                        break
        except csv.Error as e:
            print(f"[경고] CSV 파싱 실패: {e}")
            return False

    if bad:
        print("[경고] 데이터 행 필드 개수 불일치 (pgAdmin 형식 파싱 기준):")
        for csv_row, n_fields, fid in bad:
            print(f"  CSV 레코드 {csv_row}: 필드 {n_fields}개 (기대 {expected_ncols}) news_id? {fid!r}")
        return False
    return True


def main() -> None:
    p = argparse.ArgumentParser(description="bigkinds_full_news.csv → news_articles_import.csv")
    p.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_FULL_CSV,
        help=f"입력 CSV (기본: {DEFAULT_FULL_CSV})",
    )
    p.add_argument(
        "--no-url",
        action="store_true",
        help="출력 마지막 url 열을 생략 (테이블에 url 컬럼이 없을 때 Import 컬럼 개수와 맞추기)",
    )
    args = p.parse_args()

    if not args.input.exists():
        lines = [
            f"입력 파일이 없습니다: {args.input}",
            "",
            "크롤 CSV 경로 전체를 --input 으로 지정해야 합니다. (리터럴 ... 는 PowerShell 명령이 아닙니다.)",
            f"스크립트 기본 검색 위치: {DEFAULT_FULL_CSV}",
        ]
        # 흔한 배치: open/bigkinds_full_news.csv 한 단계 바깥
        sug = (BASE_DIR / ".." / ".." / "bigkinds_full_news.csv").resolve()
        if sug.exists():
            lines.extend(
                (
                    "",
                    "같은 드라이브에 다음 후보 파일이 있습니다:",
                    f'  "{sug}"',
                    "",
                    "data 폴더에서 이렇게 실행하세요:",
                    f'  py run_preprocess_bigkinds.py --input "{sug}"',
                    "",
                    '또는: py preprocess_bigkinds_for_news_articles.py --input "' + str(sug) + '"',
                )
            )
        raise FileNotFoundError("\n".join(lines))

    full_df = load_full_csv(args.input)
    out_df = transform(full_df)

    cols = [
        "news_id", "date", "press", "title", "content",
        "main_category", "summary", "image_url", "url",
    ]
    if args.no_url:
        cols = [c for c in cols if c != "url"]
    out_df = out_df[cols]
    nullable = ("summary", "image_url", "url")
    nullable = tuple(c for c in nullable if c in cols)
    out_df = apply_pg_nullable_optional_columns(out_df, nullable)

    if OUTPUT_CSV.exists():
        shutil.copy2(OUTPUT_CSV, BACKUP_CSV)
        print(f"기존 출력 백업: {BACKUP_CSV}")

    save_pipe_csv(out_df, OUTPUT_CSV)

    if not verify_pipe_csv_structure(OUTPUT_CSV, expected_ncols=len(cols)):
        if BACKUP_CSV.exists():
            shutil.copy2(BACKUP_CSV, OUTPUT_CSV)
        raise ValueError(
            "| 구분자 검증 실패. 출력을 이전 상태로 되돌렸습니다." if BACKUP_CSV.exists() else
            "| 구분자 검증 실패."
        )

    print(f"\n변환 완료: {OUTPUT_CSV}")
    print(f"최종 행 수: {len(out_df)}")
    print("\nPostgreSQL Import 시 아래 순서 그대로 지정해야 합니다 (컬럼 개수 불일치 → 한글 깨짐처럼 보임):\n")
    print("  " + ", ".join(cols))

    if "url" in cols:
        print(
            "\nurl 테이블 컬럼이 없으면 DDL 적용 또는 전처리에 --no-url 로 다시 생성하세요:\n"
            "  ai-news-summary-service/backend/sql/add_news_article_url_column.sql"
        )


if __name__ == "__main__":
    main()
