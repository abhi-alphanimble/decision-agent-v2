
"""
Test script for FastAPI endpoints
Run with: python test_api.py
"""
# import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_separator(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_endpoint(method, endpoint, expected_status=200):
    """Test an endpoint and print results"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing: {method} {endpoint}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url)
        
        duration = round((time.time() - start_time) * 1000, 2)
        
        print(f"   Status: {response.status_code} (Expected: {expected_status})")
        print(f"   Duration: {duration}ms")
        
        if response.status_code == expected_status:
            print("   ✅ PASSED")
        else:
            print("   ❌ FAILED")
        
        print(f"   Response: {response.json()}")
        
        return response.status_code == expected_status
    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def main():
    print_separator("FastAPI Endpoint Tests")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now()}")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Root endpoint
    print_separator("Test 1: Root Endpoint")
    tests_total += 1
    if test_endpoint("GET", "/"):
        tests_passed += 1
    
    # Test 2: Health check
    print_separator("Test 2: Health Check")
    tests_total += 1
    if test_endpoint("GET", "/health"):
        tests_passed += 1
    
    # Test 3: System status
    print_separator("Test 3: System Status")
    tests_total += 1
    if test_endpoint("GET", "/api/v1/status"):
        tests_passed += 1
    
    # Test 4: OpenAPI docs (HTML response)
    print_separator("Test 4: API Documentation")
    print(f"\n🔍 Testing: GET /docs")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200 and "swagger" in response.text.lower():
            print("   ✅ PASSED - Swagger UI accessible")
            tests_passed += 1
        else:
            print("   ❌ FAILED - Swagger UI not accessible")
        tests_total += 1
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        tests_total += 1
    
    # Test 5: Invalid endpoint (should return 404)
    print_separator("Test 5: Invalid Endpoint (404)")
    tests_total += 1
    if test_endpoint("GET", "/invalid-endpoint", expected_status=404):
        tests_passed += 1
    
    # Summary
    print_separator("Test Summary")
    print(f"\n   Total Tests: {tests_total}")
    print(f"   Passed: {tests_passed}")
    print(f"   Failed: {tests_total - tests_passed}")
    print(f"   Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("\n   🎉 All tests passed!")
    else:
        print("\n   ⚠️  Some tests failed")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print("\n⏳ Waiting for server to be ready...")
    time.sleep(2)
    main()

