from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

def create_data():
    distance_matrix = [
        [0.0, 14.0326446604846, 6.773007614834758, 27.26444030263413],
        [13.565740687701306, 0.0, 7.288854700065262, 26.592052361660745],
        [7.429384530490422, 9.247051797524735, 0.0, 27.92847902030918],
        [29.74006192170536, 26.48757109473579, 27.924680867593, 0.0],
    ]

    demands = [0, 1, 2, 3]
    vehicle_capacities = [4, 4]
    num_vehicles = 2
    depot = 0

    return {
        "distance_matrix": distance_matrix,
        "demands": demands,
        "vehicle_capacities": vehicle_capacities,
        "num_vehicles": num_vehicles,
        "depot": depot,
    }

def solve_vrp():
    data = create_data()
    distance_matrix = data["distance_matrix"]
    demands = data["demands"]
    num_vehicles = data["num_vehicles"]
    depot = data["depot"]

    # Create the routing model
    route_index_manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
    routing = pywrapcp.RoutingModel(route_index_manager)

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = route_index_manager.IndexToNode(from_index)
        to_node = route_index_manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node]*1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Capacity callback
    def demand_callback(from_index):
        from_node = route_index_manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    # Add capacity dimension
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # max slack
        data["vehicle_capacities"],
        True,
        "Capacity",
    )

    # Search parameters: use only DefaultRoutingSearchParameters, no strategy set
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    solution = routing.SolveWithParameters(search_parameters)

    if solution is None:
        print("No solution found.")
        return

    print("Total distance:", solution.ObjectiveValue()/1000.0)

    names = [
        "Pakistan Monument (Depot)",
        "Centaurus Mall",
        "Lok Virsa",
        "Near Islamabad Airport",
    ]

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        route_load = 0
        while not routing.IsEnd(index):
            node = route_index_manager.IndexToNode(index)
            route.append(names[node])
            route_load += demands[node]
            index = solution.Value(routing.NextVar(index))
        route.append(names[0])
        print(f"Vehicle {vehicle_id} route: {route} (load: {route_load})")

if __name__ == "__main__":
    solve_vrp()