import heapq
import itertools
from math import radians, cos, sin, asin, sqrt

def hv(lat1, lon1, lat2, lon2):
    R = 6371  
    lat = radians(lat2 - lat1)
    lon = radians(lon2 - lon1)
    a = sin(lat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(lon / 2)**2
    return 2 * R * asin(sqrt(a))



def astar(graph, stops_geo, start_nodes, end_nodes, start_time_secs, mode):
    counter = itertools.count()
    
    pq = []
   
    target_lat = stops_geo[list(end_nodes)[0]]['lat']
    target_lon = stops_geo[list(end_nodes)[0]]['lon']

    for s in start_nodes:
        g_score = 0
        h_score = 0
        
        if mode == 't':
            dist = hv(stops_geo[s]['lat'], stops_geo[s]['lon'], target_lat, target_lon)
            h_score = (dist / 120) * 3600 
        
        heapq.heappush(pq, (g_score + h_score, g_score, next(counter), s, start_time_secs, [], 0, None))

    visited_g_scores = {}

    while pq:
        f, g, _, u, current_time, path, transfers, last_trip = heapq.heappop(pq)
        if u in end_nodes:
            return (g, path, current_time, transfers)

        if u in visited_g_scores and visited_g_scores[u] <= g:
            continue
        visited_g_scores[u] = g

        if u not in graph:
            continue

        for edge in graph[u]:
            v = edge["to"]
            
           
            if edge["type"] == "transfer":
                wait_time = edge.get("travel_time", 180)
                new_g = g + (wait_time if mode == 't' else 0)
                new_time = current_time + wait_time
                new_transfers = transfers
                new_last_trip = last_trip
            else:
                dep = edge["departure_time"]
                if dep < current_time: continue
                is_transfer = 1 if (last_trip is not None and edge["trip_id"] != last_trip) else 0
                
                if mode == 't':
                    new_g = g + (dep - current_time) + edge["travel_time"]
                else:
                    new_g = g + is_transfer
            
                new_time = edge["arrival_time"]
                new_transfers = transfers + is_transfer
                new_last_trip = edge["trip_id"]

            
            h = 0
            if mode == 't':
                dist = hv(stops_geo[v]['lat'], stops_geo[v]['lon'], target_lat, target_lon)
                h = (dist / 120) * 3600
            elif mode == 'p':
                h = 0 

            heapq.heappush(pq, (
                new_g + h, new_g, next(counter), v, new_time,
                path + [(u, v, edge["trip_id"], edge["departure_time"], new_time)],
                new_transfers, new_last_trip
            ))

    return None


