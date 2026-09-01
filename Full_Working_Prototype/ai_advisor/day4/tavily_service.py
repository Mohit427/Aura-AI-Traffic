import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set")

client = TavilyClient(api_key=TAVILY_API_KEY)


def search_events_near_intersection(intersection: str):
    query = f"events happening near {intersection}"

    response = client.search(
        query=query,
        search_depth="basic",
        max_results=5
    )

    return response