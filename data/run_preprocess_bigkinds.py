"""
전처리 스크립트를 data 폴더 안에서 실행할 때 편하게 쓰는 래퍼.

예 (입력 파일이 같은 data 폴더에 없을 때 open 루트 CSV 지정):

  py run_preprocess_bigkinds.py --input ..\\..\\bigkinds_full_news.csv

또는 절대 경로:

  py run_preprocess_bigkinds.py --input C:\\Users\\jundo\\Desktop\\open\\bigkinds_full_news.csv
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_MAIN = _SCRIPT_DIR / "preprocess_bigkinds_for_news_articles.py"


def main() -> None:
    if not _MAIN.exists():
        raise SystemExit(f"메인 스크립트 없음: {_MAIN}")
    cmd = [sys.executable, str(_MAIN), *sys.argv[1:]]
    raise SystemExit(subprocess.call(cmd, cwd=str(_SCRIPT_DIR)))


if __name__ == "__main__":
    main()
