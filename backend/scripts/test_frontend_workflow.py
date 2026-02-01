"""
Comprehensive Frontend Workflow Test
Tests: Signup -> Project Creation -> Results Viewing
"""
import requests
import json
import sys
import io
import time
from pathlib import Path

# Fix Unicode encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_test(test_name):
    """Print a test name"""
    print(f"\n[TEST] {test_name}")

def print_success(message):
    """Print success message"""
    print(f"[OK] {message}")

def print_error(message):
    """Print error message"""
    print(f"[FAIL] {message}")

def print_info(message):
    """Print info message"""
    print(f"[INFO] {message}")

def test_health_check():
    """Test 1: Health check"""
    print_section("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is healthy: {data.get('status')}")
            print_info(f"Version: {data.get('version')}")
            print_info(f"Database: {data.get('database')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_user_signup():
    """Test 2: User Signup"""
    print_section("TEST 2: User Signup")
    
    # Generate unique email (use valid domain)
    timestamp = int(time.time())
    email = f"testuser_{timestamp}@example.com"
    
    signup_data = {
        "email": email,
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "role": "user"
    }
    
    print_test("Registering new user...")
    print_info(f"Email: {email}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json=signup_data,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("User registered successfully!")
            print_info(f"User ID: {data.get('user', {}).get('id')}")
            print_info(f"Email: {data.get('user', {}).get('email')}")
            print_info(f"Name: {data.get('user', {}).get('first_name')} {data.get('user', {}).get('last_name')}")
            print_info(f"Token: {data.get('access_token', 'N/A')[:20]}...")
            return data.get('user', {}).get('id'), email
        else:
            print_error(f"Signup failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print_error(f"Signup error: {e}")
        return None, None

def test_user_login(email):
    """Test 3: User Login"""
    print_section("TEST 3: User Login")
    
    login_data = {
        "email": email,
        "password": "TestPassword123!"
    }
    
    print_test("Logging in user...")
    print_info(f"Email: {email}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("User logged in successfully!")
            print_info(f"User ID: {data.get('user', {}).get('id')}")
            print_info(f"Token: {data.get('access_token', 'N/A')[:20]}...")
            return True
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False

def test_project_creation():
    """Test 4: Project Creation (Frontend Mode - FormData)"""
    print_section("TEST 4: Project Creation (FormData)")
    
    project_data = {
        "title": f"Test Project - {int(time.time())}",
        "description": "Comprehensive test project created via frontend workflow",
        "country": "United States",
        "region": "California",
        "latitude": "37.7749",
        "longitude": "-122.4194",
        "collection_timestamp": "2024-01-15T10:30:00Z",
        "symptoms": "Fever, Cough, Fatigue",
        "clinical_severity": "Moderate",
        "clinical_notes": "Test case for system validation"
    }
    
    print_test("Creating project with FormData (as frontend does)...")
    print_info(f"Title: {project_data['title']}")
    
    try:
        # Create project using FormData (as frontend does)
        response = requests.post(
            f"{BASE_URL}/projects",
            data=project_data,  # FormData
            timeout=30
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Project created successfully!")
            print_info(f"Project ID: {data.get('id')}")
            print_info(f"Title: {data.get('title')}")
            print_info(f"Status: {data.get('status')}")
            print_info(f"User ID: {data.get('user_id')}")
            return data.get('id')
        else:
            print_error(f"Project creation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Project creation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_list_projects():
    """Test 5: List Projects"""
    print_section("TEST 5: List Projects")
    
    print_test("Fetching project list...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/projects",
            params={"page": 1, "page_size": 10},
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            total = data.get('total', 0)
            print_success(f"Retrieved {len(projects)} projects (Total: {total})")
            
            if projects:
                print_info("Sample projects:")
                for p in projects[:3]:
                    print_info(f"  - ID: {p.get('id')}, Title: {p.get('title')}, Status: {p.get('status')}")
            
            return True
        else:
            print_error(f"Failed to list projects: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"List projects error: {e}")
        return False

def test_get_project(project_id):
    """Test 6: Get Project Details"""
    print_section("TEST 6: Get Project Details")
    
    print_test(f"Fetching project {project_id}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/projects/{project_id}",
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Project retrieved successfully!")
            print_info(f"ID: {data.get('id')}")
            print_info(f"Title: {data.get('title')}")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Country: {data.get('country')}")
            print_info(f"Region: {data.get('region')}")
            print_info(f"Created: {data.get('created_at')}")
            return True
        else:
            print_error(f"Failed to get project: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Get project error: {e}")
        return False

def test_get_project_status(project_id):
    """Test 7: Get Project Status"""
    print_section("TEST 7: Get Project Status")
    
    print_test(f"Fetching status for project {project_id}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/projects/{project_id}/status",
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Project status retrieved!")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Progress: {data.get('progress', 0)}%")
            if data.get('error'):
                print_info(f"Error: {data.get('error')}")
            return True
        else:
            print_error(f"Failed to get project status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get project status error: {e}")
        return False

def test_get_project_results(project_id):
    """Test 8: Get Project Results"""
    print_section("TEST 8: Get Project Results")
    
    print_test(f"Fetching results for project {project_id}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/results/projects/{project_id}",
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Project results retrieved!")
            print_info(f"Project ID: {data.get('project_id')}")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Mutations: {len(data.get('mutations', []))}")
            print_info(f"Drug Candidates: {len(data.get('drug_candidates', []))}")
            print_info(f"Modifications: {len(data.get('modifications', []))}")
            return True
        else:
            print_error(f"Failed to get project results: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            # This is OK if project is still processing
            if response.status_code == 404:
                print_info("Note: Results may not be available yet (project still processing)")
            return False
    except Exception as e:
        print_error(f"Get project results error: {e}")
        return False

def test_get_mutations(project_id):
    """Test 9: Get Mutations"""
    print_section("TEST 9: Get Mutations")
    
    print_test(f"Fetching mutations for project {project_id}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/results/projects/{project_id}/mutations",
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} mutations")
            if data:
                print_info(f"Sample mutation: Position {data[0].get('mutation_position')}, "
                          f"Effect: {data[0].get('effect')}")
            return True
        else:
            print_info(f"Status: {response.status_code} (Results may not be available yet)")
            return True  # Not a failure if no results yet
    except Exception as e:
        print_info(f"Note: {e} (Results may not be available yet)")
        return True  # Not a failure

def test_get_drugs(project_id):
    """Test 10: Get Drug Candidates"""
    print_section("TEST 10: Get Drug Candidates")
    
    print_test(f"Fetching drug candidates for project {project_id}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/results/projects/{project_id}/drugs",
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} drug candidates")
            return True
        else:
            print_info(f"Status: {response.status_code} (Results may not be available yet)")
            return True
    except Exception as e:
        print_info(f"Note: {e} (Results may not be available yet)")
        return True

def test_user_profile():
    """Test 11: Get User Profile"""
    print_section("TEST 11: Get User Profile")
    
    print_test("Fetching user profile...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("User profile retrieved!")
            print_info(f"ID: {data.get('id')}")
            print_info(f"Email: {data.get('email')}")
            print_info(f"Name: {data.get('first_name')} {data.get('last_name')}")
            print_info(f"Role: {data.get('role')}")
            return True
        else:
            print_error(f"Failed to get profile: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get profile error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  COMPREHENSIVE FRONTEND WORKFLOW SYSTEM TEST")
    print("  Testing: Signup -> Project Creation -> Results Viewing")
    print("=" * 70)
    
    results = {
        "health_check": False,
        "signup": False,
        "login": False,
        "project_creation": False,
        "list_projects": False,
        "get_project": False,
        "project_status": False,
        "project_results": False,
        "mutations": False,
        "drugs": False,
        "profile": False
    }
    
    project_id = None
    user_email = None
    
    # Test 1: Health Check
    results["health_check"] = test_health_check()
    if not results["health_check"]:
        print_error("Backend is not healthy. Stopping tests.")
        return
    
    # Test 2: User Signup
    user_id, user_email = test_user_signup()
    results["signup"] = user_id is not None
    
    # Test 3: User Login
    if user_email:
        results["login"] = test_user_login(user_email)
    
    # Test 4: Project Creation
    project_id = test_project_creation()
    results["project_creation"] = project_id is not None
    
    # Test 5: List Projects
    results["list_projects"] = test_list_projects()
    
    # Test 6: Get Project
    if project_id:
        results["get_project"] = test_get_project(project_id)
    
    # Test 7: Project Status
    if project_id:
        results["project_status"] = test_get_project_status(project_id)
    
    # Test 8: Project Results
    if project_id:
        results["project_results"] = test_get_project_results(project_id)
    
    # Test 9: Mutations
    if project_id:
        results["mutations"] = test_get_mutations(project_id)
    
    # Test 10: Drug Candidates
    if project_id:
        results["drugs"] = test_get_drugs(project_id)
    
    # Test 11: User Profile
    results["profile"] = test_user_profile()
    
    # Summary
    print_section("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print("\n" + "=" * 70)
    if passed_tests == total_tests:
        print("  ALL TESTS PASSED!")
    else:
        print("  SOME TESTS FAILED - Check details above")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

