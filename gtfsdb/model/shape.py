from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Numeric, String

from gtfsdb import config, util
from gtfsdb.model.base import Base

import logging
log = logging.getLogger(__name__)


__all__ = ['Shape']


class Shape(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'shapes.txt'

    __tablename__ = 'shapes'

    shape_id = Column(String(255), primary_key=True, index=True)
    shape_pt_lat = Column(Numeric(12, 9))
    shape_pt_lon = Column(Numeric(12, 9))
    shape_pt_sequence = Column(Integer, primary_key=True, index=True)
    shape_dist_traveled = Column(Numeric(20, 10))

    @classmethod
    def get_sequence_from_dist(cls, dist, shapes, find_nearest=True, max_nearest=111.111, def_val=-1):
        """
        find the sequence based on
        """
        ret_val = None
        nearest_seq = def_val
        nearest_dist = max_nearest

        # loop thru shape points
        for s in shapes:
            # exact hit will stop the loop
            if dist == s.shape_dist_traveled:
                ret_val = s.shape_pt_sequence
                break
            # a fuzzy nearest is also an option
            if find_nearest:
                d = abs(dist - s.shape_dist_traveled)
                if d < nearest_dist:
                    nearest_dist = d
                    nearest_seq = s.shape_pt_sequence

        # assignment rules below kick in when no exact matches happens above
        if ret_val is None:
            ret_val = def_val
            if find_nearest:
                ret_val = nearest_seq

        return ret_val

    @classmethod
    def get_sequence_from_coord(cls, lat, lon, shapes, def_val=-1):
        """
        find the sequence based on lat / lon coordinate
        """
        ret_val = def_val
        for s in shapes:
            # exact hit will stop the loop
            if lat == float(s.shape_pt_lat) and lon == float(s.shape_pt_lon):
                ret_val = s.shape_pt_sequence
                break
        return ret_val

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    @classmethod
    def add_geom_to_dict(cls, row):
        args = (config.SRID, row['shape_pt_lon'], row['shape_pt_lat'])
        row['geom'] = 'SRID={0};POINT({1} {2})'.format(*args)

    @classmethod
    def post_process(cls, db, **kwargs):
        """
        routines to run after db is loaded
        """
        log.debug('{0}.post_process'.format(cls.__name__))
        cls.populate_shape_dist_traveled(db)

    @classmethod
    def populate_shape_dist_traveled(cls, db):
        """
        populate Shape.shape_pt_sequence where ever it is missing
        TODO: assumes feet as the measure ... should make this configurable
        """
        session = db.session()
        try:
            shapes = session.query(Shape).order_by(Shape.shape_id, Shape.shape_pt_sequence).all()
            if shapes:
                shape_id = "-111"
                prev_lat = prev_lon = None
                distance = 0.0
                count = 0
                for s in shapes:
                    # step 1: on first iteration or shape change, goto loop again (e.g., need 2 coords to calc distance)
                    if prev_lat is None or shape_id != s.shape_id:
                        prev_lat = s.shape_pt_lat
                        prev_lon = s.shape_pt_lon
                        shape_id = s.shape_id
                        distance = s.shape_dist_traveled = 0.0
                        continue

                    # step 2: now that we have 2 coords, we can (if missing) calculate the travel distannce
                    # import pdb; pdb.set_trace()
                    if s.shape_dist_traveled is None:
                        msg = "calc dist {}: {},{} to {},{}".format(s.shape_pt_sequence, prev_lat, prev_lon, s.shape_pt_lat, s.shape_pt_lon)
                        #log.debug(msg)
                        distance += util.distance_ft(prev_lat, prev_lon, s.shape_pt_lat, s.shape_pt_lon)
                        s.shape_dist_traveled = distance
                        count += 1

                    # step 3 save off these coords (and distance) for next iteration
                    prev_lat = s.shape_pt_lat
                    prev_lon = s.shape_pt_lon
                    distance = s.shape_dist_traveled

                    # step 4 persist every now and then not to build a big buffer
                    if count >= 10000:
                        session.commit()
                        session.flush()
                        count = 0

        except Exception as e:
            log.warning(e)
            session.rollback()
        finally:
            session.commit()
            session.flush()
            session.close()
