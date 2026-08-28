import subprocess
import json

# Replace with the actual path to your compiled C++ executable
exe_path = r"Full Working Prototype/engine/Debug/edmonds_karp.exe"

try:
    # 1. Run the C++ engine and capture the terminal output
    result = subprocess.run([exe_path], capture_output=True, text=True, check=True)
    
    # 2. Parse the captured text into a Python JSON dictionary
    engine_data = json.loads(result.stdout)
    
    # 3. Prove it worked by printing a specific key from the dictionary
    print("Integration Successful!")
    print(f"Pedestrian Green Time: {engine_data['phase_durations']['pedestrian_crossing_green']} seconds (VUI Score: {engine_data['vui_score']})")
    print(f"North-South Green Time: {engine_data['phase_durations']['north_south_green']} seconds")
    print(f"East-West Green Time: {engine_data['phase_durations']['east_west_green']} seconds")
    
except FileNotFoundError:
    print(f"Error: Could not find the executable at {exe_path}")
except json.JSONDecodeError:
    print("Error: The C++ output is not valid JSON. Raw output:")
    print(result.stdout)