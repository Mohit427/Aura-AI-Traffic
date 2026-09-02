import os
import sys
import time
import json
import datetime
import requests
import psycopg2
import traci

# Locate the SUMO TraCI library
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Error: Please declare environment variable 'SUMO_HOME'")

# 1. Configuration
SUMO_CMD = ["sumo-gui", "-c", "osm.sumocfg"]
STATE_API_URL = "http://localhost:8000/api/sumo-state"

# Database Configuration (You will need to ask Mohit for the exact credentials/table name)
DB_CONFIG = {
    "dbname": "aura_db",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

def fetch_live_counts():
    """Queries the latest vision counts directly from PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Querying the latest row from Mohit's vision table
        # (Mohit might need to adjust the exact table/column names here)
        cur.execute("SELECT counts FROM vision_logs ORDER BY timestamp DESC LIMIT 1;")
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if row:
            return row[0] # Assuming the 'counts' column is a JSONB dictionary
    except Exception as e:
        pass # Fallback if DB connection fails
    
    return {"car": 7, "bus": 0, "person": 1}

def inject_live_traffic(step, counts):
    """Dynamically creates the route and spawns vehicles based on vision counts."""
    cars = counts.get("car", 0)
    
    if cars > 0 and step % 10 == 0:  
        veh_id = f"live_car_{step}"
        try:
            if "dynamic_north_south" not in traci.route.getIDList():
                traci.route.add("dynamic_north_south", ["1313198082", "1313198082.274"])
            
            traci.vehicle.add(veh_id, routeID="dynamic_north_south", typeID="DEFAULT_VEHTYPE")
        except traci.exceptions.TraCIException:
            pass 

def export_twin_state(step):
    """Exports queue and wait times to the backend API via POST."""
    edges_to_monitor = [
        "1313198082.274", # North approach stop line
        "1313198080.250", # South approach stop line
        "1110246916",     # East approach stop line
        "588357066"       # West approach stop line
    ]
    edge_data = []
    
    for edge_id in edges_to_monitor:
        try:
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

    payload = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "intersection_id": "vadapalani_junction",
        "sim_time_s": step,
        "edges": edge_data,
        "demand_profile": "medium"
    }
    
    # Print the data so you can see it on your own screen
    print(f"[{step}s] Metrics: {json.dumps(payload['edges'])}")
    
    # Send the payload directly to Mohit's endpoint
    try:
        requests.post(STATE_API_URL, json=payload, timeout=2)
    except requests.exceptions.RequestException:
        pass # Ignore the server error since he is on a different laptop

def run_digital_twin():
    """Runs the SUMO simulation and synchronizes with live data."""
    traci.start(SUMO_CMD)
    step = 0
    
    print("Starting AURA Digital Twin (Headless Mode)...")
    
    while step < 3600:
        traci.simulationStep()
        
        if step % 5 == 0:
            live_counts = fetch_live_counts()
            inject_live_traffic(step, live_counts)
            export_twin_state(step)
            
        step += 1
        time.sleep(0.1)

    traci.close()

if __name__ == "__main__":
    run_digital_twin()