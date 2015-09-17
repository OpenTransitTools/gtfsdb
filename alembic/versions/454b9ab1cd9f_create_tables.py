"""Create Tables

Revision ID: 454b9ab1cd9f
Revises: 1cbb6c31e044
Create Date: 2015-09-17 14:29:14.483909

"""

# revision identifiers, used by Alembic.
revision = '454b9ab1cd9f'
down_revision = '1cbb6c31e044'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.create_table('gtfs_agency',
    sa.Column('id', sa.Integer(), nullable=True),
    sa.Column('agency_id', sa.String(length=255), nullable=False),
    sa.Column('agency_name', sa.String(length=255), nullable=False),
    sa.Column('agency_url', sa.String(length=255), nullable=False),
    sa.Column('agency_timezone', sa.String(length=50), nullable=False),
    sa.Column('agency_lang', sa.String(length=10), nullable=True),
    sa.Column('agency_phone', sa.String(length=50), nullable=True),
    sa.Column('agency_fare_url', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gtfs_agency_agency_id'), 'gtfs_agency', ['agency_id'], unique=True)
    op.create_table('gtfs_calendar',
    sa.Column('service_id', sa.String(length=255), nullable=False),
    sa.Column('monday', sa.Boolean(), nullable=False),
    sa.Column('tuesday', sa.Boolean(), nullable=False),
    sa.Column('wednesday', sa.Boolean(), nullable=False),
    sa.Column('thursday', sa.Boolean(), nullable=False),
    sa.Column('friday', sa.Boolean(), nullable=False),
    sa.Column('saturday', sa.Boolean(), nullable=False),
    sa.Column('sunday', sa.Boolean(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('service_id')
    )
    op.create_index('calendar_ix1', 'gtfs_calendar', ['start_date', 'end_date'], unique=False)
    op.create_index(op.f('ix_gtfs_calendar_service_id'), 'gtfs_calendar', ['service_id'], unique=False)
    op.create_table('gtfs_calendar_dates',
    sa.Column('service_id', sa.String(length=255), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('exception_type', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('service_id', 'date')
    )
    op.create_index(op.f('ix_gtfs_calendar_dates_date'), 'gtfs_calendar_dates', ['date'], unique=False)
    op.create_index(op.f('ix_gtfs_calendar_dates_service_id'), 'gtfs_calendar_dates', ['service_id'], unique=False)
    op.create_table('gtfs_directions',
    sa.Column('route_id', sa.String(length=255), nullable=False),
    sa.Column('direction_id', sa.Integer(), nullable=False),
    sa.Column('direction_name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('route_id', 'direction_id')
    )
    op.create_index(op.f('ix_gtfs_directions_direction_id'), 'gtfs_directions', ['direction_id'], unique=False)
    op.create_index(op.f('ix_gtfs_directions_route_id'), 'gtfs_directions', ['route_id'], unique=False)
    op.create_table('gtfs_fare_attributes',
    sa.Column('fare_id', sa.String(length=255), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('currency_type', sa.String(length=255), nullable=False),
    sa.Column('payment_method', sa.Integer(), nullable=False),
    sa.Column('transfers', sa.Integer(), nullable=True),
    sa.Column('transfer_duration', sa.Integer(), nullable=True),
    sa.Column('agency_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('fare_id')
    )
    op.create_table('gtfs_fare_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fare_id', sa.String(length=255), nullable=False),
    sa.Column('route_id', sa.String(length=255), nullable=True),
    sa.Column('origin_id', sa.String(length=255), nullable=True),
    sa.Column('destination_id', sa.String(length=255), nullable=True),
    sa.Column('contains_id', sa.String(length=255), nullable=True),
    sa.Column('service_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gtfs_fare_rules_fare_id'), 'gtfs_fare_rules', ['fare_id'], unique=False)
    op.create_table('gtfs_feed_info',
    sa.Column('feed_publisher_name', sa.String(length=255), nullable=False),
    sa.Column('feed_publisher_url', sa.String(length=255), nullable=False),
    sa.Column('feed_lang', sa.String(length=255), nullable=False),
    sa.Column('feed_start_date', sa.Date(), nullable=True),
    sa.Column('feed_end_date', sa.Date(), nullable=True),
    sa.Column('feed_version', sa.String(length=255), nullable=True),
    sa.Column('feed_license', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('feed_publisher_name')
    )
    op.create_table('gtfs_frequencies',
    sa.Column('trip_id', sa.String(length=255), nullable=False),
    sa.Column('start_time', sa.String(length=8), nullable=False),
    sa.Column('end_time', sa.String(length=8), nullable=True),
    sa.Column('headway_secs', sa.Integer(), nullable=True),
    sa.Column('exact_times', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('trip_id', 'start_time')
    )
    op.create_table('gtfs_route_type',
    sa.Column('route_type', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('route_type_name', sa.String(length=255), nullable=True),
    sa.Column('route_type_desc', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('route_type')
    )
    op.create_index(op.f('ix_gtfs_route_type_route_type'), 'gtfs_route_type', ['route_type'], unique=False)
    op.create_table('gtfs_routes',
    sa.Column('route_id', sa.String(length=255), nullable=False),
    sa.Column('agency_id', sa.String(length=255), nullable=True),
    sa.Column('route_short_name', sa.String(length=255), nullable=True),
    sa.Column('route_long_name', sa.String(length=255), nullable=True),
    sa.Column('route_desc', sa.String(length=255), nullable=True),
    sa.Column('route_type', sa.Integer(), nullable=False),
    sa.Column('route_url', sa.String(length=255), nullable=True),
    sa.Column('route_color', sa.String(length=6), nullable=True),
    sa.Column('route_text_color', sa.String(length=6), nullable=True),
    sa.Column('route_sort_order', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('route_id')
    )
    op.create_index(op.f('ix_gtfs_routes_agency_id'), 'gtfs_routes', ['agency_id'], unique=False)
    op.create_index(op.f('ix_gtfs_routes_route_id'), 'gtfs_routes', ['route_id'], unique=False)
    op.create_index(op.f('ix_gtfs_routes_route_sort_order'), 'gtfs_routes', ['route_sort_order'], unique=False)
    op.create_index(op.f('ix_gtfs_routes_route_type'), 'gtfs_routes', ['route_type'], unique=False)
    op.create_table('gtfs_shape_geoms',
    sa.Column('shape_id', sa.String(length=255), nullable=False),
    sa.Column('the_geom', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=900913), nullable=True),
    sa.PrimaryKeyConstraint('shape_id')
    )
    op.create_index(op.f('ix_gtfs_shape_geoms_shape_id'), 'gtfs_shape_geoms', ['shape_id'], unique=False)
    op.create_table('gtfs_shapes',
    sa.Column('shape_id', sa.String(length=255), nullable=False),
    sa.Column('shape_pt_lat', sa.Numeric(precision=12, scale=9), nullable=True),
    sa.Column('shape_pt_lon', sa.Numeric(precision=12, scale=9), nullable=True),
    sa.Column('shape_pt_sequence', sa.Integer(), nullable=False),
    sa.Column('shape_dist_traveled', sa.Numeric(precision=20, scale=10), nullable=True),
    sa.PrimaryKeyConstraint('shape_id', 'shape_pt_sequence')
    )
    op.create_index(op.f('ix_gtfs_shapes_shape_id'), 'gtfs_shapes', ['shape_id'], unique=False)
    op.create_index(op.f('ix_gtfs_shapes_shape_pt_sequence'), 'gtfs_shapes', ['shape_pt_sequence'], unique=False)
    op.create_table('gtfs_stop_times',
    sa.Column('trip_id', sa.String(length=255), nullable=False),
    sa.Column('arrival_time', sa.String(length=8), nullable=True),
    sa.Column('departure_time', sa.String(length=8), nullable=True),
    sa.Column('stop_id', sa.String(length=255), nullable=False),
    sa.Column('stop_sequence', sa.Integer(), nullable=False),
    sa.Column('stop_headsign', sa.String(length=255), nullable=True),
    sa.Column('pickup_type', sa.Integer(), nullable=True),
    sa.Column('drop_off_type', sa.Integer(), nullable=True),
    sa.Column('shape_dist_traveled', sa.Numeric(precision=20, scale=10), nullable=True),
    sa.Column('timepoint', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('trip_id', 'stop_sequence')
    )
    op.create_index(op.f('ix_gtfs_stop_times_departure_time'), 'gtfs_stop_times', ['departure_time'], unique=False)
    op.create_index(op.f('ix_gtfs_stop_times_stop_id'), 'gtfs_stop_times', ['stop_id'], unique=False)
    op.create_index(op.f('ix_gtfs_stop_times_timepoint'), 'gtfs_stop_times', ['timepoint'], unique=False)
    op.create_index(op.f('ix_gtfs_stop_times_trip_id'), 'gtfs_stop_times', ['trip_id'], unique=False)
    op.create_table('gtfs_stops',
    sa.Column('stop_id', sa.String(length=255), nullable=False),
    sa.Column('stop_code', sa.String(length=50), nullable=True),
    sa.Column('stop_name', sa.String(length=255), nullable=False),
    sa.Column('stop_desc', sa.String(length=255), nullable=True),
    sa.Column('stop_lat', sa.Numeric(precision=12, scale=9), nullable=False),
    sa.Column('stop_lon', sa.Numeric(precision=12, scale=9), nullable=False),
    sa.Column('zone_id', sa.String(length=50), nullable=True),
    sa.Column('stop_url', sa.String(length=255), nullable=True),
    sa.Column('location_type', sa.Integer(), nullable=True),
    sa.Column('parent_station', sa.String(length=255), nullable=True),
    sa.Column('stop_timezone', sa.String(length=50), nullable=True),
    sa.Column('wheelchair_boarding', sa.Integer(), nullable=True),
    sa.Column('platform_code', sa.String(length=50), nullable=True),
    sa.Column('direction', sa.String(length=50), nullable=True),
    sa.Column('position', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('stop_id')
    )
    op.create_index(op.f('ix_gtfs_stops_location_type'), 'gtfs_stops', ['location_type'], unique=False)
    op.create_index(op.f('ix_gtfs_stops_stop_id'), 'gtfs_stops', ['stop_id'], unique=False)
    op.create_table('gtfs_transfers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_stop_id', sa.String(length=255), nullable=True),
    sa.Column('to_stop_id', sa.String(length=255), nullable=True),
    sa.Column('transfer_type', sa.Integer(), nullable=True),
    sa.Column('min_transfer_time', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gtfs_transfers_transfer_type'), 'gtfs_transfers', ['transfer_type'], unique=False)
    op.create_table('gtfs_trips',
    sa.Column('route_id', sa.String(length=255), nullable=False),
    sa.Column('service_id', sa.String(length=255), nullable=False),
    sa.Column('trip_id', sa.String(length=255), nullable=False),
    sa.Column('trip_headsign', sa.String(length=255), nullable=True),
    sa.Column('trip_short_name', sa.String(length=255), nullable=True),
    sa.Column('direction_id', sa.Integer(), nullable=True),
    sa.Column('block_id', sa.String(length=255), nullable=True),
    sa.Column('shape_id', sa.String(length=255), nullable=True),
    sa.Column('trip_type', sa.String(length=255), nullable=True),
    sa.Column('bikes_allowed', sa.Integer(), nullable=True),
    sa.Column('wheelchair_accessible', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('trip_id')
    )
    op.create_index(op.f('ix_gtfs_trips_route_id'), 'gtfs_trips', ['route_id'], unique=False)
    op.create_index(op.f('ix_gtfs_trips_service_id'), 'gtfs_trips', ['service_id'], unique=False)
    op.create_index(op.f('ix_gtfs_trips_shape_id'), 'gtfs_trips', ['shape_id'], unique=False)
    op.create_index(op.f('ix_gtfs_trips_trip_id'), 'gtfs_trips', ['trip_id'], unique=False)
    op.create_table('route_filters',
    sa.Column('route_id', sa.String(length=255), nullable=False),
    sa.Column('agency_id', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('route_id')
    )
    op.create_index(op.f('ix_route_filters_agency_id'), 'route_filters', ['agency_id'], unique=False)
    op.create_index(op.f('ix_route_filters_route_id'), 'route_filters', ['route_id'], unique=False)
    op.create_table('route_stops',
    sa.Column('route_id', sa.String(length=255), nullable=False),
    sa.Column('direction_id', sa.Integer(), nullable=False),
    sa.Column('stop_id', sa.String(length=255), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('route_id', 'direction_id', 'stop_id')
    )
    op.create_index(op.f('ix_route_stops_direction_id'), 'route_stops', ['direction_id'], unique=False)
    op.create_index(op.f('ix_route_stops_order'), 'route_stops', ['order'], unique=False)
    op.create_index(op.f('ix_route_stops_route_id'), 'route_stops', ['route_id'], unique=False)
    op.create_index(op.f('ix_route_stops_stop_id'), 'route_stops', ['stop_id'], unique=False)
    op.create_table('stop_features',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stop_id', sa.String(length=255), nullable=False),
    sa.Column('feature_type', sa.String(length=50), nullable=False),
    sa.Column('feature_name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stop_features_feature_type'), 'stop_features', ['feature_type'], unique=False)
    op.create_index(op.f('ix_stop_features_stop_id'), 'stop_features', ['stop_id'], unique=False)
    op.create_table('universal_calendar',
    sa.Column('service_id', sa.String(length=255), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('service_id', 'date')
    )
    op.create_index(op.f('ix_universal_calendar_date'), 'universal_calendar', ['date'], unique=False)
    op.create_index(op.f('ix_universal_calendar_service_id'), 'universal_calendar', ['service_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_universal_calendar_service_id'), table_name='universal_calendar')
    op.drop_index(op.f('ix_universal_calendar_date'), table_name='universal_calendar')
    op.drop_table('universal_calendar')
    op.drop_index(op.f('ix_stop_features_stop_id'), table_name='stop_features')
    op.drop_index(op.f('ix_stop_features_feature_type'), table_name='stop_features')
    op.drop_table('stop_features')
    op.drop_index(op.f('ix_route_stops_stop_id'), table_name='route_stops')
    op.drop_index(op.f('ix_route_stops_route_id'), table_name='route_stops')
    op.drop_index(op.f('ix_route_stops_order'), table_name='route_stops')
    op.drop_index(op.f('ix_route_stops_direction_id'), table_name='route_stops')
    op.drop_table('route_stops')
    op.drop_index(op.f('ix_route_filters_route_id'), table_name='route_filters')
    op.drop_index(op.f('ix_route_filters_agency_id'), table_name='route_filters')
    op.drop_table('route_filters')
    op.drop_index(op.f('ix_gtfs_trips_trip_id'), table_name='gtfs_trips')
    op.drop_index(op.f('ix_gtfs_trips_shape_id'), table_name='gtfs_trips')
    op.drop_index(op.f('ix_gtfs_trips_service_id'), table_name='gtfs_trips')
    op.drop_index(op.f('ix_gtfs_trips_route_id'), table_name='gtfs_trips')
    op.drop_table('gtfs_trips')
    op.drop_index(op.f('ix_gtfs_transfers_transfer_type'), table_name='gtfs_transfers')
    op.drop_table('gtfs_transfers')
    op.drop_index(op.f('ix_gtfs_stops_stop_id'), table_name='gtfs_stops')
    op.drop_index(op.f('ix_gtfs_stops_location_type'), table_name='gtfs_stops')
    op.drop_table('gtfs_stops')
    op.drop_index(op.f('ix_gtfs_stop_times_trip_id'), table_name='gtfs_stop_times')
    op.drop_index(op.f('ix_gtfs_stop_times_timepoint'), table_name='gtfs_stop_times')
    op.drop_index(op.f('ix_gtfs_stop_times_stop_id'), table_name='gtfs_stop_times')
    op.drop_index(op.f('ix_gtfs_stop_times_departure_time'), table_name='gtfs_stop_times')
    op.drop_table('gtfs_stop_times')
    op.drop_index(op.f('ix_gtfs_shapes_shape_pt_sequence'), table_name='gtfs_shapes')
    op.drop_index(op.f('ix_gtfs_shapes_shape_id'), table_name='gtfs_shapes')
    op.drop_table('gtfs_shapes')
    op.drop_index(op.f('ix_gtfs_shape_geoms_shape_id'), table_name='gtfs_shape_geoms')
    op.drop_table('gtfs_shape_geoms')
    op.drop_index(op.f('ix_gtfs_routes_route_type'), table_name='gtfs_routes')
    op.drop_index(op.f('ix_gtfs_routes_route_sort_order'), table_name='gtfs_routes')
    op.drop_index(op.f('ix_gtfs_routes_route_id'), table_name='gtfs_routes')
    op.drop_index(op.f('ix_gtfs_routes_agency_id'), table_name='gtfs_routes')
    op.drop_table('gtfs_routes')
    op.drop_index(op.f('ix_gtfs_route_type_route_type'), table_name='gtfs_route_type')
    op.drop_table('gtfs_route_type')
    op.drop_table('gtfs_frequencies')
    op.drop_table('gtfs_feed_info')
    op.drop_index(op.f('ix_gtfs_fare_rules_fare_id'), table_name='gtfs_fare_rules')
    op.drop_table('gtfs_fare_rules')
    op.drop_table('gtfs_fare_attributes')
    op.drop_index(op.f('ix_gtfs_directions_route_id'), table_name='gtfs_directions')
    op.drop_index(op.f('ix_gtfs_directions_direction_id'), table_name='gtfs_directions')
    op.drop_table('gtfs_directions')
    op.drop_index(op.f('ix_gtfs_calendar_dates_service_id'), table_name='gtfs_calendar_dates')
    op.drop_index(op.f('ix_gtfs_calendar_dates_date'), table_name='gtfs_calendar_dates')
    op.drop_table('gtfs_calendar_dates')
    op.drop_index(op.f('ix_gtfs_calendar_service_id'), table_name='gtfs_calendar')
    op.drop_index('calendar_ix1', table_name='gtfs_calendar')
    op.drop_table('gtfs_calendar')
    op.drop_index(op.f('ix_gtfs_agency_agency_id'), table_name='gtfs_agency')
    op.drop_table('gtfs_agency')
