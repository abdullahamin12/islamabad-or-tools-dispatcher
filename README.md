# 🚀 Mini Dispatcher UI for OR-Tools with AI-Based Delivery-Time Estimation

<div align="center">
  <p><strong>Smart Route Optimization for Islamabad | OR-Tools + XGBoost + Streamlit</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/OR-Tools-9.x-green.svg" alt="OR-Tools">
    <img src="https://img.shields.io/badge/XGBoost-1.x-orange.svg" alt="XGBoost">
    <img src="https://img.shields.io/badge/Streamlit-1.x-red.svg" alt="Streamlit">
  </p>
  <p><strong>Author:</strong> Abdullah Amin</p>
</div>

---

## 📖 Overview

Modern logistics optimization in 2026 requires a sophisticated interplay between **algorithmic efficiency** and **real-time operational awareness**. This project bridges the functional gap between raw mathematical solvers (Google OR-Tools) and comprehensive enterprise solutions like **AWS Intelligent Route Optimization**.

### 🎯 What This Project Does

- ✅ Solves **Capacitated Vehicle Routing Problem (CVRP)** using Google OR-Tools
- ✅ Integrates **real-world road networks** for Islamabad via OSRM + OSMnx
- ✅ Predicts **traffic-aware delivery times** using XGBoost ML model
- ✅ Provides an **interactive web UI** with Streamlit + Folium mapping
- ✅ **Dynamic geocoding** - type any location name (e.g., "Centaurus Mall") and get coordinates automatically

---
┌─────────────────────────────────────────────────────────────┐
│ USER INTERFACE (Streamlit) │
└──────────────────────────┬──────────────────────────────────┘
│
┌──────────────────────────▼──────────────────────────────────┐
│ LIVE SENSORS & PARAMETERS │
│ (Time, Weather, Congestion, Traffic) │
└──────────────────────────┬──────────────────────────────────┘
│
┌──────────────────────────▼──────────────────────────────────┐
│ AI BRAIN (XGBoost) │
│ Traffic-Aware Travel-Time Matrix Generator │
└──────────────────────────┬──────────────────────────────────┘
│
┌──────────────────────────▼──────────────────────────────────┐
│ CONSTRAINT SOLVER (OR-Tools) │
│ Integer Callback Engine (CVRP) │
└──────────────────────────┬──────────────────────────────────┘
│
┌──────────────────────────▼──────────────────────────────────┐
│ GEOGRAPHIC MAPPING & VISUALIZATION (Folium) │
│ Interactive Route Canvas │
└─────────────────────────────────────────────────────────────┘

text

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

```bash
# 1. Create project folder
mkdir islamabad_or_tools_dispatcher
cd islamabad_or_tools_dispatcher

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install ortools xgboost streamlit folium osmnx networkx scikit-learn geopy pandas numpy
```

### Running the Application

```bash
# Run the Streamlit web app
streamlit run app.py

# Or run the VRP solver directly
python islamabad_vrp_solver.py
```

---

## 📁 Project Structure
islamabad_or_tools_dispatcher/
│
├── app.py # Streamlit web frontend with mapping
├── islamabad_vrp_solver.py # Core OR-Tools CVRP solver (real roads)
├── basic_vrp.py # Basic VRP with fake distances (learning)
├── roads_test.py # OSRM + OSMnx road network test
├── islamabad_vrp.py # Distance matrix generator from OSMnx
│
├── data_generator.py # Synthetic traffic data generator
├── train_model.py # XGBoost model trainer
├── live_sensors.py # Open-Meteo weather API connector
│
├── .gitignore # Git ignore file
├── README.md # This file
└── requirements.txt # Python dependencies


---

## 🔧 Features

### 1. Routing Core (CVRP)
- Solves **Capacitated Vehicle Routing Problem**
- Each vehicle has capacity limits
- Total demand on route ≤ vehicle capacity
- Minimizes total travel distance/time

### 2. Real Road Integration
- **OSMnx**: Downloads Islamabad road network from OpenStreetMap
- **OSRM**: Computes real road distances (not geometric)
- Converts location names → coordinates → road nodes
- Distance matrix based on actual road topology

### 3. AI Delivery-Time Estimation
- **XGBoost Regressor** for traffic-aware ETA
- Trained on synthetic Islamabad traffic data
- Factors: time of day, weather, congestion
- Fast inference for OR-Tools callback loops

### 4. Web Dispatcher Interface
- **Streamlit**: Interactive web frontend
- **Folium**: Interactive map with route visualization
- Real-time parameters (weather, time, traffic)
- Click "Optimize" → see routes instantly

### 5. Dynamic Geocoding Pipeline
- **geopy** + **OpenStreetMap Nominatim API**
- Type any location name → get lat/lon coordinates
- Auto-calculates Haversine distance
- Updates AI matrix on the fly

---

## 🎯 Example Usage

### Running the VRP Solver

```python
# Run islamabad_vrp_solver.py

# Output:
Total distance: 85.0 km
Vehicle 0 route: ['Pakistan Monument (Depot)', 'Lok Virsa', 'Pakistan Monument (Depot)'] (load: 2)
Vehicle 1 route: ['Pakistan Monument (Depot)', 'Centaurus Mall', 'Near Islamabad Airport', 'Pakistan Monument (Depot)'] (load: 4)
```

### Running the Streamlit App

```bash
streamlit run app.py
```

Then in your browser:
1. Open `http://localhost:8501`
2. Enter location names (e.g., "Centaurus Mall")
3. Set vehicle capacities and demands
4. Click "Optimize Routes"
5. See routes on interactive map

---

## 📊 Key Findings

### Capacity-Distance Relationship

| Capacity | Total Distance | Observation |
|----------|---------------|-------------|
| [3, 3]   | 100 km        | Tighter → distance **increases** |
| [4, 4]   | 85 km         | Optimal |
| [5, 5]   | 85 km         | Looser → distance **decreases/stays** |

### Infeasibility Threshold
- If **any single demand > vehicle capacity** → solver returns **"No solution found"**
- OR-Tools cannot isolate or bypass problematic nodes
- Strict boundary conditions of mathematical optimization

### ML Strategy: Why XGBoost?
1. **Speed**: Matrix generation must be **instantaneous** for OR-Tools callbacks
2. **Tabular Standard**: CSV/SQL datasets → XGBoost is industry standard for accuracy

---

## 🛠️ Technologies Used

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Solver** | Google OR-Tools 9.x | CVRP constraint optimization |
| **ML** | XGBoost 1.x | Traffic-aware ETA prediction |
| **UI** | Streamlit 1.x | Web frontend |
| **Mapping** | Folium 0.x | Interactive route visualization |
| **Roads** | OSMnx 2.x, OSRM | Real road network from OpenStreetMap |
| **Geocoding** | geopy 2.x | Location name → coordinates |
| **Network** | NetworkX 3.x | Shortest path computation |
| **Data** | pandas, numpy | Data processing |
| **ML Utils** | scikit-learn | Preprocessing, metrics |

---

## 🧪 Testing & Stress Results

### Test 1: Capacity Tightening
```python
vehicle_capacities =   # Was[1][2]
# Result: Distance increases from 85 → 100 km
```

### Test 2: Demand Shift
```python
demands =   # Was[2][3][4][1]
# Result: Load changes, but routes stay identical (stable boundary)
```

### Test 3: Infeasibility
```python
demands =   # Customer 3 demand > capacity 4[3][4][5]
# Result: "No solution found" (problem infeasible)
```

---

## ⚠️ Limitations

### 1. Cold-Start Data Problem
- OR-Tools and VROOM are algorithmically robust but lack **proprietary telemetry** from Uber/Google
- Production needs: **ePOD workflows** + **mobile telemetry** integration

### 2. Synthetic Training Data
- Current data: **rule-based simulations** for Islamabad traffic
- Future: **backpropagation telemetry loop** with real rider data

### 3. Free Geocoder Limits
- **Nominatim rate-limiting**: 1 request/second
- Vulnerable to **user typos**
- Commercial platforms use **proprietary autocomplete engines** (Google Places API) for robust coordinate snapping

---

## 🔮 Future Roadmap

### Phase 1 (Done)
- ✅ CVRP with OR-Tools
- ✅ Real roads (OSMnx + OSRM)
- ✅ XGBoost ETA model
- ✅ Streamlit + Folium UI
- ✅ Dynamic geocoding (geopy + Nominatim)

### Phase 2 (Next)
- ⏳ Real rider telemetry integration
- ⏳ ePOD (Electronic Proof of Delivery)
- ⏳ Mobile driver app
- ⏳ Google Places API for robust geocoding
- ⏳ Multi-vehicle-type support (heterogeneous fleets)

### Phase 3 (Long-term)
- ⏳ AWS Intelligent Route Optimization parity
- ⏳ Real-time traffic API integration
- ⏳ Production-grade deployment
- ⏳ Backpropagation data loop

---

## 📚 References

- **Google OR-Tools**: [https://developers.google.com/optimization/](https://developers.google.com/optimization/)
- **VROOM**: [https://github.com/VROOM-Project/vroom](https://github.com/VROOM-Project/vroom)
- **AWS Intelligent Route Optimization**: [AWS Docs](https://docs.aws.amazon.com/solutions/intelligent-route-optimization-on-aws/)
- **OSMnx**: [GitHub](https://github.com/gbondar/osmnx)
- **XGBoost**: [https://xgboost.readthedocs.io/](https://xgboost.readthedocs.io/)
- **Streamlit**: [https://streamlit.io/](https://streamlit.io/)

---

## 📄 License

This project is for educational purposes. OR-Tools and other dependencies have their own licenses.

---

## 👤 Author

**Abdullah Amin**  
- Course/Project: OR-Tools based route optimization for Islamabad  
- Year: 2026

---

<div align="center">
  <p><strong>🚀 Built with ❤️ using OR-Tools + XGBoost + Streamlit</strong></p>
  <p>From raw math to operational logistics</p>
</div>

## 🏗️ Architecture
