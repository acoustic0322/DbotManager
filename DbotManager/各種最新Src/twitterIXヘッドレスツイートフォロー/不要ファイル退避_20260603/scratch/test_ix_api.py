
import requests
import json

base_url = "http://127.0.0.1:53200/api"

def test_api(endpoint):
    print(f"Testing {endpoint}...")
    try:
        resp = requests.post(f"{base_url}{endpoint}", json={'page': 1, 'limit': 10}, timeout=5)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

test_api("/v2/profile-list")
test_api("/profile-list")
test_api("/v2/group-list")
