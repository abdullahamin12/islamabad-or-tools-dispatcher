import osmnx as ox
import networkx as nx

def main():
    # 1. Download road network for Islamabad (driving network)
    print("Downloading Islamabad road network...")
    G = ox.graph_from_place("Islamabad, Pakistan", network_type="drive")
    print("Downloaded graph with", len(G.nodes), "nodes and", len(G.edges), "edges")

    # 2. Pick two random nodes from the graph
    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[100]  # just pick another node

    print("Source node:", source)
    print("Target node:", target)

    # 3. Compute shortest path by travel time or length
    # First, add edge speeds and travel times if not present
    G = ox.add_edge_speeds(G)        # adds 'speed_kph' to edges
    G = ox.add_edge_travel_times(G)  # adds 'travel_time' (seconds) to edges

    # Shortest path by travel_time
    route = nx.shortest_path(G, source, target, weight="travel_time")
    print("Route length (nodes):", len(route))

    # 4. Compute total travel time along this route
    total_travel_time = 0
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G[u][v][0]  # first edge between u and v
        total_travel_time += edge_data["travel_time"]

    print("Estimated travel time (seconds):", round(total_travel_time, 1))
    print("Estimated travel time (minutes):", round(total_travel_time / 60, 1))

if __name__ == "__main__":
    main()