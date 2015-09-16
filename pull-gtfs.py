import requests
from gtfsdb import Database, GTFS
from joblib import Parallel, delayed
from sqlalchemy.exc import IntegrityError


#response = requests.get('http://www.gtfs-data-exchange.com/api/agencies')

#agencies = response.json()['data']
#source_zips = []
#for agency in agencies:
#    feed = agency['feed_baseurl']
#    if '.zip' in feed:
#        source_zips.append(feed)
#sources = [source_zips[0]]
sources = ['/Users/rhunter/Desktop/action_20150129_0101.zip',
           '/Users/rhunter/Desktop/abq-ride_20150802_0107.zip']
#db_string = 'sqlite:///gtfs.db'
db_string = 'postgresql://censio:insecure@test-gtfs.cvklf6ftrsse.us-east-1.rds.amazonaws.com:5432/gtfs_data'
#Parallel(n_jobs=2)(delayed(database_load)(filename=source, url=db_string) for source in sources)
db = Database(url=db_string)
db.create()
try:
    GTFS.bootstrab_db(db)
except IntegrityError:
    pass


def process_source(source):
    gtfs = GTFS(filename=source)
    p_db = Database(url=db_string)
    gtfs.load(p_db, filename=source)


#Parallel(n_jobs=2)(delayed(process_source)(source) for source in sources)


for source in sources:
    process_source(source)



