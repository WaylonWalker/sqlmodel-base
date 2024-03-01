from typing import Optional

from pydantic import validator
from rich.console import Console
from sqlmodel import Field

from sqlmodel_base.base import Base

console = Console()


class Hero(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
