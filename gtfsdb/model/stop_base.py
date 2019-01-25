from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import joinedload, joinedload_all, object_session, relationship

from gtfsdb import config
from gtfsdb.util import BBox, Point

import logging
log = logging.getLogger(__name__)


class StopBase(object):
    """
    provides a generic set of stop query routines
    """

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            cls.geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    @classmethod
    def query_orm_for_stop(cls, session, stop_id, detailed=False, agency=None):
        """
        simple utility for quering a stop from gtfsdb
        """
        ret_val = None
        try:
            log.info("query Stop for {}".format(stop_id))
            q = session.query(cls)
            q = q.filter(cls.stop_id == stop_id)
            # TODO q.filter(Stop.agency_id == agency_id)
            if detailed:
                q = q.options(joinedload("stop_features"))
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
            q = q.filter(cls.geom.ST_Within(bbox.get_geojson()))
            q = q.limit(limit + 10)
            ret_val = q.all()
        except Exception as e:
            log.warning(e)
        return ret_val

    @classmethod
    def query_stops_via_point(cls, session, point, limit=10, sort=False):
        ret_val = []
        try:
            # import pdb; pdb.set_trace()
            log.info("query Stop table")
            q = session.query(cls)
            q = q.filter(cls.location_type == 0)
            q = q.order_by(cls.geom.distance_centroid(point.get_geojson()))
            q = q.limit(limit)
            ret_val = q.all()
            if sort:
                ret_val = cls.sort_list_by_distance(point, ret_val)
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

    @classmethod
    def sort_list_by_distance(cls, point, stop_list, order=True):
        """
        sort a python list [] by distance, and assign order
        """
        # step 1: calculate distance from a point
        for s in stop_list:
            s.distance = point * 1111.1111

        # step 2: sort the list
        stop_list.sort(key=lambda x: x.distance, reverse=False)

        # step 3: (optionally) append a numeric order
        if order:
            for i, s in enumerate(stop_list):
                s.order = i + 1

        return stop_list
