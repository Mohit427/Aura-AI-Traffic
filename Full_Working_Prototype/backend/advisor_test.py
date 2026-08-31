import urllib.request
import urllib.error
import json
import os # Import the os module

def test_hello_world():
    print("Bypassing Swytchcode: Executing Gemini directly via native headers...")
    
    # Pull the key dynamically to pass GitHub's security scan
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        print("Error: GEMINI_API_KEY environment variable not found.")
        return
        
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"
    
    payload = json.dumps({
        "contents": [{"parts": [{"text": "Respond strictly with the words: Hello World"}]}]
    }).encode("utf-8")
    
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': API_KEY
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            print(f"Success! Agent Response:\n{text_response}")
    except urllib.error.HTTPError as e:
        print(f"Error ({e.code}):\n{e.read().decode('utf-8')}")

if __name__ == "__main__":
    test_hello_world()