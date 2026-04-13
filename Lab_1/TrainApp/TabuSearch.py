import sys
import time
from collections import deque
from dijkstra import dijkstra
from calendar_utils import time_to_seconds
import itertools
from graph import build_graph
from loader import (
    load_stops, load_stop_times, load_trips,
    load_routes, load_calendar, load_calendar_dates
)

def seconds_to_time(seconds):
    seconds = int(seconds) % 86400 
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def find_stops_by_name(stops, name):
    name = name.lower()
    return [
        stop_id
        for stop_id, stop in stops.items()
        if name in stop["name"].lower()
    ]

def calculate_cost(path, mode='t'):
    if not path:
        return float('inf')
    if mode == 't':
        return path[-1][4] - path[0][3]
    else:
        transfers = 0
        last_real_trip = None
        
        for i in range(len(path)):
            current_trip = path[i][2]
            if current_trip and "TRANSFER" not in str(current_trip):
                if last_real_trip is not None and current_trip != last_real_trip:
                    transfers += 1
                last_real_trip = current_trip
                
        return transfers

def largest_cost(path):
    if not path: return None
    worst_edge = None
    worst_val = -1
    for edge in path:
        u, v, trip_id, dep, arr = edge
        duration = arr - dep
        if duration > worst_val:
            worst_val = duration
            worst_edge = edge
    return worst_edge


def generate_neigh(graph, path, expensive_edge):
    neighbors = []
    if not path:
        return neighbors
        
    start_time = path[0][3]
    
    for i in range(len(path)):
        if path[i] != expensive_edge:
            continue
            
        u, v_old, trip_old, dep_old, arr_old = path[i]
        arrival_to_u = path[i - 1][4] if i > 0 else start_time

        
        for edge in graph.get(u, []):
            v_new = edge["to"]
            trip_new = edge.get("trip_id", "TRANSFER")
            
            if i < len(path) - 1:
                next_u = path[i + 1][0]
                if v_new != next_u:
                    continue 

          
            if edge.get("type") == "transfer":
                wait_time = edge.get("min_transfer_time", 180)
                new_dep = arrival_to_u + wait_time
                new_arr = new_dep 
            else:
                
                p_dep = edge.get("departure_time")
                if p_dep is None or p_dep < arrival_to_u:
                    continue
                new_dep = p_dep
                new_arr = edge["arrival_time"]

            new_segment = (u, v_new, trip_new, new_dep, new_arr)
            new_path = path[:i] + [new_segment]
            current_time = new_arr
            possible_path = True

            for j in range(i + 1, len(path)):
                uj, vj, tripj, depj, arrj = path[j]
                found_next_step = False
                
                for potential_edge in graph.get(uj, []):
                    if potential_edge["to"] == vj:
                      
                        p_dep_j = potential_edge.get("departure_time")
                        if p_dep_j is not None:
                            if p_dep_j >= current_time:
                                new_path.append((uj, vj, potential_edge.get("trip_id"), 
                                                 p_dep_j, potential_edge["arrival_time"]))
                                current_time = potential_edge["arrival_time"]
                                found_next_step = True
                                break
                        elif potential_edge.get("type") == "transfer":
                            t_time = potential_edge.get("min_transfer_time", 180)
                            new_path.append((uj, vj, "TRANSFER", current_time, current_time + t_time))
                            current_time += t_time
                            found_next_step = True
                            break
                
                if not found_next_step:
                    possible_path = False
                    break

            if possible_path:
                neighbors.append((i, path[i], new_segment, new_path))
                
    return neighbors

def tabu_search(graph, start_nodes, end_nodes, start_time_str, mode='t', iterations=50, list_l_length=1):
    res = dijkstra(graph, start_nodes, end_nodes, start_time_str)
   
    if not res: return None
    
    _, best_path, _, _ = res
    best_cost = calculate_cost(best_path, mode)
    current_path = list(best_path)
    tabu_limit = list_l_length*2
    
    tabu_set = set()
    tabu_list = deque(maxlen=tabu_limit)

    for _ in range(iterations):
        expensive_edge = largest_cost(current_path)
        if not expensive_edge: break
        
        neighbors = generate_neigh(graph, current_path, expensive_edge)
        best_neighbor = None
        best_cost_iter = float('inf')
        best_move = None

        for i, old_s, new_s, n_path in neighbors:
            cost = calculate_cost(n_path, mode)
            move = (i, old_s, new_s)
            
            if move in tabu_set and cost >= best_cost: continue
            
            if cost < best_cost_iter:
                best_cost_iter = cost
                best_neighbor = n_path
                best_move = move

        if not best_neighbor: break
        current_path = best_neighbor
        tabu_list.append(best_move)
        tabu_set.add(best_move)

        if best_cost_iter < best_cost:
            best_cost = best_cost_iter
            best_path = current_path

    return best_path, best_cost


def solve_full_trip(graph, stops_dict, start_node_id, stop_list_names, mode, start_time_str):
    start_calc_time = time.time()
    
    stops_to_visit_names = [s.strip() for s in stop_list_names.split(';') if s.strip()]
    
    target_stop_ids = []
    for name in stops_to_visit_names:
        ids = find_stops_by_name(stops_dict, name)
        if not ids:
            print(f"Error: Nie znaleziono {name}")
            return
        target_stop_ids.append(ids[0])
    
    best_overall_route = None
    min_overall_cost = float('inf')
   
    for permutation in itertools.permutations(target_stop_ids):
        current_node = start_node_id
        current_time_val = start_time_str
        temp_route = []
        possible = True
       
        for next_stop_id in permutation:
            res = tabu_search(graph, [current_node], [next_stop_id], current_time_val, mode, iterations=10)
            if not res:
                possible = False
                break
            path, _ = res
            temp_route.extend(path)
            current_node = next_stop_id
            current_time_val = seconds_to_time(path[-1][4])
            
        if not possible: continue
            
        res_back = tabu_search(graph, [current_node], [start_node_id], current_time_val, mode, iterations=10)
        if res_back:
            temp_route.extend(res_back[0])
            total_cost = calculate_cost(temp_route, mode)
            
            if total_cost < min_overall_cost:
                min_overall_cost = total_cost
                best_overall_route = temp_route

    if not best_overall_route:
        print("Nie udało się znaleźć optymalnej kolejności.")
        return

    print("\n" + "="*95)
    print(f"{'ODJAZD':<25} | {'PRZYJAZD':<25} | {'LINIA':<17} | {'START':<10} | {'KONIEC':<10}")
    print("-"*95)

    for u, v, line, dep, arr in best_overall_route:
        u_name = stops_dict[u]['name']
        v_name = stops_dict[v]['name']
        if u_name == v_name: continue
        
        line_name = line if line else "TRANSFER"
        print(f"{u_name[:24]:<25} | {v_name[:24]:<25} | {line_name:<17} | {seconds_to_time(dep):<10} | {seconds_to_time(arr):<10}")
    
    print("="*95)
    print(f"Wartość kryterium: {min_overall_cost}")
    print(f"Czas obliczeń: {time.time() - start_calc_time:.4f}s")


def main():
    stops = load_stops("data/stops.txt")
    stop_times = load_stop_times("data/stop_times.txt")
    trips = load_trips("data/trips.txt")
    calendar = load_calendar("data/calendar.txt")
    calendar_dates = load_calendar_dates("data/calendar_dates.txt")
    routes = load_routes("data/routes.txt") 


    start_name = input("Przystanek początkowy A: ")
    stops_l_str = input("Lista przystanków L (oddzielone ;): ")
    mode = input("Kryterium (t/p): ")
    start_time = input("Czas rozpoczęcia (HH:MM:SS): ")
    date = input("Data (YYYYMMDD): ")

    graph, _ = build_graph(stop_times, stops, trips, routes, calendar, calendar_dates, date)

    start_ids = find_stops_by_name(stops, start_name)
    if not start_ids:
        print(f"Nie znaleziono przystanku: {start_name}")
        return
    
    solve_full_trip(graph, stops, start_ids[0], stops_l_str, mode, start_time)

if __name__ == "__main__":
    main()