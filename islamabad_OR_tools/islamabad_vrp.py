import osmnx as ox
import networkx as nx
import math

# 1. Define 4 locations (lat, lon) in Islamabad
# index 0 = depot, 1,2,3 = customers
locations = {
    0: (33.6842, 73.1624),  # Depot: Pakistan Monument
    1: (33.6894, 73.0708),  # Customer 1: Centaurus Mall
    2: (33.6920, 73.1200),  # Customer 2: Lok Virsa
    3: (33.5480, 73.1150),  # Customer 3: near Islamabad Airport
}

def snap_to_graph(G, lat, lon):
    """Snap a (lat, lon) point to the nearest node in the graph."""
    node = ox.nearest_nodes(G, lon, lat)
    return node

def distance_between_nodes(G, source, target):
    """Compute shortest path distance (in meters) between two nodes."""
    # Use 'length' as weight (edge length in meters)
    route = nx.shortest_path(G, source, target, weight="length")
    total_length = 0
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G[u][v][0]
        total_length += edge_data["length"]
    return total_length  # meters

def create_distance_matrix_islamabad():
    # Download Islamabad road network
    print("Downloading Islamabad road network...")
    G = ox.graph_from_place("Islamabad, Pakistan", network_type="drive")
    print("Downloaded graph with", len(G.nodes), "nodes and", len(G.edges), "edges")

    # Snap each location to nearest node
    nodes = {}
    for i, (lat, lon) in locations.items():
        nodes[i] = snap_to_graph(G, lat, lon)
        print(f"Location {i} (lat={lat}, lon={lon}) snapped to node {nodes[i]}")

    # Create distance matrix (in km)
    num_locs = len(locations)
    dist_matrix = [[0.0] * num_locs for _ in range(num_locs)]

    print("Computing distance matrix...")
    for i in range(num_locs):
        for j in range(num_locs):
            if i == j:
                dist_matrix[i][j] = 0.0
            else:
                meters = distance_between_nodes(G, nodes[i], nodes[j])
                dist_matrix[i][j] = meters / 1000.0  # km

    print("\nDistance matrix (km):")
    for row in dist_matrix:
        print(row)

    return dist_matrix

def main():
    dist_matrix = create_distance_matrix_islamabad()

    # Just print it for now; we will use it in OR-Tools later
    print("\nYou can now use this distance matrix in your OR-Tools VRP.")

if __name__ == "__main__":
    main()