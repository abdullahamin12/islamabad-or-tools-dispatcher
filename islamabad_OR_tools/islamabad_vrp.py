import osmnx as ox
import networkx as nx
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

# ---------------------------------------------------------
# 1. OSMNX MAP DATA GENERATION (Your Code)
# ---------------------------------------------------------
locations = {
    0: (33.6842, 73.1624),  # Depot: Pakistan Monument
    1: (33.6894, 73.0708),  # Customer 1: Centaurus Mall
    2: (33.6920, 73.1200),  # Customer 2: Lok Virsa
    3: (33.5480, 73.1150),  # Customer 3: near Islamabad Airport
}

def snap_to_graph(G, lat, lon):
    return ox.nearest_nodes(G, lon, lat)

def distance_between_nodes(G, source, target):
    route = nx.shortest_path(G, source, target, weight="length")
    total_length = 0
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G[u][v][0]
        total_length += edge_data["length"]
    return total_length

def create_distance_matrix_islamabad():
    print("Downloading Islamabad road network (This may take a minute)...")
    G = ox.graph_from_place("Islamabad, Pakistan", network_type="drive")
    print(f"Downloaded graph with {len(G.nodes)} nodes and {len(G.edges)} edges")

    nodes = {}
    for i, (lat, lon) in locations.items():
        nodes[i] = snap_to_graph(G, lat, lon)

    num_locs = len(locations)
    dist_matrix = [[0.0] * num_locs for _ in range(num_locs)]

    print("Computing real-world distance matrix...")
    for i in range(num_locs):
        for j in range(num_locs):
            if i != j:
                meters = distance_between_nodes(G, nodes[i], nodes[j])
                dist_matrix[i][j] = meters / 1000.0  # Convert to km

    return dist_matrix

# ---------------------------------------------------------
# 2. OR-TOOLS SOLVER SETUP
# ---------------------------------------------------------
def create_data():
    # Dynamically generate the real distance matrix
    distance_matrix = create_distance_matrix_islamabad()

    return {
        'distance_matrix': distance_matrix,
        'demands': [0, 1, 2, 3],  # 0 demand at depot
        'vehicle_capacities': [4, 4], # Two vehicles, capacity 4
        'num_vehicles': 2,
        'depot': 0,
    }

def print_solution(data, manager, routing, solution):
    """Prints the final routed solution to the console."""
    print("\n--- OPTIMIZED ROUTES ---")
    # Divide objective by 1000 to convert back to km
    print(f"Total Fleet Distance: {solution.ObjectiveValue() / 1000.0:.2f} km\n")
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = f'Vehicle {vehicle_id} Route:\n'
        route_load = 0
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += f' Node {node_index} Load({route_load}) -> '
            index = solution.Value(routing.NextVar(index))
            
        node_index = manager.IndexToNode(index)
        plan_output += f' Node {node_index} Load({route_load})\n'
        print(plan_output)

def solve_vrp():
    data = create_data()
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    
    # Distance Callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Multiply float km by 1000 to satisfy the C++ integer requirement
        return int(data['distance_matrix'][from_node][to_node] * 1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Demand Callback & Capacity Dimension
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0, data['vehicle_capacities'], True, 'Capacity'
    )

    # Solve
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    
    print("\nOptimizing routes...")
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("No solution found!")

if __name__ == '__main__':
    solve_vrp()