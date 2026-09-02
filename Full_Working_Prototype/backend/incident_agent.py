import os
import json
import urllib.request
import urllib.error
import subprocess
from tavily_service import get_search_context
from dotenv import load_dotenv

load_dotenv()

def analyze_and_respond(engine_output):
    context = get_search_context(engine_output.get("intersection_id", "Vadapalani Junction, Chennai"))
    
    print("\nCalling Gemini AI for Decision...")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"
    
    prompt = f"""
    Engine Output: {json.dumps(engine_output)}
    Search Context: {json.dumps(context)}
    
    Analyze the traffic data. If priority_mode is 'emergency_vehicle', return strictly a JSON string with key "action" set to "DISPATCH_ALERT" and "explanation" describing the conflict and reason for the green wave. Otherwise set "action" to "NORMAL".
    """
    
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    headers = {'Content-Type': 'application/json', 'x-goog-api-key': gemini_key}
    req = urllib.request.Request(url, data=payload, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            
            clean_text = text_response.replace('```json', '').replace('```', '').strip()
            decision = json.loads(clean_text)
            
            print(f"AI Decision: {decision.get('explanation', '')}")
            
            if decision.get("action") == "DISPATCH_ALERT":
                dispatch_alerts(decision.get('explanation', 'Emergency priority triggered.'))
                
    except Exception as e:
        print(f"Gemini AI error: {e}")

def dispatch_alerts(message):
    print("\n[ALERT] Dispatching Swytchcode Actions...")
    
    slack_canonical_id = "slack.chat.postmessage.create"
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    
    # Slack Alert via Swytchcode CLI
    slack_payload = json.dumps({
        "token": slack_token,
        "body": {
            "channel": "U0BU75050KD",
            "text": f"🚨 TRAFFIC ALERT: {message}"
        }
    })
    print(f"Firing Slack via CLI...")
    subprocess.run(["swytchcode", "exec", slack_canonical_id], input=slack_payload, text=True)

if __name__ == "__main__":
    mock_engine_output = {
        "intersection_id": "vadapalani_junction",
        "phase_durations": {"north_south_green": 32, "east_west_green": 28, "pedestrian_crossing_green": 15},
        "priority_mode": "emergency_vehicle",
        "vui_score": 42
    }
    analyze_and_respond(mock_engine_output)