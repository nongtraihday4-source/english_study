import requests
import json
import time

URL = "http://localhost:8000/api/v1/grammar-analysis/analyze/"
PAYLOAD = {
    "text": "Explain the difference between make and do"
}

print(f"Testing API: {URL}")
print(f"Payload: {json.dumps(PAYLOAD, indent=2)}")
print("-" * 40)

try:
    start_time = time.time()
    response = requests.post(URL, json=PAYLOAD, timeout=30)
    end_time = time.time()
    
    print(f"Status Code: {response.status_code}")
    print(f"Time Taken: {end_time - start_time:.2f}s")
    print("-" * 40)
    
    if response.status_code == 200:
        print("Response Body:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print("Error Response:")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("❌ Could not connect to the server.")
    print("Make sure the Django server is running: python backend/manage.py runserver")
except Exception as e:
    print(f"❌ An error occurred: {e}")
