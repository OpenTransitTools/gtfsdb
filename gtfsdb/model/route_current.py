import datetime
import logging
import time

from gtfsdb import config
from gtfsdb.model.route import Route

import sqlalchemy as db
from sqlalchemy import Column
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Integer, String

log = logging.getLogger(__name__)

__all__ = ['RouteCurrent']


class RouteCurrent(Route):
    datasource = config.DATASOURCE_DERIVED
    __tablename__ = 'routes_current'

    def update_view(self):
        pass



db.Index(RouteCurrent.__name__ + '_index', RouteCurrent.route_id, unique=True)