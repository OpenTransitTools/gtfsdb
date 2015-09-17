"""setup rds postgis

Revision ID: 1cbb6c31e044
Revises: 
Create Date: 2015-09-17 14:22:05.891410

"""

# revision identifiers, used by Alembic.
revision = '1cbb6c31e044'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Enable extensions
    op.execute("""
    -- Created from: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.html

    -- Create Extentsions
    create extension postgis;
    create extension fuzzystrmatch;
    create extension postgis_tiger_geocoder;
    create extension postgis_topology;

    -- Set Ownership Permissions
    alter schema tiger owner to rds_superuser;
    alter schema topology owner to rds_superuser;
    alter schema tiger_data owner to rds_superuser;

    CREATE FUNCTION exec(text) returns text language plpgsql volatile AS $f$ BEGIN EXECUTE $1; RETURN $1; END; $f$;
    SELECT exec('ALTER TABLE ' || quote_ident(s.nspname) || '.' || quote_ident(s.relname) || ' OWNER TO rds_superuser')
      FROM (
        SELECT nspname, relname
        FROM pg_class c JOIN pg_namespace n ON (c.relnamespace = n.oid)
        WHERE nspname in ('tiger','topology') AND
        relkind IN ('r','S','v') ORDER BY relkind = 'S')
    s;
    """)

def downgrade():
    pass
