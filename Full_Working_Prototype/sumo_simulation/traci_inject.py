import traci
import requests
import time
import json
import datetime

# 1. Configuration
BACKEND_URL = "http://localhost:8000/api/vision/latest"
SUMO_CMD = ["sumo", "-c", "osm.sumocfg"]

def fetch_live_counts():
    """Fetches the real-time YOLOv8 counts from the backend."""
    try:
        response = requests.get(BACKEND_URL)
        data = response.json()
        return data.get("counts", {})
    except Exception as e:
        # Fallback matching Shruti's exact data contract
        return {"car": 2, "bus": 0, "person": 5}

def inject_live_traffic(step, counts):
    """Translates JSON counts into TraCI spawn commands."""
    cars = counts.get("car", 0)
    
    if cars > 0 and step % 10 == 0:  
        veh_id = f"live_car_{step}"
        try:
            traci.vehicle.add(veh_id, "route_north_south", typeID="DEFAULT_VEHTYPE")
        except traci.exceptions.TraCIException:
            pass 

def export_twin_state(step):
    """Extracts live graph state from SUMO and formats it to the Data Contract."""
    # Using the North and East approach edge IDs from your map
    edges_to_monitor = ["1313198082", "1110246916"]
    edge_data = []
    
    for edge_id in edges_to_monitor:
        try:
            # Yashvant's requested TraCI functions to get the edge state
            queue = traci.edge.getLastStepVehicleNumber(edge_id)
            occupancy = traci.edge.getLastStepOccupancy(edge_id)
            wait_time = traci.edge.getWaitingTime(edge_id)
            
            edge_data.append({
                "edge_id": edge_id,
                "queue_length": queue,
                "occupancy_ratio": round(occupancy, 2),
                "avg_wait_time_s": round(wait_time, 2)
            })
        except traci.exceptions.TraCIException:
            pass

    # Build the exact JSON schema defined in CONTRACTS.md
    payload = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "intersection_id": "vadapalani_junction",
        "sim_time_s": step,
        "edges": edge_data,
        "demand_profile": "medium"
    }
    
    # Print the JSON payload so Mohit's backend can capture it from the console
    print(f"TWIN_STATE_EXPORT: {json.dumps(payload)}")

def run_digital_twin():
    """Runs the SUMO simulation and synchronizes with live data."""
    traci.start(SUMO_CMD)
    step = 0
    
    print("Starting AURA Digital Twin (Headless Mode)...")
    
    while step < 3600:
        traci.simulationStep()
        
        # Poll vision data and export SUMO state every 5 simulation seconds
        if step % 5 == 0:
            live_counts = fetch_live_counts()
            inject_live_traffic(step, live_counts)
            export_twin_state(step)
            
        step += 1
        time.sleep(0.1)

    traci.close()

if __name__ == "__main__":
    run_digital_twin()