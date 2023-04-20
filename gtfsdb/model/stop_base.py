from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import joinedload, object_session

from gtfsdb import config
from gtfsdb.util import BBox, Point

import logging
log = logging.getLogger(__name__)


class StopBase(object):
    """
    provides a generic set of stop query routines
    """

    def active_stops(self, date=None):
        """
        this common method will call route.is_active(), which means it will probably be slow
        note: this method, even when called from ActiveRoutes or ActiveStops, will probably be *slow*
        """
        ret_val = []
        try:
            for r in self.routes:
                if r.is_active(date):
                    ret_val.append(r)
        except Exception as e:
            log.warning(e)
        return ret_val

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            cls.geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    @classmethod
    def query_orm_for_stop(cls, session, stop_id, detailed=False, agency=None):
        """
        simple utility for querying a stop from gtfsdb
        """
        ret_val = None
        try:
            log.info("query Stop for {}".format(stop_id))
            q = session.query(cls)
            q = q.filter(cls.stop_id == stop_id)
            # TODO q.filter(cls.agency_id == agency_id)
            if detailed:
                try:
                    q = q.options(joinedload("stop_features"))
                except:
                    pass
            ret_val = q.one()
        except Exception as e:
            log.info(e)
        return ret_val

    @classmethod
    def generic_query_stops(cls, session, **kwargs):
        """
        query for list of this data
        """
        ret_val = []
        try:
            # import pdb; pdb.set_trace()
            clist = session.query(cls)
            limit = kwargs.get('limit')
            if limit:
                clist = clist.limit(limit)
            ret_val = clist.all()
        except Exception as e:
            log.warning(e)
        return ret_val

    @classmethod
    def query_stops_via_bbox(cls, session, bbox, limit=2000):
        ret_val = []
        try:
            log.info("query gtfsdb Stop table")
            q = session.query(cls)
            q = q.filter(cls.location_type == 0)  # just stops (not stations or entrances to stations)
            q = q.filter(cls.geom.ST_Within(bbox.to_geojson()))
            q = q.limit(limit + 10)
            ret_val = q.all()
        except Exception as e:
            log.warning(e)
        return ret_val

    @classmethod
    def query_stops_via_point(cls, session, point, limit=10):
        ret_val = []
        try:
            # import pdb; pdb.set_trace()
            log.info("query Stop table")
            q = session.query(cls)
            q = q.filter(cls.location_type == 0)
            q = q.order_by(cls.geom.distance_centroid(point.to_geojson()))
            q = q.limit(limit)
            ret_val = q.all()
        except Exception as e:
            log.warning(e)
        return ret_val

    @classmethod
    def query_stops(cls, session, **kwargs):
        """
        will query the db for a stop, either via bbox, point & distance or just an id
        :return list of stops
        """
        ret_val = []
        # import pdb; pdb.set_trace()
        if kwargs.get('lat') or kwargs.get('min_lat'):
            bbox = BBox(**kwargs)
            if bbox.is_valid:
                ret_val = cls.query_stops_via_bbox(session, bbox)
            else:
                point = Point(**kwargs)
                if point.is_valid:
                    ret_val = cls.query_stops_via_point_radius(session, point)
        else:
            ret_val = cls.generic_query_stops(session, **kwargs)
        return ret_val
