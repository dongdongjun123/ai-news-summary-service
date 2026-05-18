from sqlalchemy import Column, Date, ForeignKey, String, Text

from app.core.db import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    news_id = Column(String(50), primary_key=True)
    date = Column(Date, nullable=False)
    press = Column(String(50))
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    main_category = Column(
        String(20),
        ForeignKey("categories.name"),
        nullable=False,
    )
    summary = Column(Text)
