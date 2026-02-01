"""
Test project creation without authentication
"""
import requests
import json
import sys
import io

# Fix Unicode encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000/api"

def test_no_auth_project_creation():
    """Test creating a project without authentication"""
    print("=" * 60)
    print("Testing Project Creation WITHOUT Authentication")
    print("=" * 60)
    
    # Test 1: Create a project without auth token
    print("\n[TEST 1] Creating project without auth token...")
    project_data = {
        "title": "Test Project No Auth",
        "description": "Testing project creation without authentication",
        "country": "USA",
        "region": "California"
    }
    
    # Create project (FormData)
    files = {}
    data = project_data.copy()
    
    try:
        response = requests.post(
            f"{BASE_URL}/projects",
            data=data,
            files=files,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"[OK] Project created successfully!")
            print(f"   Project ID: {result.get('id')}")
            print(f"   Title: {result.get('title')}")
            return result.get('id')
        else:
            print(f"[FAIL] Failed to create project")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

def test_list_projects():
    """Test listing projects without auth"""
    print("\n[TEST 2] Listing projects without auth token...")
    
    try:
        response = requests.get(f"{BASE_URL}/projects", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            projects = result.get('projects', [])
            print(f"[OK] Retrieved {len(projects)} projects")
            return True
        else:
            print(f"[FAIL] Failed to list projects: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_get_project(project_id):
    """Test getting a project without auth"""
    if not project_id:
        return False
    
    print(f"\n[TEST 3] Getting project {project_id} without auth token...")
    
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Retrieved project: {result.get('title')}")
            return True
        else:
            print(f"[FAIL] Failed to get project: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("NO AUTHENTICATION SYSTEM TEST")
    print("=" * 60)
    
    # Test project creation
    project_id = test_no_auth_project_creation()
    
    # Test listing projects
    test_list_projects()
    
    # Test getting project
    if project_id:
        test_get_project(project_id)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

