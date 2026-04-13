from collections import defaultdict
from calendar_utils import is_service_active, time_to_seconds


def build_graph(stop_times, stops, trips, routes, calendar, calendar_dates, date):
    graph = defaultdict(list)
    
    stops_geo = {
        stop_id: {
            'lat': float(stop['lat']),
            'lon': float(stop['lon']),
            'name': stop['name']
        }

        for stop_id, stop in stops.items()
    }
    active_trips = {}
    for trip_id, trip in trips.items():
        if is_service_active(trip['service_id'], date, calendar, calendar_dates):
            route = routes.get(trip['route_id'], {})
            line_name = route.get('route_short_name') or route.get('route_long_name') or ""
            active_trips[trip_id] = line_name
    
    stop_times.sort(key=lambda x: (x["trip_id"], int(x["stop_sequence"])))

    for i in range(len(stop_times) - 1):
        curr = stop_times[i]
        nxt = stop_times[i + 1]

        if curr["trip_id"] != nxt["trip_id"]:
            continue

        trip_id = curr["trip_id"]
        if trip_id not in active_trips:
            continue

        u = curr["stop_id"]
        v = nxt["stop_id"]
        dep_time = time_to_seconds(curr["departure_time"])
        arr_time = time_to_seconds(nxt["arrival_time"])

        if arr_time < dep_time:
            continue  

        graph[u].append({
            "to": v,
            "type": "ride",
            "departure_time": dep_time,
            "arrival_time": arr_time,
            "travel_time": arr_time - dep_time,
            "line": active_trips[trip_id],
            "trip_id": trip_id
        })

    # станция и набор остановок к ней
    stations = defaultdict(list)

    for stop_id, stop in stops.items():
        parent = stop.get("parent_station")
        key = parent if parent and parent.strip() != "" else stop_id
        stations[key].append(stop_id)

    TRANSFER_TIME = 180  
    for group in stations.values():
        if len(group) < 2:
            continue

        for u in group:
            for v in group:
                if u == v:
                    continue

                graph[u].append({
                    "to": v,
                    "type": "transfer",
                    "min_transfer_time": TRANSFER_TIME,
                    "departure_time": None,
                    "arrival_time": None,
                    "travel_time": TRANSFER_TIME,
                    "line": "TRANSFER",
                    "trip_id": None
                })

    return graph, stops_geo