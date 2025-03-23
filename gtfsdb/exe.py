from sqlalchemy import text
from gtfsdb import Database
from .scripts import get_args

import logging
log = logging.getLogger(__name__)


def db_post_process():
    """
    written as a test / debug method for RS table loader
    """
    kwargs = get_args()[1]
    db = Database(**kwargs)

    with db.engine.connect() as conn:
        t = text("select * from rideconnection.stops r where st_dwithin(r.geom, (select t.geom from trimet.stops t where stop_id = '35'), 0.0001)")
        result = conn.execute(t).fetchall()
        print(result)
