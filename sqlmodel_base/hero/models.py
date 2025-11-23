from typing import Optional

from pydantic import validator
from rich.console import Console
from sqlmodel import Field

from sqlmodel_base.base import Base

console = Console()


class HeroBase(Base):
    name: str
    secret_name: str
    age: Optional[int] = None
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")

    @validator("age")
    def validate_age(cls, v):
        if v is None:
            return v
        if v > 0:
            return v
        return abs(v)


class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class HeroCreate(HeroBase):
    __table_class__ = Hero
    pass


class HeroRead(HeroBase):
    __table_class__ = Hero
    id: int


class HeroUpdate(Base, table=False):
    __table_class__ = Hero
    name: Optional[str]
    secret_name: Optional[str]
    age: Optional[int]
    team_id: Optional[int]


if __name__ == "__main__":
    Hero.cli()
