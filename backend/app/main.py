"""
FastAPI 백엔드 엔트리포인트.

실행 위치/경로 차이를 흡수하기 위해 import 전에 sys.path 를 보정한다.
  - backend/        : `from app.X` 형태 import 가능
  - 프로젝트 루트   : `from stat_summary.X` / `from summarizer.X` 가능
"""

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _THIS_DIR.parent
_PROJECT_ROOT = _BACKEND_DIR.parent

for path in (_BACKEND_DIR, _PROJECT_ROOT):
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)


from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.routers import categories, health, news  # noqa: E402


app = FastAPI(title="AI News Summary Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(categories.router)
app.include_router(news.router)
