import subprocess
import json

EXE_PATH = r"Full_Working_Prototype/engine/Debug/edmonds_karp.exe"

def parse_sumo_twin_state(twin_payload):
    """Maps Tharanesh's edge queue lengths to directional counts."""
    edge_map = {edge["edge_id"]: edge["queue_length"] for edge in twin_payload.get("edges", [])}
    
    # Map Tharanesh's OSM edge IDs to directional car counts
    north_cars = str(edge_map.get("1313198082", 20))
    south_cars = str(edge_map.get("1313198080.250", 18))
    east_cars = str(edge_map.get("1110246916", 25))
    west_cars = str(edge_map.get("588357066", 15))
    
    return [north_cars, south_cars, east_cars, west_cars]

def run_engine_test(scenario_name, twin_payload, vui_score=0, ev_north_tti=0, ev_east_tti=0, ev_north_v=0.0, ev_east_v=0.0):
    print(f"\n==========================================")
    print(f"RUNNING SCENARIO: {scenario_name}")
    print(f"==========================================")
    
    car_counts = parse_sumo_twin_state(twin_payload)
    cmd_args = car_counts + [
        str(vui_score),
        str(ev_north_tti),
        str(ev_east_tti),
        str(ev_north_v),
        str(ev_east_v)
    ]
    
    result = subprocess.run([EXE_PATH] + cmd_args, capture_output=True, text=True, check=True)
    decision = json.loads(result.stdout)
    
    print(f"Simulated Inflow Counts : North={cmd_args[0]}, South={cmd_args[1]}, East={cmd_args[2]}, West={cmd_args[3]}")
    print(f"Engine Decision Output  :\n{json.dumps(decision, indent=2)}")
    return decision

# 1. Sample Payload from Tharanesh's export_twin_state()
tharanesh_live_sumo_payload = {
    "timestamp": "2026-08-31T19:30:00Z",
    "intersection_id": "vadapalani_junction",
    "sim_time_s": 50,
    "edges": [
        {"edge_id": "1313198082", "queue_length": 42, "occupancy_ratio": 0.75, "avg_wait_time_s": 18.2},
        {"edge_id": "1110246916", "queue_length": 18, "occupancy_ratio": 0.35, "avg_wait_time_s": 8.5}
    ],
    "demand_profile": "medium"
}

# Scenario 1: Normal Traffic Flow (Consuming SUMO queues)
run_engine_test("1. NORMAL TRAFFIC (SUMO Live Feed)", tharanesh_live_sumo_payload, vui_score=0)

# Scenario 2: Platoon Detected (VUI Priority Override)
run_engine_test("2. PEDESTRIAN PLATOON OVERRIDE", tharanesh_live_sumo_payload, vui_score=15)

# Scenario 3: Dual-EV Conflict (Equal TTI + Standstill Tie-Breaker)
run_engine_test(
    "3. DUAL-EV PREEMPTION (North Standstill, East Moving)",
    tharanesh_live_sumo_payload,
    vui_score=15,
    ev_north_tti=15,
    ev_east_tti=15,
    ev_north_v=0.8,
    ev_east_v=14.2
)