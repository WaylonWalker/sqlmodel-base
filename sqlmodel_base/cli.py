import typer

from sqlmodel_base.hero.cli import hero_app

app = typer.Typer()

app.add_typer(hero_app, name="hero")


if __name__ == "__main__":
    app()
