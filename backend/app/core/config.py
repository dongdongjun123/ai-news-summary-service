import json
import logging
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)

# config.py -> core -> app -> backend
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


def _parse_cors_origins(raw: str) -> List[str]:
    """
    .env 에서 허용할 Origin 목록 파싱.
    - JSON 배열: ["http://localhost:5173", ...] (도구가 자동 생성할 때 많음)
    - 쉼표 구분: http://localhost:5173,http://127.0.0.1:5173
    JSON 문자열을 쉼표로만 split 하면 "["가 붙은 잘못된 Origin 이라 CORS 가 전부 실패한다.
    """
    raw = (raw or "").strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(
                "[backend] CORS_ORIGINS 가 JSON처럼 보이지만 파싱 실패, 쉼표 분리로 fallback"
            )
        else:
            if isinstance(data, list):
                return [str(item).strip() for item in data if str(item).strip()]
            return []
    return [chunk.strip() for chunk in raw.split(",") if chunk.strip()]


class Settings(BaseSettings):
    # Neon 등 클라우드: 대시보드 Connection string 을 그대로 넣으면 DB_* 보다 우선
    # 예) postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
    DATABASE_URL: str = ""

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    # Neon / 대부분의 클라우드 Postgres 는 require. 로컬 Docker·pgAdmin 은 보통 비움
    DB_SSLMODE: str = ""
    DB_CONNECT_TIMEOUT: int = 5

    # localhost 는 Windows에서 [::1] 로 붙어 summarizer 가 127.0.0.1 만 열어둔 경우 실패함
    SUMMARIZER_URL: str = "http://127.0.0.1:8001"
    SUMMARIZER_TIMEOUT: float = 30.0

    @field_validator("SUMMARIZER_URL", mode="after")
    @classmethod
    def _normalize_summarizer_localhost(cls, v: str) -> str:
        """httpx 가 localhost → IPv6 로 붙으면 127.0.0.1 에만 떠 있는 요약 서버에 연결 실패할 수 있음."""
        if not v:
            return v
        return (
            v.replace("://localhost:", "://127.0.0.1:")
            .replace("://LOCALHOST:", "://127.0.0.1:")
        ).rstrip("/")

    # 쉼표 구분 문자열로 받고 cors_origins property 에서 list 로 변환.
    # (List[str] 로 직접 받으면 pydantic-settings 가 JSON 파싱부터 시도해 에러가 남)
    # Vite/브라우저가 [::1]:5173 으로 접속하면 Origin 헤더가 여기 포함돼야 CORS 통과
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://[::1]:5173"
    )

    STATS_CORPUS_DAYS: int = 90
    STATS_RECENT_N: int = 4
    STATS_TOP_N: int = 8
    STATS_USE_LLM: bool = False
    STATS_USE_KEYBERT: bool = True  # 연관어: KeyBERT+임베딩 (실패 시 규칙 기반으로 fallback)

    # False: published_at 은 DB news_articles.date 와 동일 (클라이언트·pgAdmin 과 맞춤)
    # True: date 컬럼 불신 시 본문/ID 로 보조 날짜
    DISPLAY_DATE_FALLBACK: bool = False

    # false: 요약(summarizer)·언급량/연관어(stat_summary) 호출 안 함 — DB 조회만
    ENABLE_AI: bool = False

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        return _parse_cors_origins(self.CORS_ORIGINS)

    @staticmethod
    def _normalize_database_url(raw: str) -> str:
        """Neon connection string → SQLAlchemy + psycopg3 형식."""
        url = raw.strip()
        if url.startswith("postgres://"):
            url = "postgresql+psycopg://" + url[len("postgres://") :]
        elif url.startswith("postgresql://") and "+psycopg" not in url.split("://", 1)[0]:
            url = "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def database_url(self) -> str:
        from urllib.parse import quote_plus

        if self.DATABASE_URL.strip():
            return self._normalize_database_url(self.DATABASE_URL)

        base = (
            f"postgresql+psycopg://"
            f"{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        if self.DB_SSLMODE.strip():
            sep = "&" if "?" in base else "?"
            return f"{base}{sep}sslmode={quote_plus(self.DB_SSLMODE.strip())}"
        return base


settings = Settings()

logger.warning(
    "[backend] CORS_ORIGINS(파싱 후)=%s",
    settings.cors_origins,
)

# 부팅 시 환경 정보 한 줄로 로그 (비밀번호 길이만 노출)
logger.warning(
    "[backend] env_file=%s exists=%s DB_USER=%r DB_PASSWORD_len=%d DB_HOST=%s DB_NAME=%s",
    _ENV_FILE,
    _ENV_FILE.exists(),
    settings.DB_USER,
    len(settings.DB_PASSWORD or ""),
    settings.DB_HOST,
    settings.DB_NAME,
)

if not settings.DATABASE_URL.strip() and not settings.DB_PASSWORD:
    logger.error(
        "[backend] DB_PASSWORD 가 비어 있습니다. Neon 이면 DATABASE_URL 또는 backend/.env 를 확인하세요."
    )

logger.warning("[backend] SUMMARIZER_URL=%s", settings.SUMMARIZER_URL)
logger.warning("[backend] DISPLAY_DATE_FALLBACK=%s", settings.DISPLAY_DATE_FALLBACK)
logger.warning("[backend] ENABLE_AI=%s", settings.ENABLE_AI)
