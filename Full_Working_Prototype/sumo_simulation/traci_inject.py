import os
import sys
import time
import json
import datetime
import traci

# Locate the SUMO TraCI library
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Error: Please declare environment variable 'SUMO_HOME'")

# 1. Configuration
SUMO_CMD = ["sumo", "-c", "osm.sumocfg"]

def fetch_live_counts():
    """
    Reads live vision counts from standard input (stdin).
    Mohit's backend can pipe the JSON string directly into this script via subprocess.
    """
    # Check if data is being piped in. If running standalone, use fallback.
    if not sys.stdin.isatty():
        try:
            line = sys.stdin.readline()
            if line:
                data = json.loads(line)
                return data.get("counts", {})
        except Exception:
            pass
    return {"car": 2, "bus": 0, "person": 5}

def inject_live_traffic(step, counts):
    """Dynamically creates the route and spawns vehicles based on vision counts."""
    cars = counts.get("car", 0)
    
    if cars > 0 and step % 10 == 0:  
        veh_id = f"live_car_{step}"
        try:
            # Point 4 Fix: Dynamically create the route using your pre-split and post-split IDs
            if "dynamic_north_south" not in traci.route.getIDList():
                traci.route.add("dynamic_north_south", ["1313198082", "1313198082.274"])
            
            traci.vehicle.add(veh_id, routeID="dynamic_north_south", typeID="DEFAULT_VEHTYPE")
        except traci.exceptions.TraCIException:
            pass 

def export_twin_state(step):
    """Exports queue and wait times for all 4 intersection approaches."""
    # Points 2 & 3 Fix: Monitoring all 4 approaches using your exact split IDs
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
    
    # stdout output for Mohit's backend to capture. Flushed immediately to prevent buffer lag.
    sys.stdout.write(f"TWIN_STATE_EXPORT: {json.dumps(payload)}\n")
    sys.stdout.flush()

def run_digital_twin():
    """Runs the SUMO simulation and synchronizes with live data."""
    traci.start(SUMO_CMD)
    step = 0
    
    sys.stdout.write("Starting AURA Digital Twin (Headless Mode)...\n")
    sys.stdout.flush()
    
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