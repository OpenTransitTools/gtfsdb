from gtfsdb import util
import logging
log = logging.getLogger(__name__)


class RouteStopBase(object):

    @classmethod
    def is_arrival(cls, session, trip_id, stop_id):
        """
        :return True if it looks like this Trip / Stop pair is an arrival only
        NOTE: this routine might be EXPENSIVE since it is
        Further, this routine isn't well thought out...not sure block.is_arrival() works
        """
        _is_arrival = False

        from gtfsdb import Block
        blocks = Block.blocks_by_trip_stop(session, trip_id, stop_id)
        if blocks:
            for b in blocks:
                if b.is_arrival():
                    _is_arrival = True
                    break
        return _is_arrival


    @classmethod
    def query_route_short_names(cls, session, stop, filter_active=False):
        """
        :return an array of short names and types
        """
        from .route_stop import RouteStop

        # import pdb; pdb.set_trace()
        # step 1: create a short_names list
        short_names = []

        # step 2: use either route-dao list or find the active stops
        routes = stop.routes
        if routes is None or len(routes) == 0:
            routes = RouteStop.active_unique_routes_at_stop(session, stop_id=stop.stop_id)
            routes.sort(key=lambda x: x.route_sort_order, reverse=False)

        # step 3: build the short names list
        for r in routes:
            if filter_active and r.is_active() is False:
                continue
            sn = {'route_id': r.route_id, 'type': r.type, 'route_type': r.type.route_type, 'otp_type': r.type.otp_type, 'route_short_name': r.make_route_short_name(r)}
            short_names.append(sn)

        return short_names

    @classmethod
    def to_route_short_names_as_string(cls, short_names, sep=", "):
        """
        :return a string representing all short names (e.g., good for a tooltip on a stop popup)
        """
        ret_val = None
        for s in short_names:
            rsn = s.get('route_short_name')
            if rsn:
                if ret_val is None:
                    ret_val = rsn
                else:
                    ret_val = "{}{}{}".format(ret_val, sep, rsn)
        return ret_val

    @classmethod
    def query_by_stop(cls, session, stop_id, agency_id=None, date=None, count=None, sort=False):
        """
        get all route stop records by looking for a given stop_id.
        further filtering can be had by providing an active date and agency id
        """
        from .route_stop import RouteStop

        # step 1: query all route stops by stop id (and maybe agency)
        q = session.query(RouteStop).filter(RouteStop.stop_id == stop_id)
        if agency_id is not None:
            q = q.filter(RouteStop.agency_id == agency_id)

        # step 2: filter based on date
        if date:
            date = util.check_date(date)
            q = q.filter(RouteStop.start_date <= date).filter(date <= RouteStop.end_date)

        # step 3: sort the results based on order column
        if sort:
            q = q.order_by(RouteStop.order)

        # step 4: limit the number of objects returned by query
        if count:
            q = q.limit(count)

        ret_val = q.all()
        return ret_val

    @classmethod
    def unique_routes_at_stop(cls, session, stop_id, agency_id=None, date=None, route_name_filter=False):
        """
        get a unique set of route records by looking for a given stop_id.
        further filtering can be had by providing an active date and agency id, and route name
        """
        ret_val = []

        route_ids = []
        route_names = []

        route_stops = cls.query_by_stop(session, stop_id, agency_id, date, sort=True)
        for rs in route_stops:
            # step 1: filter(s) check against hashtable
            if rs.route_id in route_ids:
                continue
            if route_name_filter and rs.route.route_name in route_names:
                continue

            # step 2: add route attributes to cache hash-tables for later filtering (e.g. see filters above)
            route_ids.append(rs.route_id)
            route_names.append(rs.route.route_name)

            # step 3: this route is unique, so append route object to results
            ret_val.append(rs.route)
        return ret_val
