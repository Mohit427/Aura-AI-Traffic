import os
import sys
import requests
from datetime import datetime, timezone

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Error: Please declare environment variable 'SUMO_HOME'")

import traci

sumoCmd = ["sumo", "-c", "osm.sumocfg"]
BACKEND_URL = "http://127.0.0.1:8000/api/sumo-state"
INTERSECTION_ID = "vadapalani_junction"

EDGE_MAP = {
    "north_approach": "1313198082.274",
    "south_approach": "1313198080.250",
    "east_approach": "1110246916",
    "west_approach": "588357066",
}

def get_demand_profile(total_vehicles):
    if total_vehicles >= 40:
        return "heavy"
    elif total_vehicles >= 15:
        return "medium"
    return "light"

def post_state(step):
    edges_payload = []
    total_vehicles = 0

    for edge_name, edge_id in EDGE_MAP.items():
        try:
            queue_length = traci.edge.getLastStepVehicleNumber(edge_id)
            occupancy_ratio = round(traci.edge.getLastStepOccupancy(edge_id), 2)
            avg_wait_time_s = round(traci.edge.getWaitingTime(edge_id), 1)
        except traci.exceptions.TraCIException:
            print(f"WARNING: edge_id '{edge_id}' ({edge_name}) not found in network -- skipping")
            continue

        total_vehicles += queue_length
        edges_payload.append({
            "edge_id": edge_name,
            "queue_length": queue_length,
            "occupancy_ratio": occupancy_ratio,
            "avg_wait_time_s": avg_wait_time_s
        })

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "intersection_id": INTERSECTION_ID,
        "sim_time_s": float(step),
        "edges": edges_payload,
        "demand_profile": get_demand_profile(total_vehicles)
    }

    try:
        response = requests.post(BACKEND_URL, json=payload)
        print(f"Step {step}: posted state, status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Step {step}: backend not reachable -- is uvicorn running?")

def run_simulation():
    print("Starting headless SUMO simulation...")
    traci.start(sumoCmd)
    step = 0
    while step < 100:
        traci.simulationStep()

        if step == 10:
            traci.route.add("mock_route", ["1313198082.274", "1313198080.250"])
            traci.vehicle.add("mock_car_1", routeID="mock_route")
            print("Injected mock vehicle 'mock_car_1' onto the North approach.")

        if step % 5 == 0:
            post_state(step)

        step += 1

    traci.close()
    print("Simulation complete and closed cleanly.")

if __name__ == "__main__":
    run_simulation()
