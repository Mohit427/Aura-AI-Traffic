import traci
import requests
import time

# 1. Configuration
BACKEND_URL = "http://localhost:8000/api/vision/latest"  # Mohit's FastAPI endpoint
SUMO_CMD = ["sumo", "-c", "osm.sumocfg"]  # Uses "sumo" for headless mode instead of "sumo-gui"

def fetch_live_counts():
    """Fetches the real-time YOLOv8 counts from the backend."""
    try:
        response = requests.get(BACKEND_URL)
        data = response.json()
        return data.get("counts", {})
    except Exception as e:
        print(f"Waiting for backend... using fallback data.")
        # Fallback matching Shruti's exact data contract
        return {"car": 2, "bus": 0, "person": 5}

def inject_live_traffic(step, counts):
    """Translates JSON counts into TraCI spawn commands."""
    cars = counts.get("car", 0)
    
    # Spawn a vehicle if the vision model detects one
    if cars > 0 and step % 10 == 0:  
        veh_id = f"live_car_{step}"
        try:
            # We will use the North-South route as our initial injection path
            traci.vehicle.add(veh_id, "route_north_south", typeID="DEFAULT_VEHTYPE")
            print(f"[{step}s] Injected live vehicle: {veh_id}")
        except traci.exceptions.TraCIException as e:
            pass # Ignore if the vehicle ID already exists

def run_digital_twin():
    """Runs the SUMO simulation and synchronizes with live data."""
    traci.start(SUMO_CMD)
    step = 0
    
    print("Starting AURA Digital Twin (Headless Mode)...")
    
    while step < 3600:
        traci.simulationStep()
        
        # Poll the backend every 5 simulation seconds
        if step % 5 == 0:
            live_counts = fetch_live_counts()
            inject_live_traffic(step, live_counts)
            
        step += 1
        time.sleep(0.1)  # Pace the loop to simulate near-real-time

    traci.close()

if __name__ == "__main__":
    run_digital_twin()