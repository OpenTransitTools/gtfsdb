
--
-- how to find stop time nearest to a date & time
-- TODO - min / max / etc... ???
--
select *
from trimet.trips t
where t.service_id in (select service_id from trimet.universal_calendar uc where uc.date in ('2018-08-08', '2018-08-09'))
and t.route_id = '20'
and t.trip_id = st.trip_id
and '12:13:00' > st.arrival_time
limit 5;
