import xgboost as xgb 
import pandas as pd
model = xgb.XGBRegressor()
model.load_model('islamabad_traffic_model.json')
#test question to check whether model is running 
# Example format:
trip_data = pd.DataFrame({
    'distance_km': [18.5],
    'hour_of_day': [18],
    'day_of_week': [0],
    'is_raining': [1],
    'road_qualities': [0],      # Moved this UP
    'congestion_levels': [5],   # Moved this DOWN
    'type_of_road': [0],
    'checkpoints': [3]
})
predicted_minutes = model.predict(trip_data)[0]
print(predicted_minutes)