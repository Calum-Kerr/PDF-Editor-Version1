import requests

# Base URL 
base_url = "http://localhost:5000"

# Routes to test
routes = [
    "/",
    "/accessibility-statement",
    "/accessibility",
    "/privacy",
    "/terms",
    "/cookies",
]

# Test each route
for route in routes:
    url = base_url + route
    try:
        response = requests.get(url)
        print(f"Route: {route} - Status: {response.status_code}")
    except Exception as e:
        print(f"Route: {route} - Error: {e}") 