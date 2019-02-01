from gtfsdb import util

import logging
log = logging.getLogger(__name__)


class RouteBase(object):
    """
    provides a generic set of route query routines
    """

    def is_active(self, date=None):
        log.warning("calling abstract base class")
        return True

    @classmethod
    def query_route(cls, session, route_id, detailed=False):
        """
        simple utility for quering a route from gtfsdb
        """
        # import pdb; pdb.set_trace()
        ret_val = None
        try:
            log.info("query Route for {}".format(route_id))
            q = session.query(cls)
            q = q.filter(cls.route_id == route_id)
            if detailed:
                # todo: some joined junk, ala what we see in stops? -- q = q.options(joinedload("stop_features"))
                pass
            ret_val = q.one()
        except Exception as e:
            log.info(e)
        return ret_val

    @classmethod
    def query_route_list(cls, session):
        """
        :return list of *all* Route orm objects queried from the db
        """
        # import pdb; pdb.set_trace()
        from .route import RouteFilter
        routes = session.query(cls)\
            .filter(~cls.route_id.in_(session.query(RouteFilter.route_id)))\
            .order_by(cls.route_sort_order)\
            .all()
        return routes

    @classmethod
    def query_active_routes(cls, session, date=None):
        """
        :return list of *active* Route orm objects queried from the db
        :note 'active' is based on date ... this routine won't deal with holes in the
              schedule (e.g., when a route is not active for a period of time, due to construction)
        """
        # step 1: grab all routes
        routes = cls.query_route_list(session)

        # step 2: filter routes by active date
        ret_val = cls.filter_active_routes(routes, date)
        return ret_val

    @classmethod
    def filter_active_routes(cls, route_list, date=None):
        """
        filter an input list of route (orm) objects via is_active
        :return new list of routes filtered by date
        """
        # import pdb; pdb.set_trace()
        ret_val = []
        for r in route_list:
            if r and r.is_active(date):
                ret_val.append(r)
        return ret_val

    @classmethod
    def query_nearest_routes(cls, session, geom):
        """
        simple utility for quering a route from gtfsdb
        """
        ret_val = None

    @classmethod
    def query_active_route_ids(cls, session):
        """
        return an array of route_id / agency_id pairs
        {route_id:'2112', agency_id:'C-TRAN'}
        """
        ret_val = []
        routes = cls.query_active_routes(session)
        for r in routes:
            ret_val.append({"route_id": r.route_id, "agency_id": r.agency_id})
        return ret_val

    @classmethod
    def make_route_short_name(cls, route, def_name=None):
        """
        fix up the short name...
        """
        ret_val = def_name
        try:
            ret_val = util.safe_get_any(route, ['route_short_name', 'short_name', 'route_long_name', 'name'])

            # strip off 'Line' from last word, ala MAX Blue Line == MAX Blue
            if ret_val and ret_val.startswith('MAX') and ret_val.endswith('Line'):
                ret_val = " ".join(ret_val.split()[:-1])
            # special fix for Portland Streetcar
            if 'Portland Streetcar' in ret_val:
                ret_val = ret_val.replace('Portland Streetcar', 'PSC').strip()
            # fix WES
            if ret_val and ret_val.startswith('WES '):
                ret_val = "WES"
            # fix Portland Aerial Tram
            if ret_val and ret_val == 'Portland Aerial Tram':
                ret_val = "Aerial Tram"
        except Exception as e:
            log.warning(e)

        return ret_val

