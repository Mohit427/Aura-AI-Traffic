import requests
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv


print("Starting TomTom test...")


# Load .env from the project root
load_dotenv(
    r"C:\Users\hp\Aura-AI-Traffic\Full Working Prototype\.env"
)

API_KEY = os.getenv("TOMTOM_API_KEY")


if not API_KEY:
    print("ERROR: TOMTOM_API_KEY not found in .env")
    exit()


print("TomTom API key found.")


# -----------------------------------
# Vadapalani Junction, Chennai
# -----------------------------------

lat = 13.0505
lon = 80.2121


# TomTom Traffic Flow API
url = (
    "https://api.tomtom.com/traffic/services/4/"
    "flowSegmentData/absolute/10/json"
)


params = {
    "point": f"{lat},{lon}",
    "unit": "KMPH",
    "thickness": 10,
    "openLr": "false",
    "key": API_KEY
}


print("Requesting TomTom Traffic Flow data...")
print("Location:", lat, lon)


try:

    response = requests.get(url, params=params, timeout=15)

except requests.RequestException as e:

    print("ERROR: Could not connect to TomTom")
    print(e)
    exit()


print("Status code:", response.status_code)


# -----------------------------------
# Process successful response
# -----------------------------------

if response.status_code == 200:

    data = response.json()
    flow = data["flowSegmentData"]

    current_speed = flow["currentSpeed"]
    free_flow_speed = flow["freeFlowSpeed"]

    # Calculate congestion ratio
    if free_flow_speed > 0:
        congestion_ratio = round(
            1 - (current_speed / free_flow_speed),
            3
        )
    else:
        congestion_ratio = 0


    # -----------------------------------
    # AURA TomTom JSON Contract
    # -----------------------------------

    tomtom_record = {

        "timestamp": datetime.now(timezone.utc).isoformat(),

        "segment_id": "vadapalani_junction",

        "current_speed_kmh": current_speed,

        "free_flow_speed_kmh": free_flow_speed,

        "congestion_ratio": congestion_ratio
    }


    print("\nTomTom Traffic Data")
    print("-------------------")

    print("Current speed:",
          current_speed, "km/h")

    print("Free flow speed:",
          free_flow_speed, "km/h")

    print("Congestion ratio:",
          congestion_ratio)


    print("\nAURA TomTom JSON")
    print("----------------")

    print(json.dumps(
        tomtom_record,
        indent=2
    ))


    # -----------------------------------
    # Save JSON
    # -----------------------------------

    with open(
        "day2_tomtom.json",
        "w"
    ) as f:

        json.dump(
            tomtom_record,
            f,
            indent=2
        )


    print("\nSaved to day2_tomtom.json")


else:

    print("ERROR: TomTom request failed")
    print(response.text)