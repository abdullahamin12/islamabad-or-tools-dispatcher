import xgboost as xgb
import pandas as pd

def create_time_matrix(distance_matrix, model):
    num_locations = len(distance_matrix)
    
    # Create an empty grid of zeros to hold our AI's time predictions
    time_matrix = [[0.0 for _ in range(num_locations)] for _ in range(num_locations)]
    
    print("Asking the AI to predict travel times for all routes...")
    
    # ==========================================
    # Predict travel times for every route in the distance matrix.
    for i in range(num_locations):
        for j in range(num_locations):
            if i == j:
                time_matrix[i][j] = 0.0
            else:
                features = pd.DataFrame([{
                    'distance_km': distance_matrix[i][j],
                    'hour_of_day': 14,
                    'day_of_week': 1,
                    'is_raining': 0,
                    'road_qualities': 1,
                    'congestion_levels': 2,
                    'type_of_road': 0,
                    'checkpoints': 0
                }])
                time_matrix[i][j] = float(model.predict(features)[0])
    # ==========================================

    return time_matrix

def main():
    # 1. Load the Brain
    model = xgb.XGBRegressor()
    model.load_model('islamabad_traffic_model.json')
    
    # 2. Our fake Distance Matrix (in kilometers)
    distance_matrix = [
        [0.0, 5.2, 8.1, 12.5],
        [5.2, 0.0, 3.4, 9.8],
        [8.1, 3.4, 0.0, 6.2],
        [12.5, 9.8, 6.2, 0.0]
    ]
    
    # 3. Build the Time Matrix
    time_matrix = create_time_matrix(distance_matrix, model)
    
    # 4. Print the final Time Matrix
    print("\nFinal AI-Predicted Time Matrix (Minutes):")
    for row in time_matrix:
        # Rounding to 1 decimal place so it's easy to read
        print([round(time, 1) for time in row])

if __name__ == "__main__":
    main()