from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

def create_distance_matrix():
    # Simple 4x4 distance matrix (depot + 3 customers)
    # Index 0 = depot, 1,2,3 = customers
    return [
        [0, 10, 15, 20],   # from depot to 0,1,2,3
        [10, 0, 35, 25],   # from customer 1
        [15, 35, 0, 30],   # from customer 2
        [20, 25, 30, 0]    # from customer 3
    ]

def solve_vrp():
    # Data
    distance_matrix = create_distance_matrix()
    num_vehicles = 2
    depot = 0

    # Create the routing model
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback for distances
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Set the cost of each arc to be the distance
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add capacity constraint (optional, for now we just use distance)
    # For now, we skip capacity and just optimize distance.

    # Set search parameters
    search_parameters = routing.NewSearchParameters()
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
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))  # depot at end
        print(f"Vehicle {vehicle_id} route: {route}")

if __name__ == "__main__":
    solve_vrp()