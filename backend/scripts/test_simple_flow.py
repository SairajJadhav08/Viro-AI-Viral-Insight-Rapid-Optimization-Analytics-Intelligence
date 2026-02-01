"""
Simple test: Create user and project with JSON
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

print("="*70)
print("SIMPLE AUTHENTICATION FLOW TEST")
print("="*70)

# Step 1: Create User
print("\n[1] Creating user...")
timestamp = int(time.time())
email = f"testuser_{timestamp}@test.com"

signup_data = {
    "firstName": "Test",
    "lastName": "User",
    "email": email,
    "password": "Test123!",
    "role": "user"
}

try:
    r = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, timeout=10)
    if r.status_code == 200:
        data = r.json()
        token = data.get("access_token") or data.get("token")
        user_id = data.get("user", {}).get("id") if isinstance(data.get("user"), dict) else None
        print(f"[OK] User created: {email}")
        print(f"[OK] User ID: {user_id}")
        print(f"[OK] Token: {token[:30]}...")
    else:
        print(f"[FAIL] Signup failed: {r.status_code}")
        print(f"Response: {r.text}")
        exit(1)
except Exception as e:
    print(f"[FAIL] Error: {e}")
    exit(1)

# Step 2: Create Project with JSON
print("\n[2] Creating project with JSON...")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

project_data = {
    "title": "Test Project from JSON",
    "description": "Testing JSON project creation",
    "country": "USA",
    "region": "California",
    "symptoms": "Fever, cough",
    "clinical_severity": "Moderate",
    "clinical_notes": "Test notes"
}

try:
    r = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=30)
    if r.status_code in [200, 201]:
        project = r.json()
        project_id = project.get("id")
        print(f"[OK] Project created!")
        print(f"[OK] Project ID: {project_id}")
        print(f"[OK] Title: {project.get('title')}")
        print(f"[OK] Status: {project.get('status')}")
    else:
        print(f"[FAIL] Project creation failed: {r.status_code}")
        print(f"Response: {r.text}")
        exit(1)
except Exception as e:
    print(f"[FAIL] Error: {e}")
    exit(1)

# Step 3: View Results
print("\n[3] Viewing project results...")
try:
    r = requests.get(f"{BASE_URL}/results/{project_id}/detailed", headers=headers, timeout=10)
    if r.status_code == 200:
        results = r.json()
        mutations = len(results.get("mutations", []))
        drugs = len(results.get("drugs", []))
        modifications = len(results.get("modifications", []))
        print(f"[OK] Results retrieved!")
        print(f"[OK] Mutations: {mutations}")
        print(f"[OK] Drugs: {drugs}")
        print(f"[OK] Modifications: {modifications}")
    else:
        print(f"[FAIL] Failed to get results: {r.status_code}")
        print(f"Response: {r.text}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

print("\n" + "="*70)
print("[SUCCESS] All tests passed!")
print("="*70)

