import csv

def load_stops(path):
    stops = {}

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stops[row["stop_id"]] = {
             "name": row["stop_name"],
             "lat": float(row["stop_lat"]),
             "lon": float(row["stop_lon"]),
             "parent_station": row.get("parent_station")
               }
    return stops


def load_stop_times(path):
    stop_times = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stop_times.append(row)
    return stop_times

def load_trips(path):
    trips = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trips[row["trip_id"]] = row
    return trips

def load_routes(path):
    routes = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            routes[row["route_id"]] = row["route_short_name"]
    return {
    row["route_id"]: {
        "route_short_name": row["route_short_name"],
        "route_long_name": row["route_long_name"]
    }
}

def load_calendar(path):
    calendar = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            calendar[row["service_id"]] = row
    return calendar


def load_calendar_dates(path):
    dates = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.append(row)
    return dates