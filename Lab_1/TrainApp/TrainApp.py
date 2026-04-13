import time
import sys
from astar import astar
from loader import (
    load_stops, load_stop_times, load_trips,
    load_routes, load_calendar, load_calendar_dates
)
from graph import build_graph
from dijkstra import dijkstra
from calendar_utils import time_to_seconds  
from visualize import visualize
from TabuSearch import tabu_search


def find_stops_by_name(stops, name):
    name = name.lower()
    return [
        stop_id
        for stop_id, stop in stops.items()
        if name in stop["name"].lower()
    ]

def format_final_time(seconds):
    if seconds is None:
        return "--:--"
    h = (seconds // 3600)
    m = (seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"

def print_path(path, stops):
    last_tid = None
    for step in path:
        u, v, label, dep, arr = step
        
        if last_tid is not None and label != last_tid and label != "TRANSFER":
            print(f"      [TRANSFER] Waiting on the platform {stops[u]['name']}")

        dep_str = format_final_time(dep)
        arr_str = format_final_time(arr)
        
        if label == "TRANSFER":
            print(f"  [WALK] {stops[u]['name']} ({dep_str}) -> {stops[v]['name']} ({arr_str})")
        else:
            print(f"  [RIDE] {stops[u]['name']} [{dep_str}] -> {stops[v]['name']} [{arr_str}] | Line: {label}")
        
        last_tid = label

def main():
    
    stops = load_stops("data/stops.txt")
    stop_times = load_stop_times("data/stop_times.txt")
    trips = load_trips("data/trips.txt")
    calendar = load_calendar("data/calendar.txt")
    calendar_dates = load_calendar_dates("data/calendar_dates.txt")
    routes = load_routes("data/routes.txt") 

    start_name = input("Przystanek początkowy A: ")
    end_name = input("Przystanek końcowy B: ")
    mode = input("Kryterium optymalizacji (t - czas, p - przesiadki): ")
    start_time = input("Czas rozpoczęcia podróży (HH:MM:SS): ")
    date = input("Data (YYYYMMDD): ")

    start_ids = find_stops_by_name(stops, start_name)
    end_ids = find_stops_by_name(stops, end_name)

    if not start_ids or not end_ids:
        print("Nie znaleziono podanych przystanków.")
        return

    start_time_secs = time_to_seconds(start_time)
    start_calc = time.time()

    graph, stops_geo = build_graph( stop_times, stops, trips, routes, calendar, calendar_dates, date)
    result = astar(  graph, stops_geo, set(start_ids), set(end_ids), start_time_secs, mode)

    end_calc = time.time()
    calc_duration = end_calc - start_calc

    if not result:
        print("Nie znaleziono połączenia.")
        return

    cost, path, final_time_secs, transfers = result

    print("\n" + "=" * 60)
    print(f" NAJKRÓTSZA ŚCIEŻKA A* ({'CZAS' if mode == 't' else 'PRZESIADKI'})")
    print("-" * 40)

    print_path(path, stops)

    print("-" * 40)
    print(f"Czas przyjazdu: {format_final_time(final_time_secs)}")
    print(f"Liczba przesiadek: {transfers}")
    print("=" * 60)

    sys.stderr.write(f"\nWartość kryterium ({mode}): {cost}\n")
    sys.stderr.write(f"Czas obliczeń A*: {calc_duration:.4f}s\n")

    result_dejkstra = dijkstra(graph,set(start_ids),set(end_ids),start_time)

    if not result_dejkstra:
     print("Nie znaleziono połączenia.")
     return

    cost, path, final_time_secs, transfers = result_dejkstra

    print("\n" + "=" * 60)
    print(f" NAJKRÓTSZA ŚCIEŻKA DIJKSTRA 'CZAS' ")
    print("-" * 40)

    print_path(path, stops)

    print("-" * 40)
    print(f"Czas przyjazdu: {format_final_time(final_time_secs)}")
    print(f"Liczba przesiadek: {transfers}")
    print("=" * 60)

    sys.stderr.write(f"\nWartość kryterium ({mode}): {cost}\n")

    visualize(graph, path, stops)

if __name__ == "__main__":
    main()