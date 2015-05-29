class UTF8Recoder(object):
    """Iterator that reads an encoded stream and encodes the input to UTF-8"""
    def __init__(self, f, encoding):
        import codecs
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


def get_route_direction_name(headsign, route_long_name, route_direction_name=None):
    ''' this routine will look first at the headsign for a route direction name '''
    ret_val = headsign
    if route_direction_name and headsign == route_long_name:
        ret_val = self.trip.trip_headsign
    return ret_val

