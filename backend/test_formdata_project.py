"""
Test project creation with FormData (like frontend does)
"""
import requests
import time

BASE_URL = "http://localhost:8000/api"

print("="*70)
print("TESTING PROJECT CREATION WITH FORMDATA")
print("="*70)

# Step 1: Create User
print("\n[1] Creating user...")
timestamp = int(time.time())
email = f"testuser_{timestamp}@test.com"

signup_data = {
    "first_name": "Test",
    "last_name": "User",
    "email": email,
    "password": "Test123!",
    "role": "user"
}

try:
    r = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, timeout=10)
    if r.status_code == 200:
        data = r.json()
        token = data.get("access_token") or data.get("token")
        print(f"[OK] User created: {email}")
        print(f"[OK] Token: {token[:30]}...")
    else:
        print(f"[FAIL] Signup failed: {r.status_code}")
        print(f"Response: {r.text}")
        exit(1)
except Exception as e:
    print(f"[FAIL] Error: {e}")
    exit(1)

# Step 2: Create Project with FormData (like frontend)
print("\n[2] Creating project with FormData...")
headers = {"Authorization": f"Bearer {token}"}

# Create FormData
form_data = {
    "title": "Test Project from FormData",
    "description": "Testing FormData project creation",
    "country": "USA",
    "region": "California",
    "symptoms": "Fever, cough",
    "clinical_severity": "Moderate",
    "clinical_notes": "Test notes"
}

try:
    r = requests.post(f"{BASE_URL}/projects", data=form_data, headers=headers, timeout=30)
    print(f"Status Code: {r.status_code}")
    print(f"Response Headers: {dict(r.headers)}")
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
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*70)
print("[SUCCESS] FormData project creation test passed!")
print("="*70)

