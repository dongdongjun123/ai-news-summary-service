from sqlalchemy import Column, String

from app.core.db import Base


class Category(Base):
    __tablename__ = "categories"

    name = Column(String(20), primary_key=True)
