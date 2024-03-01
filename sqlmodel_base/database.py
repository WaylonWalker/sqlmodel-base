from functools import lru_cache

from sqlmodel import Session, SQLModel, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"


@lru_cache
def get_engine():

    engine = create_engine(sqlite_url)
    SQLModel.metadata.create_all(engine)
    return engine


def get_session():
    with Session(get_engine()) as session:
        yield session
