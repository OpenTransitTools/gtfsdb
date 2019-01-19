import os
import sys
import datetime
import tempfile

import logging
log = logging.getLogger(__name__)


def get_all_subclasses(cls):
    """
    :see https://stackoverflow.com/questions/3862310/how-to-find-all-the-subclasses-of-a-class-given-its-name
    """
    ret_val = set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in get_all_subclasses(c)]
    )
    return ret_val


def make_temp_sqlite_db_uri(name=None):
    """
    will return a FILE URI to a temp file, ala /tmp/bLaHh111 for the path of a new sqlite file db
    NOTE: name is optional ... if provided, the file will be named as such (good for testing and refreshing sqlite db)
    """
    if name:
        db_file = os.path.join(tempfile.gettempdir(), name)
    else:
        db_file = tempfile.mkstemp()[1]
    url = 'sqlite:///{0}'.format(db_file)
    log.debug("DATABASE TMP FILE: {0}".format(db_file))
    return url


def safe_get(obj, key, def_val=None):
    """
    try to return the key'd value from either a class or a dict
    (or return the raw value if we were handed a native type)
    """
    ret_val = def_val
    try:
        ret_val = getattr(obj, key)
    except:
        try:
            ret_val = obj[key]
        except:
            if isinstance(obj, (int, long, str)):
                ret_val = obj
    return ret_val


def safe_get_any(obj, keys, def_val=None):
    """
    :return object element value matching the first key to have an associated value
    """
    ret_val = def_val
    for k in keys:
        v = safe_get(obj, k)
        if v and len(v) > 0:
            ret_val = v
            break
    return ret_val


def check_date(in_date, fmt_list=['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y'], def_val=None):
    """
    utility function to parse a request object for something that looks like a date object...
    """
    if isinstance(in_date, datetime.date) or isinstance(in_date, datetime.datetime):
        ret_val = in_date
    else:
        if def_val is None:
            def_val = datetime.date.today()

        ret_val = def_val
        for fmt in fmt_list:
            try:
                d = datetime.datetime.strptime(in_date, fmt).date()
                if d is not None:
                    ret_val = d
                    break
            except Exception as e:
                log.debug(e)
    return ret_val


class UTF8Recoder(object):
    """Iterator that reads an encoded stream and encodes the input to UTF-8"""
    def __init__(self, f, encoding):
        import codecs
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        if sys.version_info >= (3, 0):
            return next(self.reader)
        else:
            return self.reader.next().encode('utf-8')

    def __next__(self):
        return self.next()
