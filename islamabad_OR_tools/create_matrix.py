import xgboost as xgb
import pandas as pd
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

# 1. The Matrix Generator
def create_time_matrix(distance_matrix, model):
    num_locations = len(distance_matrix)
    time_matrix = [[0.0] * num_locations for _ in range(num_locations)]
    print("AI is pre-calculating the Time Matrix...")
    for i in range(num_locations):
        for j in range(num_locations):
            if i == j:
                time_matrix[i][j] = 0.0
            else:
                features = pd.DataFrame([{
                    'distance_km': distance_matrix[i][j],
                    'hour_of_day': 18,        # 6 PM Rush Hour!
                    'day_of_week': 0,         # Monday
                    'is_raining': 1,          # Raining!
                    'road_qualities': 0,      # Bad Roads
                    'congestion_levels': 5,   # Heavy Traffic
                    'type_of_road': 0,
                    'checkpoints': 1
                }])
                time_matrix[i][j] = float(model.predict(features)[0])
    return time_matrix

def main():
    # 2. Setup the Data
    model = xgb.XGBRegressor()
    model.load_model('islamabad_traffic_model.json')
    
    # 5 locations in Islamabad (e.g., NUST, G-11, I-8, F-7, DHA)
    distance_matrix = [
        [0.0, 5.2, 8.1, 12.5, 15.0],
        [5.2, 0.0, 3.4, 9.8, 11.2],
        [8.1, 3.4, 0.0, 6.2, 8.5],
        [12.5, 9.8, 6.2, 0.0, 4.1],
        [15.0, 11.2, 8.5, 4.1, 0.0]
    ]
    
    time_matrix = create_time_matrix(distance_matrix, model)
    num_vehicles = 1
    depot = 0 # Starting at NUST

    # 3. Setup OR-Tools
    manager = pywrapcp.RoutingIndexManager(len(time_matrix), num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # ==========================================
    # THE FUSION CALLBACK
    def time_callback(from_index, to_index):
        # 1. Convert routing indices to matrix indices
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        
        # 2. Look up the AI's predicted minutes in time_matrix
        predicted_minutes = time_matrix[from_node][to_node]
        
        # 3. Convert minutes to seconds (multiply by 60) and cast to integer
        return int(predicted_minutes * 60)
    # ==========================================

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 4. Solve the Route
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    print("\nOR-Tools is calculating the fastest route using AI predictions...")
    solution = routing.SolveWithParameters(search_parameters)

    # 5. Print the Results
    if solution:
        print("\n--- OPTIMAL ROUTE FOUND ---")
        index = routing.Start(0)
        plan_output = 'Route:\n'
        route_time_seconds = 0
        
        while not routing.IsEnd(index):
            plan_output += f'Location {manager.IndexToNode(index)} -> '
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_time_seconds += routing.GetArcCostForVehicle(previous_index, index, 0)
            
        plan_output += f'Location {manager.IndexToNode(index)}\n'
        plan_output += f'Total ETA: {round(route_time_seconds / 60, 1)} minutes'
        print(plan_output)
    else:
        print("No solution found!")

if __name__ == "__main__":
    main()

