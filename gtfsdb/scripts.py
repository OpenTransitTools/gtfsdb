import click

from gtfsdb.model.db import Database

@click.option('--database', help="The database connection string")
@click.group()
@click.pass_context
def gtfsdb(ctx, database):
    """Simple program that greets NAME for a total of COUNT times."""
    ctx.obj = dict(database=Database(url=database))

@gtfsdb.group()
def index():
    pass

@index.command()
@click.pass_context
def drop(ctx):
    ctx.obj['database'].drop_indexes()

@index.command()
@click.pass_context
def create(ctx):
    ctx.obj['database'].create_indexes()
