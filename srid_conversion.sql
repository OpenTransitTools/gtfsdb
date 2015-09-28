drop index if EXISTS gtfs_shapes_geom_gem;
drop index if EXISTS gtfs_shapes_gem;
drop index if EXISTS gtfs_stops_gem;

ANALYZE;

alter table gtfs_shapes ALTER COLUMN the_geom type geometry(Point, 900913) using ST_Transform(ST_SetSRID(the_geom,4326),900913);
alter table gtfs_stops ALTER COLUMN the_geom type geometry(Point, 900913) using ST_Transform(ST_SetSRID(the_geom,4326),900913);
alter table gtfs_shape_geoms ALTER COLUMN the_geom type geometry(LineString, 900913) using ST_Transform(ST_SetSRID(the_geom,4326),900913);

create index gtfs_shapes_geom_gem  on gtfs_shape_geoms using GIST (the_geom);
create index gtfs_shapes_gem  on gtfs_shapes using GIST (the_geom);
create index gtfs_stops_gem  on gtfs_stops using GIST (the_geom);

ANALYZE;