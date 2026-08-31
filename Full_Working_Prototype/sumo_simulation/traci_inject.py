import os
import sys


# Locate the SUMO TraCI library
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Error: Please declare environment variable 'SUMO_HOME'")

import traci
# Set up the headless SUMO command
sumoCmd = ["sumo", "-c", "osm.sumocfg"]

def run_simulation():
    print("Starting headless SUMO simulation...")
    traci.start(sumoCmd)

    step = 0
    while step < 100:
        traci.simulationStep()
        
        # Inject a mock vehicle at exactly step 10
        if step == 10:
            # Create a temporary route from the North incoming edge to the South outgoing sink
            traci.route.add("mock_route", ["1313198082.274", "1313198080"])
            
            # Spawn the vehicle on that route
            traci.vehicle.add("mock_car_1", routeID="mock_route")
            print("Successfully injected mock vehicle 'mock_car_1' onto the North approach.")
            
        step += 1

    traci.close()
    print("Simulation complete and closed cleanly.")

if __name__ == "__main__":
    run_simulation()
