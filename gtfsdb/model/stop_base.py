import datetime
from collections import defaultdict

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import joinedload, joinedload_all, object_session, relationship

from gtfsdb.util import BBox
from gtfsdb.util import Point

import logging
log = logging.getLogger(__name__)


class StopBase(object):
    """ provides a generic set of stop query routines """

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
    def query_stops_via_bbox(cls, session, **kwargs):
        ret_val = []
        return ret_val

    @classmethod
    def query_stops_via_point_radius(cls, session, **kwargs):
        ret_val = []
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
                ret_val = cls.query_stops_via_bbox(session, **kwargs)
            else:
                point = Point(**kwargs)
                if point.is_valid:
                    ret_val = cls.query_stops_via_point_radius(session, **kwargs)
        else:
            ret_val = cls.generic_query_stops(session, **kwargs)
        return ret_val


class StopQuery(object):

    @classmethod
    def query_bbox_stops(cls, session, geojson_bbox, limit=1000, is_active=True):
        """
        query gtfsdb for as-the-crow-flies nearest stops ... not accurate around barriers like rivers, highways, etc...
        :params db session, POINT(x,y), limit=10:
        """
        # import pdb; pdb.set_trace()

        # step 1: query database via geo routines for stops within
        #         note we grab 10 extra in the /Q, because some stops might not be active (no routes)
        #         thus we filter them below
        log.info("query gtfsdb Stop table")
        q = session.query(cls)
        q = q.filter(cls.location_type == 0)  # just stops (not stations or entrances to stations)
        q = q.filter(Stop.geom.ST_Within(geojson_bbox))
        q = q.limit(limit)
        stop_list = q.all()

        # step 2: filter stops
        ret_val = []
        for s in stop_list:
            # step 2a: filter stops w/out any routes assigned (stop should have active routes)
            if is_active and len(s.routes) < 1:
                continue

            # step 2b: stop if we have enough stops to return
            if len(ret_val) >= limit:
                break

            # step 2c: passed all filters, so add to our return list
            ret_val.append(s)

        return ret_val


class StopQueryX(object):

    @classmethod
    def query_nearest_stops(cls, session, geojson_point, radius=None, limit=10, is_active=True):
        """
        query gtfsdb for as-the-crow-flies nearest stops ... not accurate around barriers like rivers, highways, etc...
        :params db session, POINT(x,y), limit=10:
        """
        # import pdb; pdb.set_trace()

        # step 1: query database via geo routines for N of stops cloesst to the POINT
        #         note we grab 10 extra in the /Q, because some stops might not be active (no routes)
        #         thus we filter them below
        log.info("query gtfsdb Stop table")
        q = session.query(Stop)
        q = q.filter(Stop.location_type == 0)  # just stops (not stations or entrances to stations)
        # if radius and float(radius):
        #     q = q.filter-by distance todo: either here or below?
        q = q.order_by(Stop.geom.distance_centroid(geojson_point))
        q = q.limit(limit + 10)
        stop_list = q.all()

        # step 2: filter stops
        distance_filtered = False
        ret_val = []
        for s in stop_list:
            # step 2a: filter stops w/out any routes assigned (stop should have active routes)
            if is_active and len(s.routes) < 1:
                continue

            # step 2b: stop if we have enough stops to return
            if len(ret_val) >= limit:
                break

            # step 2c: radius / distance filter
            # todo: this not working right now (note len routes is filter above)
            # todo: should this be part of query see above
            if radius and len(s.routes) < 1:
                distance_filtered = True
                continue

            # step 2d: passed all filters, so add to our return list
            ret_val.append(s)

        # step 3: cleanup ... if we didn't get enough stops, maybe add some (non-active) stops back
        if not distance_filtered and len(ret_val) < limit:
            cls._add_back_stops(cls, stop_list, ret_val)

        return ret_val



    @classmethod
    def _add_back_stops(cls, all_stop_list, filtered_list, limit=7):
        for s in all_stop_list:
            if len(filtered_list) >= limit:
                break

            if s not in filtered_list:
                filtered_list.append(s)

    @classmethod
    def nearest_stops(cls, session, geo_params):
        """ make a StopListDao based on a route_stops object
            @params: lon, lat, limit=10, name=None, agency="TODO", detailed=False):
        """
        # import pdb; pdb.set_trace()

        # step 1: make POINT(x,y) / get desired limit number of stops
        point = geo_params.to_point_srid()
        limit = int(geo_params.limit)

        # TODO replace step 2 with this below.... really, replace this with otp_client_py nearest stops
        # step 2: query for N of stops cloesst to the POINT
        # stops = cls.query_otp_nearest_stops(point, limit)

        # step 2: query database via geo routines for N of stops cloesst to the POINT
        #         note we grab 10 extra in the /Q, because some stops might not be active (no routes), thus we filter them below
        log.info("query Stop table")
        q = session.query(Stop)
        q = q.filter(Stop.location_type == 0)
        q = q.order_by(Stop.geom.distance_centroid(point))
        q = q.limit(limit + 10)
        stops_list = q

        # step 3a: loop thru nearest N stops
        stops = []
        for s in stops_list:
            # todo remove steps 3a and 3d ... see above
            # step 3a: make sure this stop has routes assigned
            if len(s.routes) < 1:
                continue

            # step 3b: calculate distance
            dist = num_utils.distance_mi(s.stop_lat, s.stop_lon, geo_params.lat, geo_params.lon)

            # step 3c: make stop...plus add stop route short name
            stop = StopDao.from_stop_orm(stop_orm=s, distance=dist, agency=geo_params.agency, detailed=geo_params.detailed)
            stop.get_route_short_names(stop_orm=s)
            stops.append(stop)

            # step 3d: stop if we have enough stops to return
            if len(stops) >= limit:
                break

        # step 4: sort list then return
        stops = cls.sort_list_by_distance(stops)
        ret_val = StopListDao(stops, name=geo_params.name)
        return ret_val

    @classmethod
    def sort_list_by_distance(cls, stop_list, order=True):
        """ sort a python list [] by distance, and assign order
        """

        # step 1: sort the list
        stop_list.sort(key=lambda x: x.distance, reverse=False)

        # step 2: assign order
        if order:
            for i, s in enumerate(stop_list):
                s.order = i+1

        return stop_list
