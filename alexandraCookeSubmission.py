import sys
import re
import math

#Read input file from command line
def read_input_file(file_path):
    routes = [] #List to store each line/load
    with open(file_path, 'r') as locations:
        next(locations) #Skip the legend/first line in file
        for line in locations:
            pattern = r'\((.*?)\)' #Regex expression to pattern match and extract only the numbers without parenthesis/load number
            matches = re.findall(pattern, line) #Find all instances in the line matching the pattern
            coordinates = []
            #For each match instance (pickup and dropoff for the load), append to coordinate list
            for match in matches:
                x, y = match.split(',')
                x = float(x.replace("-", "-")) #Ensure negative sign in string can be coverted to float
                y = float(y.replace("-", "-"))
                coordinates.append([x,y])

            #Append load data from line to the routes list
            routes.append(coordinates)
            
    return routes

#Adds an edge to our graph from a current location to a potiental next location
#Assignes a value [possible location, distance to location] to our dictionary at current location key
def add_edge(currentLocation, nextLocation, distance):
    if currentLocation not in graph:
        graph[currentLocation] = [] 
    if nextLocation not in graph:
        graph[nextLocation] = []

    graph[currentLocation].append((nextLocation, float(distance))) 

#Create graph using Python dictionary data structure
def create_graph(routes):
    i = 1 #Respresenting current load number

    #Iterate through each load stored in routes
    for currentLoad in routes:
        #Initialize labels for our graph nodes/dictionary keys
        dropoffNode = (i)
        start = "start" 

        #Get seperate pickup/dropoff locations for specific load
        pickup = currentLoad[0]
        dropoff = currentLoad[1]

        #Find the total Euclidean distance to complete current load from start location (0,0 -> pickup -> dropoff) 
        pickupDistance = pickup[0] ** 2 + pickup[1] ** 2
        pickupEuclidean = math.sqrt(pickupDistance)
        loadDistanceX = (dropoff[0] - pickup[0]) ** 2
        loadDistanceY = (dropoff[1] - pickup[1]) ** 2
        loadEuclidean = math.sqrt(loadDistanceX + loadDistanceY)
        totalTrip = pickupEuclidean + loadEuclidean

        #Add an edge to our graph from start location to dropoff location
        add_edge(start, dropoffNode, totalTrip) 

        #Find the total Euclidean distance to return to the start location after completing current load (dropoff -> start) 
        dropoffDistance = dropoff[0] ** 2 + dropoff[1] ** 2
        dropoffEuclidean = math.sqrt(dropoffDistance)

        #Add edge to our graph from current dropoff location back to start location
        add_edge(dropoffNode, "start", dropoffEuclidean)

        #After completing a load, a driver has the potential to complete another
        #Iterate through route locations to add an edge from current load location to all other load locations
        for y in range(len(routes)):
            #Check the next load is not the same as our current load
            if i != y + 1:
                #Initialize labels for our graph nodes/dictionary keys
                currentNode = (i)
                nextLoad = (y+1)

                #Get seperate pickup/dropoff locations for current and next loads
                dropoff = currentLoad[1]
                nextPickup = routes[y][0]
                nextDropoff = routes[y][1]

                #Find the total Euclidean distance to complete the next potential load from the current load location (dropoff -> pickup -> dropoff) 
                pickupDistanceX = (dropoff[0] - nextPickup[0]) ** 2
                pickupDistanceY = (dropoff[1] - nextPickup[1]) ** 2
                pickupEuclidean = math.sqrt(pickupDistanceX + pickupDistanceY)
                loadDistanceX = (nextPickup[0] - nextDropoff[0]) ** 2
                loadDistanceY = (nextPickup[1] - nextDropoff[1]) ** 2
                loadEuclidean = math.sqrt(loadDistanceX + loadDistanceY)
                nextLoadDistance = + pickupEuclidean + loadEuclidean

                #Add edge to our graph from the current load dropoff location to the next potential load dropoff location
                add_edge(currentNode, nextLoad, nextLoadDistance)

        i +=1 #Increment i to reflect the next load

#Obtain the distance between two locations
def distance_between_two_nodes(graph, startNode, endNode):
    #Iterate through each node with an edge connected to the current node to find desired end location
    for node in graph[startNode]:
        if node[0] == endNode:
            return node[1] #Return distance from [load number, distance] value accociated with current location dictionary key

#Assign loads to drivers
def find_optimal_paths(graph, startNode, path, visited, totalDistance):
    #Ensure a driver's next load is not the start location
    if startNode != "start":
        path.append(startNode)

    #Initialize local variablee
    minDistance = 10000
    nextLocation = startNode
    returnDistance = graph[startNode][0][1]

    #Return driver's load assignments if his/her distance limit is optimized
    if totalDistance + returnDistance > 720:
        path.pop() #Remove the last location from the drivers load assignment list if it will cause him/her to exceed the limit
        return path
    
    #If the driver has not exceed his/her distance limit, assign the closet load to the driver's current location
    for node in graph[startNode]:
        #Ensure a driver's next load is not the start location
        if node[0] != "start":
            #Ensure a driver's next load has not already been completed
            if node[0] not in path and node[0] not in visited:
                #Assign the closest location as the driver's next load 
                distance = distance_between_two_nodes(graph, startNode, node[0])
                if distance < minDistance:
                    minDistance = distance
                    nextLocation = node[0]
    
    totalDistance += minDistance #Update driver's total distance traveled including next load
    
    return find_optimal_paths(graph, nextLocation, path, visited, totalDistance)

#Create a list of loads for each driver        
def driver_loads(graph):
    visited = [] #Keeps track of loads once completed by a driver
    paths = [] #Stores all driver's loads

    #Continue assigning loads until all locations are visited
    while len(visited) != len(routes):
        path = (find_optimal_paths(graph, "start", [], visited, 0)) #Obtain list of loads for single driver

        #Iterate through each load assigned to current driver and add them to our visited list
        for x in path:
            visited.append(x)
        
        #Add current drivers load list to list of driver loads
        paths.append(path)

    return paths

#Obtain VRP file from command line arguments
file_path = sys.argv[1]

#Read file and obtain location list
routes = read_input_file(file_path)

#Initalize graph
graph = dict()

#Create graph
create_graph(routes)

#Obtain solution for drivers' loads
paths = driver_loads(graph)

#Ouput solution
for schedule in paths:
    print(schedule)

