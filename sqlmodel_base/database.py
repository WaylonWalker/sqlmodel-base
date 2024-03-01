from functools import lru_cache

from sqlmodel import Field, Session, SQLModel, create_engine, select

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"


@lru_cache
def get_engine():
    from sqlmodel_base.hero.models import Hero
    from sqlmodel_base.team.models import Team

    engine = create_engine(sqlite_url)
    SQLModel.metadata.create_all(engine)
    return engine


def get_session():
    with Session(get_engine()) as session:
        yield session
