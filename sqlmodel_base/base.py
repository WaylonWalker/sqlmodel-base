from typing import Optional

from pydantic import BaseModel, validator
from rich.console import Console
from sqlalchemy import func
from sqlmodel import Field, Session, SQLModel, create_engine, select

console = Console()


def get_session():
    with Session(engine) as session:
        yield session


class PagedResult(BaseModel):
    items: list
    total: int
    page: int
    next_page: Optional[int]
    page_size: int


class Base(SQLModel):
    def create(self):
        with Session(engine) as session:
            validated = self.model_validate(self)
            session.add(self.sqlmodel_update(validated))
            session.commit()
            session.refresh(self)
            return self

    @classmethod
    def get(cls, id):
        with Session(engine) as session:
            return session.get(cls, id)

    @classmethod
    def get_all(cls):
        with Session(engine) as session:
            return session.exec(select(cls)).all()

    @classmethod
    def get_count(cls):
        with Session(engine) as session:
            return session.exec(func.count(Hero.id)).scalar()

    @classmethod
    def get_first(cls):
        with Session(engine) as session:
            return session.exec(select(cls).limit(1)).first()

    @classmethod
    def get_last(cls):
        with Session(engine) as session:
            return session.exec(select(cls).order_by(cls.id.desc()).limit(1)).first()

    @classmethod
    def get_random(cls):
        with Session(engine) as session:
            return session.exec(select(cls).order_by(cls.id).limit(1)).first()

    @classmethod
    def get_page(cls, page: int = 1, page_size: int = 20):
        with Session(engine) as session:
            items = session.exec(
                select(cls).offset((page - 1) * page_size).limit(page_size)
            ).all()
            total = cls.get_count()
            # determine if there is a next page
            if page * page_size < total:
                next_page = page + 1
            else:
                next_page = None

            return PagedResult(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                next_page=next_page,
            )

    def delete(self):
        with Session(engine) as session:
            session.delete(self)
            session.commit()
            return self

    def update(self):
        with Session(engine) as session:
            validated = self.model_validate(self)
            session.add(self.sqlmodel_update(validated))
            session.commit()
            session.refresh(self)
            return self


class Hero(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

    @validator("age")
    def validate_age(cls, v):
        if v is None:
            return v
        if v > 0:
            return v
        return abs(v)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)  # , echo=True)


# replace with alembic commands
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson").create()
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador").create()
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48).create()


def page_heroes():
    next_page = 1
    while next_page:
        page = Hero.get_page(page=next_page, page_size=2)
        console.print(page)
        next_page = page.next_page


def main():
    create_db_and_tables()
    create_heroes()
    page_heroes()


if __name__ == "__main__":
    main()
