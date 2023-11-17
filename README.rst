===========
GTFSDB
===========


.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/OpenTransitTools/gtfsdb
   :target: https://gitter.im/OpenTransitTools/gtfsdb?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


Supported Databases
*******************

* PostgreSQL (PostGIS for Geo tables) - preferred
* Oracle - tested
* MySQL  - tested
* SQLite - tested


GTFS (General Transit Feed Specification) Database
**************************************************

Python code that will load GTFS data into a relational database, and SQLAlchemy ORM bindings to the GTFS tables in the gtfsdb. The gtfsdb project's focus is on making GTFS data available in a programmatic context for software developers. The need for the gtfsdb project comes from the fact that a lot of developers start out a GTFS-related effort by first building some amount of code to read GTFS data (whether that's an in-memory loader, a database loader, etc...);  GTFSDB can hopefully reduce the need for such drudgery, and give developers a starting point beyond the first step of dealing with GTFS in .csv file format.

Available on pypi: https://pypi.python.org/pypi/gtfsdb


Install from source via github (if you want the latest code) :
**************************************************************

#. Install Python 3.x https://www.python.org/downloads/ (code also runs on 2.7 if you are stuck on that version)
#.  `pip install zc.buildout` - https://pypi.org/project/zc.buildout
#. (optinal step for **postgres users**: 'pip install psycopg2-binary')
#. git clone https://github.com/OpenTransitTools/gtfsdb.git
#. cd gtfsdb
#. buildout install prod -- NOTE: if you're using postgres, do a 'buildout install prod postgresql'
#. bin/gtfsdb-load --database_url <db url>  <gtfs file | url>
#. examples:

   * bin/gtfsdb-load --database_url sqlite:///gtfs.db gtfsdb/tests/large-sample-feed.zip

   * bin/gtfsdb-load --database_url sqlite:///gtfs.db http://developer.trimet.org/schedule/gtfs.zip

   * bin/gtfsdb-load --database_url postgresql://postgres@localhost:5432 --is_geospatial http://developer.trimet.org/schedule/gtfs.zip

     .. note:: adding the `is_geospatial` cmdline flag, when paired with a spatial-database ala PostGIS (e.g., is_spatial is meaningless with sqllite), will take longer to load...but will create geometry columns for both rendering and calculating nearest distances, etc...

#. view db ( example: https://sqliteonline.com )

The best way to get gtfsdb up and running is via the 'zc.buildout' tool.  Highly recommended to first install
buildout (e.g., pip install zc.buildout) before doing much of anything else.

Postgres users, gtfsdb requires the psycopg2-binary database driver.  Installing that via `pip install psychopg2-binary` will relieve gtfsdb from re-installing locally as part of the build.  And if after the fact, you see *exceptions* mentioning

.. note:: if you get the message "ImportError: No module named psycopg2", then 'pip install psychopg2-binary' should fix things. (Assumes you have postgres also installed on the machine you're trying to use the pg driver).


Usage with Docker:
******************

#. Build the image with `docker build -t gtfsdb .`
#. Run it with:

  .. code-block:: bash

     docker run gtfsdb --database_url <db url>  <gtfs file | url>

  .. note:: The entrypoint command is `bin/gtfsdb-load` so the arguments will be passed to it.


Example Queries:
****************

* get first stop time of each trip for route_id 1

  .. code-block:: sql

     select *
     from trips t, stop_times st
     where t.route_id = '1'
     and t.trip_id = st.trip_id
     and st.stop_sequence = 1

* get agency name and number of routes

  .. code-block:: sql

     select a.agency_name, a.agency_id, count(r.route_id)
     from routes r, agency a
     where r.agency_id = a.agency_id
     group by a.agency_id, a.agency_name
     order by 3 desc
