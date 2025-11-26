import requests
import sys

def test_endpoint(url):
    print(f"Testing {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:100]}")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

print("--- Starting Local Server Test ---")
success_root = test_endpoint("http://localhost:8000/")
success_health = test_endpoint("http://localhost:8000/health")

if success_root and success_health:
    print("✅ Local server is responsive.")
else:
    print("❌ Local server is NOT responsive.")
