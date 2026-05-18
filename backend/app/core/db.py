from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_size=5,
    pool_pre_ping=False,
    pool_recycle=1800,
    future=True,
    connect_args={"connect_timeout": settings.DB_CONNECT_TIMEOUT},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
