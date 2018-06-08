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

1. Install Python 2.7 (or 3.x), easy_install (https://pypi.python.org/pypi/setuptools) and zc.buildout (https://pypi.python.org/pypi/zc.buildout/2.5.2) on your system...
1. git clone https://github.com/OpenTransitTools/gtfsdb.git
1. cd gtfsdb
1. buildout install prod -- NOTE: if you're using postgres, do a 'buildout install prod postgresql'
1. bin/gtfsdb-load --database_url <db url>  <gtfs file | url>
   examples:
   - bin/gtfsdb-load --database_url sqlite:///gtfs.db gtfsdb/tests/large-sample-feed.zip
   - bin/gtfsdb-load --database_url sqlite:///gtfs.db http://developer.trimet.org/schedule/gtfs.zip
   - bin/gtfsdb-load --database_url postgresql://postgres@localhost:5432 --is_geospatial http://developer.trimet.org/schedule/gtfs.zip  
   NOTE: using the `is_geospatial` arg will take much longer to load...


The best way to get gtfsbd up and running is via the python 'buildout' and 'easy_install' tools.
Highly recommended to first install easy_install (setup tools) and buildout (e.g., easy_install zc.buildout)
before doing anything else.

Postgres users, gtfsdb requires the psycopg2 database driver. If you are on linux / mac, buildout will
install the necessary dependencies (or re-use whatever you have in your system site-lib).
If you are on windows, you most likely have to find and install a pre-compiled version (see below).


Install Steps (on Windows):
===========================
    0. Have a db - docs and examples assume Postgres/PostGIS installed
       http://www.postgresql.org/download/windows
       http://postgis.refractions.net/download/windows/

    1. Python2.7 - http://www.python.org/download/releases/2.7.6/ (python-2.7.6.msi)
       NOTE: see this for setting env variables correctly: https://docs.python.org/3/using/windows.html#excursus-setting-environment-variables

    2a. Install Setup Tools (easy_install) https://pypi.python.org/pypi/setuptools#windows-8-powershell
    2b. easy_install zc.buildout

    3. Install Psygopg2 (from binary):  http://www.stickpeople.com/projects/python/win-psycopg/

    4. Check out gtfsdb from trunk with Git - see: git clone https://github.com/OpenTransitTools/gtfsdb.git

    5. cd top level of gtfsdb tree
    
    6. buildout install prod

    7. bin/gtfsdb-load --database_url <db url>  <gtfs file | url>


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
