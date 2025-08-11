#!/usr/bin/env python3
"""
API Smoke Test Script for Star Wars Flask REST API (Python version)
Usage: export JWT_TOKEN=your_token_here; python3 api_smoke_test.py
"""
import os
import sys
import requests

BASE_URL = "http://127.0.0.1:3000"

# Helper to print response like curl -i
def print_response(resp):
    print(f"HTTP/{resp.raw.version/10:.1f} {resp.status_code} {resp.reason}")
    for k, v in resp.headers.items():
        print(f"{k}: {v}")
    print("\n" + resp.text)

print("\n== Root ==")
resp = requests.get(f"{BASE_URL}/", stream=True)
print_response(resp)

print("\n== Swagger Docs ==")
resp = requests.get(f"{BASE_URL}/api/docs/", stream=True)
print_response(resp)

print("\n== People ==")
resp = requests.get(f"{BASE_URL}/api/people", stream=True)
print_response(resp)

print("\n== Planets ==")
resp = requests.get(f"{BASE_URL}/api/planets", stream=True)
print_response(resp)

print("\n== Vehicles ==")
resp = requests.get(f"{BASE_URL}/api/vehicles", stream=True)
print_response(resp)

JWT_TOKEN = os.environ.get("JWT_TOKEN")
if not JWT_TOKEN:
    print("\nERROR: JWT_TOKEN is not set. Please export a valid token before running protected endpoint tests.")
    print("Example: export JWT_TOKEN=your_actual_jwt_token_here")
    sys.exit(1)

headers = {"Authorization": f"Bearer {JWT_TOKEN}"}

print("\n== Profile (JWT required) ==")
resp = requests.get(f"{BASE_URL}/api/profile", headers=headers, stream=True)
print_response(resp)

print("\n== Favorites (JWT required) ==")
resp = requests.get(f"{BASE_URL}/api/favorites", headers=headers, stream=True)
print_response(resp)

print("\n== Add Favorite (JWT required) ==")
resp = requests.post(f"{BASE_URL}/api/favorites", headers={**headers, "Content-Type": "application/json"}, json={"people_id": 1}, stream=True)
print_response(resp)

print("\n== Delete Favorite (JWT required) ==")
resp = requests.delete(f"{BASE_URL}/api/favorites/1", headers=headers, stream=True)
print_response(resp)
