import streamlit as st
import xgboost as xgb
import pandas as pd
import folium
import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from streamlit_folium import st_folium
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
import requests

# --- 1. INITIALIZE GEOCODER & SESSION STATE ---
geolocator = Nominatim(user_agent="islamabad_cvrp_pro")

if 'locations_db' not in st.session_state:
    st.session_state.locations_db = {
        "NUST H-12": [33.6425, 72.9915],
        "F-7 Markaz": [33.7297, 73.0553]
    }
if 'stops' not in st.session_state:
    st.session_state.stops = ["NUST H-12", "F-7 Markaz"]
# NEW: Memory for package demands!
if 'demands' not in st.session_state:
    st.session_state.demands = {"NUST H-12": 0, "F-7 Markaz": 5}

# --- 2. HELPERS ---
def get_road_geometry(coords1, coords2):
    lon1, lat1 = coords1[1], coords1[0]
    lon2, lat2 = coords2[1], coords2[0]
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        data = response.json()
        if data["code"] == "Ok":
            route_geometry = data["routes"][0]["geometry"]["coordinates"]
            return [[lat, lon] for lon, lat in route_geometry]
    except Exception:
        pass
    return [coords1, coords2]

def calculate_distance(coords1, coords2):
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return (R * c) * 1.3

# --- 3. LOAD AI MODEL ---
@st.cache_resource
def load_ai_model():
    model = xgb.XGBRegressor()
    try:
        model.load_model('islamabad_traffic_model.json')
        return model
    except:
        return None

model = load_ai_model()

# --- 4. STREAMLIT UI: SIDEBAR ---
st.title("📦 AI Fleet Dispatcher (Capacity Aware)")

st.sidebar.header("🔍 1. Add Customer Orders")
new_address = st.sidebar.text_input("Customer Address:")
# NEW: Input for how many packages this customer wants
packages = st.sidebar.number_input("Packages to Deliver", min_value=1, value=3)

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Geocode & Add"):
        if new_address and new_address not in st.session_state.stops:
            with st.spinner("Finding coordinates..."):
                try:
                    location = geolocator.geocode(f"{new_address}, Islamabad, Pakistan", timeout=5)
                    if location:
                        st.session_state.locations_db[new_address] = [location.latitude, location.longitude]
                        st.session_state.stops.append(new_address)
                        st.session_state.demands[new_address] = packages # Save the demand!
                        st.rerun()
                    else:
                        st.sidebar.error("Not found.")
                except GeocoderTimedOut:
                    st.sidebar.error("Service busy.")
with col2:
    if st.button("Clear All"):
        first_stop = st.session_state.stops[0]
        st.session_state.stops = [first_stop]
        st.session_state.locations_db = {first_stop: st.session_state.locations_db[first_stop]}
        st.session_state.demands = {first_stop: 0} # Reset demands
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. Fleet Constraints")
depot_stop = st.sidebar.selectbox("Starting Depot:", st.session_state.stops)
num_vehicles = st.sidebar.number_input("Number of Vehicles", min_value=1, max_value=10, value=2)
# NEW: Set the maximum physical capacity of the trucks
max_capacity = st.sidebar.number_input("Max Cargo per Vehicle", min_value=5, value=15)

st.sidebar.markdown("---")
st.sidebar.header("🌍 3. Live Conditions")
hour = st.sidebar.slider("Hour of Day", 0, 23, 18)
day = st.sidebar.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
day_mapping = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
weather = st.sidebar.radio("Weather", ["Clear", "Raining"])
is_raining = 1 if weather == "Raining" else 0
congestion = st.sidebar.slider("Congestion", 1, 5, 3)

# --- 5. ENGINE SOLVER LOGIC ---
def solve_routing():
    num_locations = len(st.session_state.stops)
    if num_locations < 2:
        return None, "Not enough stops."

    depot_index = st.session_state.stops.index(depot_stop)
    
    # Force the depot demand to be 0
    st.session_state.demands[depot_stop] = 0

    distance_matrix = [[0.0] * num_locations for _ in range(num_locations)]
    for i in range(num_locations):
        for j in range(num_locations):
            loc_i = st.session_state.stops[i]
            loc_j = st.session_state.stops[j]
            distance_matrix[i][j] = calculate_distance(st.session_state.locations_db[loc_i], st.session_state.locations_db[loc_j])

    time_matrix = [[0.0] * num_locations for _ in range(num_locations)]
    for i in range(num_locations):
        for j in range(num_locations):
            if i == j: continue
            features = pd.DataFrame([{
                'distance_km': distance_matrix[i][j],
                'hour_of_day': hour, 'day_of_week': day_mapping[day],
                'is_raining': is_raining, 'road_qualities': 1,
                'congestion_levels': congestion, 'type_of_road': 0, 'checkpoints': 0
            }])
            if model:
                time_matrix[i][j] = float(model.predict(features)[0])

    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot_index)
    routing = pywrapcp.RoutingModel(manager)
    
    # 1. TIME CALLBACK
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(time_matrix[from_node][to_node] * 60)

    transit_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)
    
    # 2. NEW: DEMAND CALLBACK (How heavy is the package at this stop?)
    demands_list = [st.session_state.demands[stop] for stop in st.session_state.stops]
    
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands_list[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    # 3. NEW: CAPACITY DIMENSION (Forbids overloading the truck)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [max_capacity] * num_vehicles,  # max capacity for each vehicle
        True,  # start cumul to zero
        'Capacity'
    )
    
    # Time dimension to balance workload
    routing.AddDimension(transit_index, 0, 100000, True, 'Time')
    time_dimension = routing.GetDimensionOrDie('Time')
    time_dimension.SetGlobalSpanCostCoefficient(100)
    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)
    
    if not solution:
        return None, "No solution found. (Check if a single order is larger than the Max Cargo capacity!)"

    # Parse Routes for MULTIPLE Vehicles
    all_routes = []
    total_time_seconds = 0
    
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        plan_output = []
        route_load = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            stop_name = st.session_state.stops[node]
            route_load += st.session_state.demands[stop_name]
            plan_output.append({"name": stop_name, "load": route_load})
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            total_time_seconds += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
        plan_output.append({"name": st.session_state.stops[manager.IndexToNode(index)], "load": route_load})
        
        if len(plan_output) > 2:
            all_routes.append(plan_output)
                
    return all_routes, round(total_time_seconds / 60, 1)

# --- 6. RENDER DASHBOARD ---
if len(st.session_state.stops) >= 2:
    result = solve_routing()
    
    if result[0] is None:
        st.error(result[1]) # Show error if trucks are overloaded
    else:
        all_routes, total_eta = result
        st.success(f"**Total Fleet AI Predicted ETA:** {total_eta} minutes")
        
        m = folium.Map(location=st.session_state.locations_db[depot_stop], zoom_start=12)
        colors = ["red", "purple", "orange", "darkblue", "green", "pink", "lightblue", "black"]

        for i, route_sequence in enumerate(all_routes):
            v_color = colors[i % len(colors)]
            
            # Create a string showing the stops and cargo load
            route_str = ' ➡️ '.join([f"{stop['name']} (Load: {stop['load']})" for stop in route_sequence])
            st.write(f"**Truck {i+1} [Cargo Route]:** {route_str}")
            
            # Draw OSRM roads
            for j in range(len(route_sequence) - 1):
                start_node = st.session_state.locations_db[route_sequence[j]["name"]]
                end_node = st.session_state.locations_db[route_sequence[j+1]["name"]]
                road_curves = get_road_geometry(start_node, end_node)
                dash_array = "10, 10" if j == len(route_sequence) - 2 else None
                folium.PolyLine(road_curves, color=v_color, weight=5, opacity=0.8, dash_array=dash_array).add_to(m)

        for stop_name in st.session_state.stops:
            coords = st.session_state.locations_db[stop_name]
            marker_color = "black" if stop_name == depot_stop else "blue"
            
            # Show the package demand in the map popup!
            demand = st.session_state.demands[stop_name]
            popup_text = f"{stop_name} (Demand: {demand} pkgs)" if stop_name != depot_stop else f"{stop_name} (Depot)"
            
            folium.Marker(
                location=coords, popup=popup_text, tooltip=popup_text,
                icon=folium.Icon(color=marker_color, icon="star" if stop_name == depot_stop else "info-sign")
            ).add_to(m)

        st_folium(m, width=700, height=500)
else:
    st.info("👈 Add destinations using the sidebar to begin routing.")