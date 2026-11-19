# SKREVET MED HJÆLP FRA CLAUDE AI
# - MALTE



#############################################################################
#####                           Prerequisites                           #####
############################################################################# 

# import ajacencylist and dijkstra pathfinding algorithm
import adjacency as adj, dijkstra as dpa
import time

# example usage of dijkstra
print(dpa.dijkstra(adj.adjlist, "WP", "RP"))

current = []        # which of the 13 key nodes the robot is at
delivered = []      # which of the 10 delivery spots are done 
picked_white = []   # how many white packages have been picked up so far (0-5)
picked_red = []     # how many red packages have been picked up so far (0-5)
CAPACITY = 5       # package capacity, between 1 and 10

#############################################################################
#####                Distance table for the 13 key nodes                #####
#############################################################################

# upper-case var names define them as constants, they cannot be altered later
START = "ST"
WHITE_PICK, RED_PICK = "WP", "RP"
WHITE_SPOTS = ["W1", "W2", "W3", "W4", "W5"]
RED_SPOTS   = ["R1", "R2", "R3", "R4", "R5"]
# all key locations
KEY = [START, WHITE_PICK, RED_PICK] + WHITE_SPOTS + RED_SPOTS

dist = {} # all distances between all nodes
paths = {} # all routes between all nodes

for a in KEY:
    for b in KEY:
        if a == b:
            dist[a, b] = 0
            paths[a, b] = [a]
        else:
            dist[a, b], paths[a, b] = dpa.dijkstra(adj.adjlist, a, b)

best_total = float("inf")   # shortest full route found so far
best_stops = []             # the stops of that route



#############################################################################
##### The search function for brute-forcing the shortest possible path. #####
#############################################################################

# At any given time the robot has 4 options.
# 1. pick up a white package
# 2. pick up a red package
# 3. deliver a white package to an undelivered spot
# 4. deliver a red package to an undelivered spot
#
# The search function is a recursive function that is very time consuming to run
# the runtimes for 1-5 packages/spots of each color can be found after the search function
# it goes trough all possible options at all possible steps in the process.
# in the end it returns the route with the shortest total distance

# debugging for search function
calls = 0
last = time.time()

def search(current, white_left, red_left, carry_w, carry_r,
           white_spots_left, red_spots_left, so_far, stops):
    """_Function for finding the shortest route by brute force_

    Args:
        current (_string_): _The node the robot is currently at_
        white_left (_int_): _The amount of white packages left_
        red_left (_int_): _The amount of red packages left_
        carry_w (_int_): _The amount of white packages the robot is carrying_
        carry_r (_int_): _The amount of red packages the robot is carrying_
        white_spots_left (_list_): _A list of the white delivery nodes yet to have a package delivered_
        red_spots_left (_list_): _A list of the red delivery nodes yet to have a package delivered_
        so_far (_float_): _The current distance traveled_
        stops (_list_): _A List of nodes visited_
    """
    
    global best_total, best_stops, calls, last

    # debugging to track the search mid run
    calls += 1 # iteration counter

    # every 1.000.000 iterations print the debug data
    if calls % 1_000_000 == 0:
        # prints the amount of iterations, the shortest route dist so far and the time elapsed.
        print(calls, best_total, round(time.time() - last, 1), "s")

    # Stop early if this route is already longer than the best one found
    if so_far >= best_total:
        return

    # Everything delivered: add the trip home and compare
    if not white_spots_left and not red_spots_left:
        total = so_far + dist[current, START]
        if total < best_total:
            best_total = total
            best_stops = stops
        return

    # if the robot doe not have room
    has_room = carry_w + carry_r < CAPACITY

    # 1. Pick up a white package
    if white_left > 0 and has_room:
        search(WHITE_PICK, 
               white_left - 1, # now there is one less WHITE package to pick up
               red_left, 
               carry_w + 1, # now carrying one more WHITE package
               carry_r,
               white_spots_left, 
               red_spots_left,
               so_far + dist[current, WHITE_PICK], 
               stops + [WHITE_PICK])

    # 2. Pick up a red package
    if red_left > 0 and has_room:
        search(RED_PICK, 
               white_left, 
               red_left - 1, # now there is one less RED package to pick up
               carry_w, 
               carry_r + 1, # now carrying one more RED package
               white_spots_left, 
               red_spots_left,
               so_far + dist[current, RED_PICK],
               stops + [RED_PICK])

    # 3. Deliver a white package to any unused white spot
    if carry_w > 0:
        for spot in white_spots_left:
            others = [s for s in white_spots_left if s != spot]
            search(spot, 
                   white_left, 
                   red_left, 
                   carry_w - 1, # now carrying one less WHITE package
                   carry_r,
                   others, 
                   red_spots_left,
                   so_far + dist[current, spot], 
                   stops + [spot])

    # 4. Deliver a red package to any unused red spot
    if carry_r > 0:
        for spot in red_spots_left:
            others = [s for s in red_spots_left if s != spot]
            search(spot, 
                   white_left, 
                   red_left, 
                   carry_w, 
                   carry_r - 1, # now carrying one less RED package
                   white_spots_left, 
                   others,
                   so_far + dist[current, spot], 
                   stops + [spot])



#############################################################################
#####                      Finally build the route                      #####
#############################################################################

def build_route():
    route = [START] # always begin in start node
    cur = START     # current node

    for target in best_stops:
        route += paths[cur, target][1:]
        cur = target
    route += paths[cur, START][1:]
    print(route)



#############################################################################
#####                         Running the search                        #####
#############################################################################

# Start: at ST, 5 white and 5 red waiting, carrying nothing, all spots open
t = time.time()
search(START, 5, 5, 0, 0, WHITE_SPOTS[:5], RED_SPOTS[:5], 0, [])
print(time.time() - t, "seconds")
build_route()

# 2 red and white packages, 2 red and white delivery spots: 0.00119s runtime
# 3 red and white packages, 3 red and white delivery spots: 0.05863s runtime
# 4 red and white packages, 4 red and white delivery spots: 3.32421s runtime
# 5 red and white packages, 5 red and white delivery spots: 658.970s runtime (11 ish min)


# result of running the search with a capacity of 10 packages at once.
# total distance of 2773.5 cm traveled
fastest_route_10 = ['ST', 'A', 'B', 'C', 'WP', 'C', 'B', 'W1', 'B', 'A', 'M', 'L', 
                 'K', 'Q', 'R', 'RP', 'R', 'S', 'I', 'R3', 'I', 'H', 'R2', 'H', 
                 'gh1', 'G', 'W3', 'G', 'fg2', 'fg1', 'F', 'W2', 'F', 'E', 'D', 
                 'R1', 'D', 'E', 'L', 'K', 'Q', 'P', 'R4', 'P', 'O', 'W4', 'O', 
                 'N', 'W5', 'N', 'R5', 'N', 'M', 'A', 'ST']