import pandas as pd
import numpy as np
import random

def generate_traffic_data(num_records=5000):
    print(f"Generating {num_records} historical trip records for Islamabad...")
    
    np.random.seed(42)
    random.seed(42)
    
    # 1. Generate random base features
    distances_km = np.random.uniform(1.0, 30.0, num_records) # Trips between 1km and 30km
    hours_of_day = np.random.randint(6, 23, num_records)     # Trips between 6 AM and 11 PM
    days_of_week = np.random.randint(0, 7, num_records)      # 0 = Monday, 6 = Sunday
    
    
    # 0 = Clear, 1 = Rain (15% chance of rain)
    weather_conditions = np.random.choice([0, 1], num_records, p=[0.85, 0.15]) 
    
    # NEW FEATURES
    # Congestion level from 1 (empty) to 5 (bumper-to-bumper)
    congestion_levels = np.random.randint(1, 6, num_records)
    
    # 0 = Potholes (10%), 1 = Normal (60%), 2 = Perfect (30%)
    road_qualities = np.random.choice([0, 1, 2], num_records, p=[0.10, 0.60, 0.30])
    
    # 1 = Highway (15%), 0 = Sector Roads (85%)
    is_highway = np.random.choice([0, 1], num_records, p=[0.85, 0.15])
    
    # Number of police checkpoints (0 to 4)
    checkpoints = np.random.choice([0, 1, 2, 3, 4], num_records)
    
    travel_times = []
    
    # 2. Apply realistic traffic logic to calculate the target variable (travel time)
    for i in range(num_records):
        dist = distances_km[i]
        hour = hours_of_day[i]
        day = days_of_week[i]
        weather = weather_conditions[i]
        
        # Base time assuming ideal conditions (approx 40 km/h -> 1.5 mins per km)
        base_time_mins = dist * 1.5 
        
        # Traffic Multipliers
        multiplier = 1.0
        #type of road
        if is_highway[i] == 1:
            multiplier -= 0.30
        #road quality 
        if road_qualities[i] == 0:
            multiplier += 0.20
        elif road_qualities[i] == 2:
            multiplier -= 0.10

        #cogestion level
        multiplier += (congestion_levels[i] - 1) * 0.10
        # Morning Rush (8 AM - 10 AM) and Evening Rush (5 PM - 7 PM)
        if (8 <= hour <= 10) or (17 <= hour <= 19):
            # Rush hour is bad on weekdays, mild on weekends
            if day < 5: 
                multiplier += np.random.uniform(0.5, 1.2) # Adds 50% to 120% more time
            else:
                multiplier += np.random.uniform(0.1, 0.3)
                
        # Rain slows things down drastically in Islamabad
        if weather == 1:
            multiplier += np.random.uniform(0.3, 0.6)
            
        # Add a little bit of random real-world noise (red lights, minor delays)
        noise = np.random.uniform(0.9, 1.1)
        
        final_time = (base_time_mins * multiplier * noise) + (checkpoints[i] * 2.0)
        final_time = max(final_time, dist * 0.5) 
        travel_times.append(round(final_time, 2))

    # 3. Package it into a DataFrame and save to CSV
    df = pd.DataFrame({
        'distance_km': np.round(distances_km, 2),
        'hour_of_day': hours_of_day,
        'day_of_week': days_of_week,
        'is_raining': weather_conditions,
        'travel_time_minutes': travel_times,
        'road_qualities':road_qualities,
        'congestion_levels':congestion_levels,
        'road_qualities':road_qualities,
        'type_of_road':is_highway,
        'checkpoints':checkpoints,
    })
    
    df.to_csv('islamabad_traffic_data.csv', index=False)
    print("Data generation complete! Saved to 'islamabad_traffic_data.csv'.")
    print("\nPreview of the data:")
    print(df.head())

if __name__ == "__main__":
    generate_traffic_data()