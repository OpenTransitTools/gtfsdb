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
        will update the current 'view' of this data
        """
        log.info("Shape.post_process")
        session = db.session()
        try:
            shapes = session.query(Shape).order_by(Shape.shape_id, Shape.shape_pt_sequence).all()
            if shapes:
                shape_id = "-111"
                prev_lat = prev_lon = None
                distance = 0.0
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
                        log.debug(msg)
                        distance += util.distance_ft(prev_lat, prev_lon, s.shape_pt_lat, s.shape_pt_lon)
                        s.shape_dist_traveled = distance

                    # step 3 save off these coords (and distance) for next iteration
                    prev_lat = s.shape_pt_lat
                    prev_lon = s.shape_pt_lon
                    distance = s.shape_dist_traveled
        except Exception as e:
            log.warning(e)
            session.rollback()
        finally:
            session.commit()
            session.flush()
            session.close()
