from typing import Optional

import typer
import uvicorn
from fastapi import APIRouter, FastAPI
from iterfzf import iterfzf
from pydantic import BaseModel
from pydantic_core._pydantic_core import PydanticUndefinedType
from rich.console import Console
from sqlalchemy import func
from sqlmodel import Session, SQLModel, select

from sqlmodel_base.database import get_engine

console = Console()


class PagedResult(BaseModel):
    items: list
    total: int
    page: int
    next_page: Optional[int]
    page_size: int


class Base(SQLModel):
    @classmethod
    @property
    def engine(self):
        engine = get_engine()
        return engine

    def create(self):
        with Session(self.engine) as session:
            validated = self.model_validate(self)
            session.add(self.sqlmodel_update(validated))
            session.commit()
            session.refresh(self)
            return self

    @classmethod
    def interactive_create(cls, id: Optional[int] = None):
        data = {}
        for name, field in cls.__fields__.items():
            default = field.default
            if (
                default is None or isinstance(default, PydanticUndefinedType)
            ) and not field.is_required():
                default = "None"
            if (isinstance(default, PydanticUndefinedType)) and field.is_required():
                default = None
            value = typer.prompt(f"{name}: ", default=default)
            if value and value != "" and value != "None":
                data[name] = value
        item = cls(**data).create()
        console.print(item)

    @classmethod
    def pick(cls):
        all = cls.all()
        item = iterfzf([item.model_dump_json() for item in all])
        if not item:
            console.print("No item selected")
            return
        return cls.get(cls.parse_raw(item).id)

    @classmethod
    def get(cls, id: int):
        with Session(cls.engine) as session:
            return session.get(cls, id)

    @classmethod
    def get_or_pick(cls, id: Optional[int] = None):
        if id is None:
            return cls.pick()
        return cls.get(id=id)

    @classmethod
    def all(cls):
        with Session(cls.engine) as session:
            return session.exec(select(cls)).all()

    @classmethod
    def count(cls):
        with Session(cls.engine) as session:
            return session.exec(func.count(cls.id)).scalar()

    @classmethod
    def first(cls):
        with Session(cls.engine) as session:
            return session.exec(select(cls).limit(1)).first()

    @classmethod
    def last(cls):
        with Session(cls.engine) as session:
            return session.exec(select(cls).order_by(cls.id.desc()).limit(1)).first()

    @classmethod
    def random(cls):
        with Session(cls.engine) as session:
            return session.exec(select(cls).order_by(cls.id).limit(1)).first()

    @classmethod
    def get_page(
        cls,
        page: int = 1,
        page_size: int = 20,
        all: bool = False,
        reverse: bool = False,
    ):
        with Session(cls.engine) as session:
            if all:
                items = session.exec(select(cls)).all()
                page_size = len(items)
            else:
                if reverse:
                    items = session.exec(
                        select(cls)
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                        .order_by(cls.id.desc())
                    ).all()
                else:
                    items = session.exec(
                        select(cls)
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                        .order_by(cls.id)
                    ).all()
                # items = session.exec(
                #     select(cls).offset((page - 1) * page_size).limit(page_size)
                # ).all()

            total = cls.count()
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
        with Session(self.engine) as session:
            session.delete(self)
            session.commit()
            return self

    def update(self):
        with Session(self.engine) as session:
            validated = self.model_validate(self)
            session.add(self.sqlmodel_update(validated))
            session.commit()
            session.refresh(self)
            return self

    @classmethod
    def interactive_update(cls, id: Optional[int] = None):
        item = cls.get_or_pick(id=id)
        if not item:
            console.print("No item selected")
            return
        for field in item.__fields__.keys():
            value = typer.prompt(f"{field}: ", default=getattr(item, field) or "None")
            if (
                value
                and value != ""
                and value != "None"
                and value != getattr(item, field)
            ):
                setattr(item, field, value)
        item.update()
        console.print(item)

    @classmethod
    def api(cls):
        api = FastAPI(
            title="FastAPI",
            version="0.1.0",
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
            # openapi_tags=tags_metadata,
            # dependencies=[Depends(set_user), Depends(set_prefers)],
        )

        api.include_router(cls.router())

        return api

    @classmethod
    def router(cls):
        router = APIRouter()
        router.add_api_route("/get/", cls.get, methods=["GET"])
        router.add_api_route("/list/", cls.all, methods=["GET"])
        router.add_api_route("/create/", cls.interactive_create, methods=["POST"])
        router.add_api_route("/update/", cls.interactive_update, methods=["PUT"])
        return router

    @classmethod
    @property
    def cli(cls):
        app = typer.Typer()

        @app.command()
        def get(id: int = typer.Option(None, help="Hero ID")):
            console.print(cls.get_or_pick(id=id))

        @app.command()
        def create():
            console.print(cls.interactive_create())

        @app.command()
        def list(
            page: int = typer.Option(1, help="Page number"),
            page_size: int = typer.Option(20, help="Page size"),
            all: bool = typer.Option(False, help="Show all heroes"),
            reverse: bool = typer.Option(False, help="Reverse order"),
        ):
            console.print(
                cls.get_page(
                    page=page,
                    page_size=page_size,
                    all=all,
                    reverse=reverse,
                )
            )

        @app.command()
        def api():
            cls.run_api()

        @app.command()
        def update():
            console.print(cls.interactive_update())

        return app

    @classmethod
    def run_api(cls):
        uvicorn.run(cls.api(), host="127.0.0.1", port=8000)
