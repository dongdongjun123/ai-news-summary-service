"""
프론트가 사용하는 카테고리명과 DB(`categories.name`) 표기 차이를 흡수.
프론트 'IT과학' <-> DB 'IT_과학' 같이 표기만 다른 경우만 매핑한다.
"""

FRONT_TO_DB = {
    "IT과학": "IT_과학",
}
DB_TO_FRONT = {v: k for k, v in FRONT_TO_DB.items()}


def to_db_category(name: str) -> str:
    if not name:
        return name
    return FRONT_TO_DB.get(name, name)


def to_front_category(name: str) -> str:
    if not name:
        return name
    return DB_TO_FRONT.get(name, name)
