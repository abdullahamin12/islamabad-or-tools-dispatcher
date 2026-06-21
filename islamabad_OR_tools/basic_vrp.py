from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

def create_data():
    # Distance matrix (depot + 3 customers)
    distance_matrix = [
        [0, 10, 15, 20],   # from depot to 0,1,2,3
        [10, 0, 35, 25],   # from customer 1
        [15, 35, 0, 30],   # from customer 2
        [20, 25, 30, 0]    # from customer 3
    ]

    # Demands for each node (index 0 = depot, 1,2,3 = customers)
    demands = [0,1,2,5]  # depot has 0 demand

    # Vehicle capacities (both vehicles have same capacity)
    vehicle_capacities = [4,4]

    num_vehicles = 2
    depot = 0

    return {
        'distance_matrix': distance_matrix,
        'demands': demands,
        'vehicle_capacities': vehicle_capacities,
        'num_vehicles': num_vehicles,
        'depot': depot,
    }

def solve_vrp():
    data = create_data()
    distance_matrix = data['distance_matrix']
    demands = data['demands']
    num_vehicles = data['num_vehicles']
    depot = data['depot']

    # Create the routing model
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)
    
    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Capacity callback
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    capacity_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    # Add capacity dimension
    routing.AddDimensionWithVehicleCapacity(
        capacity_callback_index,
        0,  # slack
        data['vehicle_capacities'],
        True,  # start cumul to zero
        'Capacity',
    )

    # Search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve
    solution = routing.SolveWithParameters(search_parameters)

    if solution is None:
        print("No solution found.")
        return

    # Print solution
    print("Total distance:", solution.ObjectiveValue())
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        route_load = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            route_load += demands[node]
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))  # depot at end
        print(f"Vehicle {vehicle_id} route: {route} (load: {route_load})")

if __name__ == "__main__":
    solve_vrp()