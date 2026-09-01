from aura_service import get_events_and_response


intersection = "Times Square, New York"

result = get_events_and_response(intersection)

print("\nINTERSECTION:")
print(result["intersection"])

print("\nAURA RESPONSE:")
print(result["response"])

print("\nSOURCES:")
for source in result["sources"]:
    print(source["title"])
    print(source["url"])