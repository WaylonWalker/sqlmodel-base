from rich.console import Console

from sqlmodel_base.database import get_engine
from sqlmodel_base.hero.models import Hero

engine = get_engine()

hero_app = Hero.cli
console = Console()
# @hero_app.callback()
# def hero():
#     "model cli"


# @hero_app.command()
# def get(id: int = typer.Option(None, help="Hero ID")):
#     console.print(Hero.get_or_pick(id=id))


# @hero_app.command()
# def list(
#     page: int = typer.Option(1, help="Page number"),
#     page_size: int = typer.Option(20, help="Page size"),
#     all: bool = typer.Option(False, help="Show all heroes"),
#     reverse: bool = typer.Option(False, help="Reverse order"),
# ):
#     console.print(
#         Hero.get_page(page=page, page_size=page_size, all=all, reverse=reverse)
#     )


# @hero_app.command()
# def create(
#     name: str = typer.Option(..., help="Hero name", prompt=True),
#     secret_name: str = typer.Option(..., help="Hero secret name", prompt=True),
#     age: int = typer.Option(None, help="Hero age", prompt=True),
# ):
#     hero = Hero(
#         name=name,
#         secret_name=secret_name,
#         age=age,
#     ).create()
#     console.print(hero)


# @hero_app.command()
# def update(
#     id: int = typer.Option(None, help="Hero ID"),
#     name: str = typer.Option(None, help="Hero name"),
#     secret_name: str = typer.Option(None, help="Hero secret name"),
#     age: int = typer.Option(None, help="Hero age"),
# ):
#     hero = Hero.interactive_update(id=id)
#     console.print(hero)


# @hero_app.command()
# def create_heroes():
#     team_1 = Team.get(id=1)
#     if not team_1:
#         team_1 = Team(name="Team 1", headquarters="Headquarters 1").create()
#     for _ in range(50):
#         Hero(name="Deadpond", secret_name="Dive Wilson", team_id=team_1.id).create()
#         Hero(name="Spider-Boy", secret_name="Pedro Parqueador").create()
#         Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48).create()
