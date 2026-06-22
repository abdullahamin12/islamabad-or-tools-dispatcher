import datetime
import requests

def get_live_conditions():
    print("📡 Fetching live data for Islamabad...")

    # 1. Get Live Time
    now = datetime.datetime.now()
    hour_of_day = now.hour
    day_of_week = now.weekday() # In Python, Monday is 0, Sunday is 6

    # 2. Get Live Weather (Islamabad Coordinates)
    url = "https://api.open-meteo.com/v1/forecast?latitude=33.6844&longitude=73.0479&current=precipitation"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Check if precipitation is greater than 0mm
        precipitation = data['current']['precipitation']
        is_raining = 1 if precipitation > 0 else 0
        
    except Exception as e:
        print("Failed to get weather. Defaulting to clear weather.")
        is_raining = 0
        precipitation = 0

    print("\n--- CURRENT CONDITIONS ---")
    print(f"Hour of Day: {hour_of_day}")
    print(f"Day of Week: {day_of_week}")
    print(f"Is Raining:  {is_raining} ({precipitation}mm detected)")
    
    return hour_of_day, day_of_week, is_raining

if __name__ == "__main__":
    get_live_conditions()