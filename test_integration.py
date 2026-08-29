import subprocess
import json

# Replace with the actual path to your compiled C++ executable
exe_path = r"Full_Working_Prototype/engine/Debug/edmonds_karp.exe"

# Simulated inputs: [North Cars, South Cars, East Cars, West Cars, VUI Score, EV North TTI, EV East TTI]
live_inputs = ["120", "85", "40", "30", "12", "15", "25"]

try:
    # Run the C++ engine WITH the dynamic command-line arguments
    result = subprocess.run([exe_path] + live_inputs, capture_output=True, text=True, check=True)
    
    # Parse the captured text into a Python JSON dictionary
    engine_data = json.loads(result.stdout)
    
    # Prove it worked by printing the dynamically calculated timings
    print("Integration Successful!")
    print(f"Priority Mode: {engine_data['priority_mode']}")
    print(f"VUI Score: {engine_data['vui_score']}")
    
    if engine_data['priority_mode'] == 'ev_preemption':
        print("\n--- EMERGENCY VEHICLE OVERRIDE ---")
        schedule = engine_data['ev_schedule']
        print(f"EV 1 (Immediate Flush): {schedule['ev_1_axis']} for {schedule['ev_1_green_flush_duration']} seconds")
        print(f"All-Red Clearance: {schedule['all_red_clearance']} seconds")
        print(f"EV 2 (Next Flush): {schedule['ev_2_axis']}")
    else:
        print(f"Pedestrian Green Time: {engine_data['phase_durations']['pedestrian_crossing_green']} seconds")
        print(f"North-South Green Time: {engine_data['phase_durations']['north_south_green']} seconds")
        print(f"East-West Green Time: {engine_data['phase_durations']['east_west_green']} seconds")
    
except FileNotFoundError:
    print(f"Error: Could not find the executable at {exe_path}")
except json.JSONDecodeError:
    print("Error: The C++ output is not valid JSON. Raw output:")
    print(result.stdout)