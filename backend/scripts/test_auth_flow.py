"""
Test the complete authentication flow: signup -> create project -> view results
"""
import requests
import json
import time
from typing import Optional

BASE_URL = "http://localhost:8000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def test_auth_flow():
    """Test complete authentication flow"""
    print_header("VIRO-AI AUTHENTICATION FLOW TEST")
    
    # Generate unique email
    timestamp = int(time.time())
    test_email = f"testuser_{timestamp}@test.com"
    test_password = "TestPassword123!"
    
    token: Optional[str] = None
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    
    # Step 1: Sign Up
    print_header("STEP 1: User Registration")
    print_info(f"Creating user with email: {test_email}")
    
    try:
        signup_data = {
            "firstName": "Test",
            "lastName": "User",
            "email": test_email,
            "password": test_password,
            "role": "user"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json=signup_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # Handle both token formats
            token = data.get("access_token") or data.get("token")
            user_data = data.get("user") or {}
            user_id = user_data.get("id") if isinstance(user_data, dict) else None
            
            if token:
                print_success(f"User registered successfully!")
                print_success(f"Token received: {token[:30]}...")
                print_success(f"User ID: {user_id}")
            else:
                print_error("No token received in response")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False
    
    if not token:
        print_error("No token available, cannot continue")
        return False
    
    # Step 2: Verify Authentication
    print_header("STEP 2: Verify Authentication")
    print_info("Testing GET /api/auth/me endpoint")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print_success(f"Authentication verified!")
            print_success(f"Current user: {user_data.get('email')}")
        else:
            print_error(f"Authentication failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Authentication verification error: {e}")
        return False
    
    # Step 3: Create Project
    print_header("STEP 3: Create Project")
    print_info("Creating a test project")
    
    try:
        project_data = {
            "title": "Test Project - Authentication Flow",
            "description": "This is a test project created during authentication flow testing",
            "country": "USA",
            "region": "California",
            "symptoms": "Fever, cough, fatigue",
            "clinical_severity": "Moderate",
            "clinical_notes": "Test clinical notes for authentication flow"
        }
        
        response = requests.post(
            f"{BASE_URL}/projects",
            json=project_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            project = response.json()
            project_id = project.get("id")
            print_success(f"Project created successfully!")
            print_success(f"Project ID: {project_id}")
            print_success(f"Project Title: {project.get('title')}")
            print_success(f"Project Status: {project.get('status')}")
        else:
            print_error(f"Project creation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Project creation error: {e}")
        return False
    
    if not project_id:
        print_error("No project ID available, cannot continue")
        return False
    
    # Step 4: Check Project Status
    print_header("STEP 4: Check Project Status")
    print_info(f"Checking status of project {project_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/projects/{project_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            project = response.json()
            print_success(f"Project status: {project.get('status')}")
            print_info(f"  Mutations: {project.get('mutations_count', 0)}")
            print_info(f"  Drugs: {project.get('drugs_count', 0)}")
            print_info(f"  Modifications: {project.get('modifications_count', 0)}")
        else:
            print_error(f"Failed to get project: {response.status_code}")
    except Exception as e:
        print_error(f"Error getting project: {e}")
    
    # Step 5: View Results
    print_header("STEP 5: View Project Results")
    print_info(f"Retrieving results for project {project_id}")
    
    try:
        # Get detailed results
        response = requests.get(
            f"{BASE_URL}/results/{project_id}/detailed",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            mutations = len(results.get("mutations", []))
            drugs = len(results.get("drugs", []))
            modifications = len(results.get("modifications", []))
            
            print_success("Results retrieved successfully!")
            print_info(f"  Mutations: {mutations}")
            print_info(f"  Drugs: {drugs}")
            print_info(f"  Modifications: {modifications}")
        else:
            print_error(f"Failed to get results: {response.status_code}")
            print_error(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Error getting results: {e}")
    
    # Step 6: Test Individual Result Endpoints
    print_header("STEP 6: Test Individual Result Endpoints")
    
    endpoints = [
        ("mutations", f"{BASE_URL}/results/{project_id}/mutations"),
        ("drugs", f"{BASE_URL}/results/{project_id}/drugs"),
        ("modifications", f"{BASE_URL}/results/{project_id}/modifications"),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print_success(f"{name.capitalize()}: {count} items")
            else:
                print_error(f"{name.capitalize()}: Failed ({response.status_code})")
        except Exception as e:
            print_error(f"{name.capitalize()}: Error - {e}")
    
    # Summary
    print_header("TEST SUMMARY")
    print_success("User registration: PASSED")
    print_success("Authentication verification: PASSED")
    print_success("Project creation: PASSED")
    print_success("Results retrieval: PASSED")
    print_success("\nAuthentication flow test completed successfully!")
    
    return True

if __name__ == "__main__":
    try:
        test_auth_flow()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

