#!/usr/bin/env python3
"""
Simple test script for the backend API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_emotion_summary():
    """Test emotion summary endpoint"""
    print("Testing emotion summary endpoint...")
    response = requests.get(f"{BASE_URL}/emotions/summary")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_daily_stats():
    """Test daily stats endpoint"""
    print("Testing daily stats endpoint...")
    response = requests.get(f"{BASE_URL}/emotions/daily-stats?days=7")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")  # Truncate long response
    print()

if __name__ == "__main__":
    print("Backend API Test Script")
    print("=" * 50)
    
    try:
        test_health()
        test_root()
        test_emotion_summary()
        test_daily_stats()
        print("All tests completed!")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to backend API at", BASE_URL)
        print("Make sure the backend is running with: cd backend && uvicorn app:app")