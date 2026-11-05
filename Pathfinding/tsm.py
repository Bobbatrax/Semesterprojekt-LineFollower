# traveling sales man algorithm
# to find the best route to deliver all the packages to the the delivery sites


### Prerequisites 
# import ajacencylist and dijkstra pathfinding algorithm
import adjacency as adj, dijkstra as dpa

# number of white packages and red packages to be collected and delivered
w_pack_cnt = 5, r_pack_cnt = 5


### Rules
# the algorithm must first collect the white packages before it can deliver white pacakges
# the algorithm must first collect the red pacakges before it can deliver red pacakges
# all white delivery locations must have 1 white package delivered
# all red delivery locations must have 1 red package delivered
# the algorithm must choose the shortest possible route to collect and deliver all packages and return to starting point


# (Step 1) design a regular TSP: Traveling Salesman Problem.
# the premise behind TSP is to deisgn a algorithm that can find the shortest route to visit all cities in a network.
# once we have the TSP as a base i can implement the rules


# (Step 2) design a TSPPD: Traveling Salesman Problem with Pick-up and Delivery
# the premise is no longer to visit all cities, but to pickup all packages and deliver them all to the right locations
# in our system there are only two pickup spots, a white and a red
# there are 10 delivery spots and 10 packages, 5 red, 5 white
# all red packages are identical and can be delivered to any red delivery spot, the same goes for white packages and spots





