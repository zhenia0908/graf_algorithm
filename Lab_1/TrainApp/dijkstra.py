import heapq
import itertools
from collections import defaultdict
from calendar_utils import time_to_seconds

def dijkstra(graph, start_nodes, end_nodes, start_time_str):
    counter = itertools.count()
    start_time_secs = time_to_seconds(start_time_str)

    pq = []
    for s in start_nodes:
        heapq.heappush(pq, (0, next(counter), s, start_time_secs, [], 0, None))

    visited_nodes = {}
    while pq:
        cost, _, u, current_time, path, transfers, last_trip = heapq.heappop(pq)
        if u in end_nodes:
            return (cost, path, current_time, transfers)

        if u in visited_nodes and visited_nodes[u] <= cost:
            continue
        visited_nodes[u] = cost

        if u not in graph:
            continue

        for edge in graph[u]:
            v = edge["to"]
            if edge["type"] == "transfer":
                transfer_time = edge.get("min_transfer_time", 180)
                new_time = current_time + transfer_time
                new_cost = cost + transfer_time

                heapq.heappush(pq, (
                    new_cost, next(counter), v, new_time,
                    path + [(u, v, "TRANSFER", current_time, new_time)],
                    transfers, last_trip
                ))

            else:
                dep = edge["departure_time"]
                arr = edge["arrival_time"]
                trip_id = edge["trip_id"]

                if dep < current_time:
                    continue

                ride_time = edge["travel_time"]
                is_transfer = 1 if (last_trip is not None and trip_id != last_trip) else 0

                
                new_cost = cost + (dep - current_time) + ride_time
                

                heapq.heappush(pq, (
                    new_cost, next(counter), v, arr,
                    path + [(u, v, trip_id, dep, arr)],
                    transfers + is_transfer,
                    trip_id
                ))

    return None