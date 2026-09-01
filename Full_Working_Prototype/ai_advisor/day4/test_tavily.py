from tavily_service import search_events_near_intersection


intersection = "Times Square, New York"

results = search_events_near_intersection(intersection)

for result in results["results"]:
    print("\nTITLE:", result["title"])
    print("URL:", result["url"])
    print("CONTENT:", result["content"][:500])