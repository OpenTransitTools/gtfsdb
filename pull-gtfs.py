import requests
from gtfsdb import Database, GTFS
from joblib import Parallel, delayed
from sqlalchemy.exc import IntegrityError



def get_sources():
    response = requests.get('http://www.gtfs-data-exchange.com/api/agencies')
    agencies = response.json()['data']
    source_zips = []
    for agency in agencies:
        feed = agency['feed_baseurl']
        if '.zip' in feed:
            source_zips.append(feed)
    print "Found {} Feeds".format(len(source_zips))

#sources = get_sources()
sources = ['/Users/rhunter/Desktop/action_20150129_0101.zip']
#sources = ['/Users/rhunter/Desktop/action_20150129_0101.zip', '/Users/rhunter/Desktop/abq-ride_20150802_0107.zip']

#db_string = 'sqlite:///gtfs.db'
#db_string = 'postgresql://censio:insecure@test-gtfs.cvklf6ftrsse.us-east-1.rds.amazonaws.com:5432/gtfs_data'

db_string = 'postgresql://postgres:insecure@localhost:5432/gtfs_data'

db = Database(url=db_string, is_geospatial=True)
db.create()
try:
    GTFS.bootstrab_db(db)
except IntegrityError:
    pass


def process_source(source):
    try:
    	gtfs = GTFS(filename=source)
    	p_db = Database(url=db_string, is_geospatial=True)
    	gtfs.load(p_db, filename=source)
    except Exception, e:
        print e
    finally:
        pass
      

#Parallel(n_jobs=36)(delayed(process_source)(source) for source in sources)


for source in sources:
    process_source(source)



