import xgboost as xgb
import pandas as pd
import requests
import datetime
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

# 1. The Live Sensor
def get_live_conditions():
    print("📡 Fetching live data for Islamabad...")
    now = datetime.datetime.now()
    hour_of_day = now.hour
    day_of_week = now.weekday() 

    url = "https://api.open-meteo.com/v1/forecast?latitude=33.6844&longitude=73.0479&current=precipitation"
    try:
        response = requests.get(url)
        data = response.json()
        precipitation = data['current']['precipitation']
        is_raining = 1 if precipitation > 0 else 0
    except Exception:
        print("⚠️ Failed to get weather. Defaulting to clear.")
        is_raining = 0

    print(f"-> Conditions: Hour {hour_of_day}, Day {day_of_week}, Raining: {'Yes' if is_raining else 'No'}")
    return hour_of_day, day_of_week, is_raining

# 2. The AI Matrix Generator (Now accepts LIVE data)
def create_time_matrix(distance_matrix, model, live_hour, live_day, live_rain):
    num_locations = len(distance_matrix)
    time_matrix = [[0.0] * num_locations for _ in range(num_locations)]
    print("\n🧠 AI is pre-calculating ETAs based on LIVE conditions...")
    
    for i in range(num_locations):
        for j in range(num_locations):
            if i == j:
                time_matrix[i][j] = 0.0
            else:
                features = pd.DataFrame([{
                    'distance_km': distance_matrix[i][j],
                    'hour_of_day': live_hour,      # LIVE!
                    'day_of_week': live_day,       # LIVE!
                    'is_raining': live_rain,       # LIVE!
                    'road_qualities': 1,           # Normal roads
                    'congestion_levels': 3,        # Moderate traffic
                    'type_of_road': 0,
                    'checkpoints': 1
                }])
                time_matrix[i][j] = float(model.predict(features)[0])
    return time_matrix

def main():
    # Fetch live data first
    live_hour, live_day, live_rain = get_live_conditions()

    # Load Brain
    model = xgb.XGBRegressor()
    model.load_model('islamabad_traffic_model.json')
    
    # Distance Matrix
    distance_matrix = [
        [0.0, 5.2, 8.1, 12.5, 15.0],
        [5.2, 0.0, 3.4, 9.8, 11.2],
        [8.1, 3.4, 0.0, 6.2, 8.5],
        [12.5, 9.8, 6.2, 0.0, 4.1],
        [15.0, 11.2, 8.5, 4.1, 0.0]
    ]
    
    # Generate Matrix with Live Data
    time_matrix = create_time_matrix(distance_matrix, model, live_hour, live_day, live_rain)
    
    # Setup OR-Tools
    manager = pywrapcp.RoutingIndexManager(len(time_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(time_matrix[from_node][to_node] * 60)

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    print("🚚 OR-Tools is solving the route...")
    solution = routing.SolveWithParameters(search_parameters)

    # Print Results
    if solution:
        print("\n--- OPTIMAL LIVE ROUTE FOUND ---")
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

if __name__ == "__main__":
    main()