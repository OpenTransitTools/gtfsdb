import click
import json
import os.path
import sys

from joblib import Parallel, delayed
from sqlalchemy.orm.exc import NoResultFound

from gtfsdb.model.db import Database
from gtfsdb.model.metaTracking import FeedFile
from gtfsdb.api import create_shapes_geoms, get_gtfs_feeds, database_load_versioned
from gtfsdb.config import DEFAULT_CONFIG_FILE


@click.option('--database', help="The database connection string")
@click.group()
@click.pass_context
def gtfsdb_main(ctx, database):
    """Simple program that greets NAME for a total of COUNT times."""
    ctx.obj = dict()
    if not database and os.path.exists(DEFAULT_CONFIG_FILE):
        conf = json.load(open(DEFAULT_CONFIG_FILE, 'r'))
        database = conf['database']
        ctx.obj.update(dict(conf=conf))
    else:
        click.echo("No database selected!!")
        sys.exit(1)
    ctx.obj.update(dict(database=Database(url=database), db_url=database))


@gtfsdb_main.command('create-geometry')
@click.pass_context
def create_geom(ctx):
    create_shapes_geoms(ctx.obj['db_url'])


@gtfsdb_main.command('drop-index')
@click.pass_context
def drop_index(ctx):
    ctx.obj['database'].drop_indexes()


@gtfsdb_main.command('create-index')
@click.pass_context
def create(ctx):
    ctx.obj['database'].create_indexes()

@gtfsdb_main.command('load-ex-feeds')
@click.option('-p', '--parallel', default=1, help='Number of worker processes')
@click.argument('feeds', nargs=-1)
@click.pass_context
def load_gtfs_ex(ctx, feeds, parallel):
    db = ctx.obj['database']
    feeds = set(get_gtfs_feeds(db.get_session(), feeds))
    click.echo("Ready to load {} feeds".format(len(feeds)))
    load_feeds(feeds, db, parallel)

@gtfsdb_main.command('delete-feed-file')
@click.argument('file_id', nargs=1)
@click.pass_context
def delete_feed_file(ctx, file_id):
    session = ctx.obj['database'].get_session()
    try:
        feed_file = session.query(FeedFile).get(file_id)
    except NoResultFound:
        click.echo("Could not find file with id: {}".format(file_id))
        sys.exit(1)
    name = feed_file.filename
    click.echo("found feed file: {} ({})".format(name, file_id))
    agencies = session.query()
    session.delete(feed_file)
    session.commit()
    session.close()
    click.echo("sucessfully deleted feed file: {} ({})".format(name, file_id))

def load_feeds(feeds, database, parallel=0):
    database.create()
    database.drop_indexes()
    if parallel:
        concurrent_run(feeds, database.url, parallel)
    else:
        serial_run(feeds, database.url)


def serial_run(sources, database):
    for source in sources:
        database_load_versioned(db_url=database, feed_file=source)


def concurrent_run(sources, database, num_jobs):
    Parallel(n_jobs=int(num_jobs))(delayed(database_load_versioned)(db_url=database, feed_file=source) for source in sources)
