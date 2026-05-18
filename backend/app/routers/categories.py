from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.category import Category
from app.utils.category_mapping import to_front_category


router = APIRouter(prefix="/api", tags=["categories"])


@router.get("/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    stmt = select(Category.name).order_by(Category.name)
    rows = db.execute(stmt).scalars().all()
    return [to_front_category(name) for name in rows]
