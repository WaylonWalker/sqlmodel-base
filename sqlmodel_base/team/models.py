from typing import Optional

from rich.console import Console
from sqlmodel import Field

from sqlmodel_base.base import Base


class Team(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
