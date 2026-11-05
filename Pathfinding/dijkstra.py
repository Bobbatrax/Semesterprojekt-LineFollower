##### sources
### Teori:
# https://www.geeksforgeeks.org/python/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/
# https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/
# https://graphable.ai/blog/pathfinding-algorithms/#How_does_it_work1

### What is a priority queue:
# https://www.geeksforgeeks.org/dsa/priority-queue-set-1-introduction/

### known pathfinding algorithms
# A* (heuristics) - exact, using an estimated guess to help choose its path.
# Dijkstra’s - exact and faster but more complicated
#
# since the computing of a path is not done real-time we don't actually need the algorithm to be fast,
# it can simply be ran prior to any usecase and stored.
#####

import heapq as pq

# Support function for dijkstra, goes backwards through prev list to return the fastest path.
def path_to(prev, target):
    path = []
    while target is not None:
        # add the target to that path list
        path.append(target)
        # go backwards to the current targets previous vertex
        target = prev[target]

    # return a list of all the previous vertexes 
    # reversed because the path list is found by iteration backwards through the path
    # we reverse the reversed path to get the real path
    return list(reversed(path))

# Dijkstras
def dijkstra(adj, src, target):

    # a dictionary of all distances from the source vertex
    # set all distances to infinity
    dist = {v: float("inf") for v in adj}

    # the distance to the source vertex is 0
    dist[src] = 0

    # a priority queue using the HeapQ library 
    heap = []

    # a dictionary of the previous node
    prev = {v: None for v in adj}
    
    # the source vertex is already added to the heap / priority queue
    pq.heappush(heap, (0, src))

    # while there IS an element in the heap 
    while heap:

        # d is the distance of the vertex, for the source node src it is set to 0
        # v is the vertex name eg. "ST" or "A"
        d, v = pq.heappop(heap)
        
        # skip stale heap entries when a shorter route has been found already
        if d > dist[v]:
            continue

        # for each neighbour vertex to the current vertex
        for n in adj[v]:

            # distance + weight of the current vertex
            # adj[vertex name][neighboring vertex][distance between the two vertices]
            dw = d + adj[v][n][0]

            # if the neighboring distance of the neighbouring vertex is greater than dw
            if dist[n] > dw:

                # update the distance of the neighbour vertex (from "inf" to the edgeweight)
                dist[n] = dw
                prev[n] = v

                # push the optional vertexes to the heap (so that they can be chosen from in the next iteration)
                pq.heappush(heap, (dist[n], n))

    return dist[target], path_to(prev, target)