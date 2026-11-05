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
from adjacency import adjlist

# Dijkstras
def dijkstra(adj, src):

    # a list of all distances from the source vertex
    # set all distances to infinity
    dist = {v: float("inf") for v in adj}

    # the distance to the source vertex is 0
    dist[src] = 0

    # a priority queue using the HeapQ library 
    heap = []

    # the source vertex is already added to the heap / priority queue
    pq.heappush(heap, (0, src))

    # while there IS an element in the heap 
    while heap:

        # d is the distance of the vertex, for the source node src it is set to 0
        # v is the vertex name eg. "ST" or "A"
        d, v = pq.heappop(heap)

        # for each neighbour vertex to the current vertex
        for n in adj[v]:

            # distance + weight of the current vertex
            # adj[vertex name][neighboring vertex][distance between the two vertices]
            dw = (d + adj[v][n][0])

            # if the neighboring distance of the neighbouring vertex is greater than dw
            if dist[n] > dw:

                # update the distance of the neighbour vertex (from "inf" to the edgeweight)
                dist[n] = dw

                # push the optional vertexes to the heap (so that they can be chosen from in the next iteration)
                pq.heappush(heap, (dist[n], n))

    return dist

# Tester
print(dijkstra(adjlist, "ST"))


##### Next step
# i need to add a second dictionary that keeps track of the path taken from vertex to vertex.
# currently it only returns the distances to get to each vertex from the source vertex.