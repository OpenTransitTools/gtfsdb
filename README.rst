======
GTFSDB
======

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/OpenTransitTools/gtfsdb
   :target: https://gitter.im/OpenTransitTools/gtfsdb?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


Supported Databases
===================

- PostgreSQL (PostGIS for Geo tables) - preferred
- Oracle - tested
- MySQL  - tested
- SQLite - tested


GTFS (General Transit Feed Specification) Database
==================================================

Python code that will load GTFS data into a relational database, and SQLAlchemy ORM bindings to the GTFS tables in the gtfsdb. 
The gtfsdb project's focus is on making GTFS data available in a programmatic context for software developers. The need for the
gtfsdb project comes from the fact that a lot of developers start out a GTFS-related effort by first building some amount of code
to read GTFS data (whether that's an in-memory loader, a database loader, etc...);  GTFSDB can hopefully reduce the need for such
drudgery, and give developers a starting point beyond the first step of dealing with GTFS in .csv file format.

(Pretty old stuff) available on pypi: https://pypi.python.org/pypi/gtfsdb


Install and use via the gtfsdb source tree:
==========================================

1. Install Python 3.x (or 2.7)

1.  `pip install zc.buildout` - https://pypi.org/project/zc.buildout

1. (if a postgres user, then `pip install psycopg2-binary`)

1. git clone https://github.com/OpenTransitTools/gtfsdb.git

1. cd gtfsdb

1. buildout install prod -- NOTE: if you're using postgres, do a 'buildout install prod postgresql'

1. bin/gtfsdb-load --database_url <db url>  <gtfs file | url>

   examples:
   
   - bin/gtfsdb-load --database_url sqlite:///gtfs.db gtfsdb/tests/large-sample-feed.zip
   - bin/gtfsdb-load --database_url sqlite:///gtfs.db http://developer.trimet.org/schedule/gtfs.zip
   - bin/gtfsdb-load --database_url postgresql://postgres@localhost:5432 --is_geospatial http://developer.trimet.org/schedule/gtfs.zip  

   NOTE: adding the `is_geospatial` cmdline flag, when paired with a spatial-database ala PostGIS (e.g., is_spatial is meaningless with sqllite), will take longer to load...but will create geometry columns for both rendering and calculating nearest distances, etc...

1. view db ( example: https://sqliteonline.com )

The best way to get gtfsbd up and running is via the 'zc.buildout' tool.  Highly recommended to first install
buildout (e.g., pip install zc.buildout) before doing much of anything else.

Postgres users, gtfsdb requires the psycopg2-binary database driver.  Installing that via `pip install psychopg2-binary`
will relieve gtfsdb from re-installing locally as part of the build.  And if after the fact, you see exceptions saying
"ImportError: No module named psycopg2", then `pip install psychopg2-binary` should fix that...

Install Steps (on Windows):
===========================
1. Recommend having a 'real' db installed - docs and examples assume Postgres/PostGIS installed
   http://www.postgresql.org/download/windows
   http://postgis.refractions.net/download/windows/

1. Install Python 3.x https://www.python.org/downloads/release/python-391 or Python2.7 https://www.python.org/downloads/release/python-2718

1. `pip install zc.buildout`

1. `git clone https://github.com/OpenTransitTools/gtfsdb.git`

1. `cd gtfsdb`

1. `buildout`

1. bin/gtfsdb-load --database_url <db url>  <gtfs file | url>
   example: `bin/gtfsdb-load --database_url sqlite:///gtfs.db http://developer.trimet.org/schedule/gtfs.zip`

1. view db ( example: https://sqliteonline.com )

Example Query:
==============

-- get first stop time of each trip for route_id 1
select *
from trips t, stop_times st
where t.route_id = '1'
and t.trip_id = st.trip_id
and st.stop_sequence = 1

-- get agency name and number of routes 
select a.agency_name, a.agency_id, count(r.route_id)
from routes r, agency a
where r.agency_id = a.agency_id
group by a.agency_id, a.agency_name
order by 3 desc
