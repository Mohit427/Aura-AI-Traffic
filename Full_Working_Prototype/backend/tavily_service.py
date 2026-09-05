import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def get_search_context(location="Vadapalani Junction, Chennai", radius_km=2):
    print(f"Searching Tavily for traffic events near {location}...")
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_key:
        print("Error: TAVILY_API_KEY not found in .env")
        return {"events": []}
        
    client = TavilyClient(api_key=tavily_key)
    query = f"Recent traffic events, road closures, or accidents near {location} within {radius_km}km"
    
    try:
        # Perform search
        response = client.search(query=query, search_depth="basic", max_results=3)
        
        events = []
        for result in response.get("results", []):
            events.append({
                "title": result.get("title", "Unknown Event"),
                "type": "incident",
                "relevance": "high"
            })
            
        return {"events": events}
    except Exception as e:
        print(f"Tavily search failed: {e}")
        return {"events": []}

if __name__ == "__main__":
    print(get_search_context())