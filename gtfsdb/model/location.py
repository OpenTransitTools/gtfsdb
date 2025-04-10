import json

from sqlalchemy import Column, String
from sqlalchemy.orm import deferred

from gtfsdb import config
from gtfsdb.model.base import Base

import logging
log = logging.getLogger(__name__)


class LocationBase(object):
    id = Column(String(255), primary_key=True, index=True, nullable=False)
    region_color = Column(String(7), default=config.default_route_color)
    text_color = Column(String(7), default=config.default_text_color)
    route_id = Column(String(255))
    region_name = Column(String(255))
    region_desc = Column(String(1023))

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            # TODO: the geom could be either a Polygon or Multi-Polygon 
            cls.geom = deferred(Column(Geometry('POLYGON', srid=config.SRID)))


class Location(Base, LocationBase):
    """ GTFS 'location' aka Flex regions """
    datasource = config.DATASOURCE_GTFS
    filename = 'locations.geojson'

    __tablename__ = 'locations'

    @classmethod
    def make_record(cls, row, **kwargs):
        if row.get('geometry') and hasattr(cls, 'geom'):
            row['geom'] = json.dumps(row['geometry'])
        return row

    @classmethod
    def post_process(cls, db, **kwargs):
        """
        fix up and populate the location table:
         - find each location's route_id and other details via stop_times table
         - create a simplified geom for rendering
         - ...
        """
        from gtfsdb.model.stop_time import StopTime

        session = db.session()
        try:
            locs = session.query(Location).all()
            if locs and len(locs) > 0:
                for l in locs:
                    stop_time = session.query(StopTime).filter_by(location_id=l.id).first()
                    if stop_time:
                        #import pdb; pdb.set_trace()
                        l.route_id = stop_time.trip.route.route_id
                        l.region_color = stop_time.trip.route.route_color
                        l.text_color = stop_time.trip.route.route_text_color
                        l.region_name = stop_time.trip.route.route_name
        except Exception as e:
            log.error(e)


class LocationCarto(Base, LocationBase):
    """ a union of GTFS related (via stop_time.location_id) flex regions, that should look good on a map """
    datasource = config.DATASOURCE_DERIVED
    __tablename__ = 'locations_carto'

    @classmethod
    def post_process(cls, db, **kwargs):
        """
        TODO: below query unions all regions for an agency ... need to union by route instead

        drop table if exists sam.flex;
        CREATE TABLE sam.flex AS
        SELECT ST_UnaryUnion(ST_CollectionExtract(unnest(ST_ClusterIntersecting(geom)))) as geom
        FROM sam.locations;
        ALTER TABLE sam.flex ADD COLUMN id BIGSERIAL PRIMARY KEY;
        """
        #import pdb; pdb.set_trace()
        pass
