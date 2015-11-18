"""change sequential ids to uuids

Revision ID: 1cf26d0edb2d
Revises: 
Create Date: 2015-11-16 18:54:12.541185

"""

# revision identifiers, used by Alembic.
revision = '1cf26d0edb2d'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from gtfsdb.model.guuid import GUID
from sqlalchemy.types import Integer, Numeric, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker, Session as BaseSession, relationship

Session = sessionmaker()

def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute('CREATE EXTENSION "uuid-ossp";')
    session.commit()
    op.drop_column('gtfs_fare_rules', 'id')
    op.drop_column('gtfs_frequencies', 'id')
    op.drop_column('gtfs_directions', 'id')
    op.drop_column('route_stops', 'id')
    op.drop_column('gtfs_shapes', 'id')
    op.drop_column('stop_features', 'id')
    op.drop_column('gtfs_stop_times', 'id')
    op.drop_column('gtfs_transfers', 'id')
    op.drop_column('dta_agency', 'id')
    op.add_column('gtfs_fare_rules', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))
    op.add_column('gtfs_frequencies', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))
    op.add_column('gtfs_directions', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))
    op.add_column('route_stops', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))
    op.add_column('gtfs_shapes', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))
    op.add_column('stop_features', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))
    op.add_column('gtfs_stop_times', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))
    op.add_column('gtfs_transfers', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))
    op.add_column('dta_agency', sa.Column('id', GUID(), primary_key=True, server_default = sa.sql.expression.text('uuid_generate_v4()')))

def downgrade():
    op.drop_column('gtfs_fare_rules', 'id')
    op.drop_column('gtfs_frequencies', 'id')
    op.drop_column('gtfs_directions', 'id')
    op.drop_column('route_stops', 'id')
    op.drop_column('gtfs_shapes', 'id')
    op.drop_column('stop_features', 'id')
    op.drop_column('gtfs_stop_times', 'id')
    op.drop_column('gtfs_transfers', 'id')
    op.drop_column('dta_agency', 'id')
    op.add_column('gtfs_fare_rules', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
    op.add_column('gtfs_frequencies', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
    op.add_column('gtfs_directions', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
    op.add_column('route_stops', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
    op.add_column('gtfs_shapes', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
    op.add_column('stop_features', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
    op.add_column('gtfs_stop_times', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
    op.add_column('gtfs_transfers', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
    op.add_column('dta_agency', sa.Column('id', Integer, Sequence(None, optional=True), primary_key=True))
