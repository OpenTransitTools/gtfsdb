This is forked from: https://github.com/OpenTransitTools/gtfsdb

Installation:

install like a normal python package via the setup.py `ie pip install . `

Most of the functionality is wrapped up in a click app: https://github.com/Censio/gtfsdb/blob/master/gtfsdb/scripts.py

after install you should be able to call `gtfsdb --help` for some basic documentation. The current implementation is pretty hackish. The biggest differences between this and the original application are::
* Capable of Parallel execution. It should be noted that this still relies on `INSERT` to push to the database instead of the preffered `COPY`. This results in the parallelization being a mixed blessing. I tried to keep the inserts append only and relaxed constraints wherver possible.
* the application devides transactions by feeds. We commit once per feed file operation. Scary, and memory heavy, but it opens the door for atomic updates of agency feeds. Prior to this, I used asycronous parse/push: see https://github.com/Censio/gtfsdb/commit/53c60a39da61fc89c5bfdf135443c24eaa9fe614 if the single commit becomes unwieldy.
* I convert all forign keys to UUIDs and track them across the feed. This prevents key collisions

General Procedure for creating a database:

1. load the feed either via the zip loader: `gtfsdb add-by-zip <Directory or zip file>`
2. Create the indexed `gtfsdb create-index`
3. Create the geometries `gtfsdb create-geometry`
4. Convert the SRID by running sql/srid_conversion_to_final.sql against the database. This is nessesary because the final database uses UTM as opposed to Lat Lon. PostGIS doesnt differentiate between Point lat lon and Point x y in a meaningful way. Thus, my current workaround is to create the database using SRID 4326 and converting to 900913 ad hoc.
