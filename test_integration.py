import subprocess
import json

# Replace with the actual path to your compiled C++ executable
exe_path = r"Full_Working_Prototype/engine/Debug/edmonds_karp.exe"

# Simulated inputs: 
# [North Cars, South Cars, East Cars, West Cars, VUI Score, EV North TTI, EV East TTI, EV North Velocity, EV East Velocity]
# North EV: TTI 15, Velocity 1.0 m/s (Standstill) | East EV: TTI 25, Velocity 12.5 m/s
live_inputs = ["120", "85", "40", "30", "12", "15", "25", "1.0", "12.5"]

try:
    result = subprocess.run([exe_path] + live_inputs, capture_output=True, text=True, check=True)
    engine_data = json.loads(result.stdout)
    
    print("Integration Successful!\n")
    print(f"Priority Mode: {engine_data['priority_mode']}")
    
    if engine_data['priority_mode'] == 'ev_preemption':
        schedule = engine_data['ev_schedule']
        print("--- EMERGENCY VEHICLE OVERRIDE ---")
        print(f"Primary Axis (EV-1): {schedule['ev_1_axis']}")
        print(f"Standstill Gridlock Detected: {schedule['standstill_pre_flush_triggered']}")
        print(f"Forced Green Flush Duration: {schedule['ev_1_green_flush_duration']} seconds")
        print(f"All-Red Clearance: {schedule['all_red_clearance']} seconds")
        print(f"Secondary Axis (EV-2): {schedule['ev_2_axis']}")
    else:
        print("Normal routing active.")
        
except FileNotFoundError:
    print(f"Error: Could not find the executable at {exe_path}")
except json.JSONDecodeError:
    print("Error: The C++ output is not valid JSON. Raw output:")
    print(result.stdout)