"""move string id

Revision ID: 469038f28c54
Revises: 
Create Date: 2015-09-24 15:33:45.556940

"""

# revision identifiers, used by Alembic.
revision = '469038f28c54'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


col_list = [
    ('gtfs_shapes', 'shape_id'),
    ('gtfs_calendar_dates', 'service_id'),
    ('universal_calendar', 'service_id'),
    ('gtfs_stops', 'zone_id'),
    ('gtfs_fare_rules', 'service_id'),
    ('gtfs_fare_rules', 'origin_id'),
    ('gtfs_fare_rules', 'destination_id'),
    ('gtfs_fare_rules', 'contains_id'),
    ('gtfs_shape_geoms', 'shape_id'),
    ('gtfs_trips', 'service_id'),
    ('gtfs_trips', 'shape_id'),
    ('gtfs_trips', 'block_id')
]


def str_uuid(table, column):
    op.execute('alter table {tbl} alter column {col} type uuid using {col}::uuid;'.format(tbl=table, col=column))


def uuid_str(table, column):
    op.execute('alter table {tbl} alter column {col} type VARCHAR(255) using {col}::VARCHAR(255);'.format(
        tbl=table, col=column))


def upgrade():
    for table, column in col_list:
        str_uuid(table, column)


def downgrade():
    for table, column in col_list:
        uuid_str(table, column)
