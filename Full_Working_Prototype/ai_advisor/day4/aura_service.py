from tavily_service import search_events_near_intersection
from gemini_service import generate_response


def get_events_and_response(intersection: str):
    # Step 1: Search for real-world events
    tavily_results = search_events_near_intersection(intersection)

    # Step 2: Give Tavily results to Gemini
    prompt = f"""
You are AURA, an AI assistant that helps users understand
what is happening around their location.

The user is near:
{intersection}

Here are real-world search results from Tavily:

{tavily_results}

Based on these results:

1. Identify the most relevant events.
2. Give the user a concise summary.
3. Mention the event name and useful details when available.
4. Include the source URL when useful.
5. Do not invent information that is not present in the search results.

Respond in a helpful, natural way.
"""

    # Step 3: Generate AURA's response
    response = generate_response(prompt)

    # Step 4: Return the final result
    return {
        "intersection": intersection,
        "response": response,
        "sources": tavily_results["results"]
    }