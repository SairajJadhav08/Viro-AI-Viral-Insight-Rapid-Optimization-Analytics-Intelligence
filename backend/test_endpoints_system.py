"""
Comprehensive system test for Viro-AI Backend
Tests all endpoints by creating a user and project, then verifying all connections
"""
import sys
import os
import time
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
HEALTH_URL = f"{BASE_URL}/api/health"

# Test user credentials (using camelCase as expected by API)
# Note: role is required by the API
def get_test_user():
    """Get test user data with unique email"""
    return {
        "firstName": "Test",
        "lastName": "User",
        "email": f"testuser_{int(time.time())}@test.com",
        "password": "TestPassword123!",
        "phone": "+1234567890",
        "role": "user"
    }

TEST_USER = get_test_user()

# Test project data
TEST_PROJECT = {
    "title": "System Test Project",
    "description": "This is a test project created by the system test script",
    "country": "USA",
    "region": "California",
    "symptoms": "Fever, cough",
    "clinical_severity": "Moderate",
    "clinical_notes": "Test clinical notes"
}

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {message}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {message}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {message}")

def print_header(message: str):
    """Print header"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

class EndpointTester:
    """Test all endpoints"""
    
    def __init__(self):
        self.base_url = API_BASE
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.project_id: Optional[int] = None
        self.test_results: Dict[str, Any] = {}
    
    def get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if include_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        print_info("Testing health check endpoint...")
        try:
            response = requests.get(HEALTH_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check: {data.get('status', 'unknown')}")
                return True
            else:
                print_error(f"Health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print_error("Cannot connect to backend. Is the server running on http://localhost:8000?")
            return False
        except Exception as e:
            print_error(f"Health check error: {e}")
            return False
    
    def test_register_user(self) -> bool:
        """Test user registration"""
        print_info("Testing user registration...")
        try:
            # Get fresh test user data
            user_data = get_test_user()
            # Try /api/auth/signup first (actual endpoint)
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json=user_data,
                headers=self.get_headers(include_auth=False),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Try different possible response formats
                self.token = data.get("access_token") or data.get("accessToken") or data.get("token")
                user_data = data.get("user") or data
                self.user_id = user_data.get("id") if isinstance(user_data, dict) else None
                print_success(f"User registered: {user_data['email']}")
                if self.token:
                    print_success(f"Token received: {self.token[:20]}...")
                if self.user_id:
                    print_success(f"User ID: {self.user_id}")
                else:
                    print_warning("User ID not found in response")
                return True
            elif response.status_code == 400 and "already registered" in response.text.lower():
                print_warning("User already exists, trying login instead...")
                # Update TEST_USER for login
                global TEST_USER
                TEST_USER = user_data
                return self.test_login()
            else:
                print_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Registration error: {e}")
            return False
    
    def test_login(self) -> bool:
        """Test user login"""
        print_info("Testing user login...")
        try:
            # Get current test user email
            user_email = TEST_USER.get("email") or get_test_user()["email"]
            user_password = TEST_USER.get("password") or "TestPassword123!"
            response = requests.post(
                f"{self.base_url}/auth/signin",
                json={
                    "email": user_email,
                    "password": user_password
                },
                headers=self.get_headers(include_auth=False),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Try different possible response formats
                self.token = data.get("access_token") or data.get("accessToken") or data.get("token")
                user_data = data.get("user") or data
                self.user_id = user_data.get("id") if isinstance(user_data, dict) else None
                print_success(f"User logged in: {user_email}")
                if self.token:
                    print_success(f"Token received: {self.token[:20]}...")
                return True
            else:
                print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Login error: {e}")
            return False
    
    def test_get_current_user(self) -> bool:
        """Test get current user endpoint"""
        print_info("Testing GET /api/auth/me...")
        try:
            response = requests.get(
                f"{self.base_url}/auth/me",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Current user: {data.get('email')}")
                return True
            else:
                print_error(f"Get current user failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Get current user error: {e}")
            return False
    
    def test_update_profile(self) -> bool:
        """Test update profile endpoint"""
        print_info("Testing PUT /api/user/profile/...")
        try:
            update_data = {
                "first_name": "Updated",
                "professional_summary": "System test user"
            }
            response = requests.put(
                f"{self.base_url}/user/profile/",
                json=update_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Profile updated: {data.get('first_name')}")
                return True
            else:
                print_error(f"Update profile failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Update profile error: {e}")
            return False
    
    def test_create_project(self) -> bool:
        """Test create project endpoint"""
        print_info("Testing POST /api/projects...")
        try:
            # Create project with JSON data (based on actual API)
            project_data = TEST_PROJECT.copy()
            
            response = requests.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.project_id = data.get("id")
                print_success(f"Project created: {data.get('title')}")
                print_success(f"Project ID: {self.project_id}")
                print_success(f"Project Status: {data.get('status')}")
                return True
            else:
                print_error(f"Create project failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Create project error: {e}")
            return False
    
    def test_list_projects(self) -> bool:
        """Test list projects endpoint"""
        print_info("Testing GET /api/projects...")
        try:
            response = requests.get(
                f"{self.base_url}/projects?limit=10&offset=0",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # API might return list directly or wrapped
                if isinstance(data, list):
                    count = len(data)
                    print_success(f"Projects listed: {count} projects")
                else:
                    total = data.get("total", len(data.get("items", [])))
                    items = data.get("items", [])
                    print_success(f"Projects listed: {total} total, {len(items)} in response")
                return True
            else:
                print_error(f"List projects failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"List projects error: {e}")
            return False
    
    def test_get_project(self) -> bool:
        """Test get project endpoint"""
        if not self.project_id:
            print_warning("No project ID available, skipping get project test")
            return False
        
        print_info(f"Testing GET /api/projects/{self.project_id}...")
        try:
            response = requests.get(
                f"{self.base_url}/projects/{self.project_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Project retrieved: {data.get('title')}")
                return True
            else:
                print_error(f"Get project failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Get project error: {e}")
            return False
    
    def test_get_project_status(self) -> bool:
        """Test get project status endpoint"""
        if not self.project_id:
            print_warning("No project ID available, skipping project status test")
            return False
        
        print_info(f"Testing GET /api/projects/{self.project_id} (for status)...")
        try:
            # Status is included in project response
            response = requests.get(
                f"{self.base_url}/projects/{self.project_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                print_success(f"Project status: {status}")
                print_info(f"  Mutations: {data.get('mutations_count', 0)}")
                print_info(f"  Drugs: {data.get('drugs_count', 0)}")
                print_info(f"  Modifications: {data.get('modifications_count', 0)}")
                return True
            else:
                print_error(f"Get project status failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Get project status error: {e}")
            return False
    
    def test_get_project_results(self) -> bool:
        """Test get project results endpoint"""
        if not self.project_id:
            print_warning("No project ID available, skipping project results test")
            return False
        
        print_info(f"Testing GET /api/results/{self.project_id}/detailed...")
        try:
            response = requests.get(
                f"{self.base_url}/results/{self.project_id}/detailed",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                mutations = len(data.get("mutations", []))
                drugs = len(data.get("drugs", []))
                modifications = len(data.get("modifications", []))
                print_success(f"Project results retrieved")
                print_info(f"  Mutations: {mutations}")
                print_info(f"  Drugs: {drugs}")
                print_info(f"  Modifications: {modifications}")
                return True
            else:
                print_error(f"Get project results failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Get project results error: {e}")
            return False
    
    def test_get_mutations(self) -> bool:
        """Test get mutations endpoint"""
        if not self.project_id:
            print_warning("No project ID available, skipping mutations test")
            return False
        
        print_info(f"Testing GET /api/results/{self.project_id}/mutations...")
        try:
            response = requests.get(
                f"{self.base_url}/results/{self.project_id}/mutations",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print_success(f"Mutations retrieved: {count}")
                return True
            else:
                print_error(f"Get mutations failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Get mutations error: {e}")
            return False
    
    def test_get_drugs(self) -> bool:
        """Test get drugs endpoint"""
        if not self.project_id:
            print_warning("No project ID available, skipping drugs test")
            return False
        
        print_info(f"Testing GET /api/results/{self.project_id}/drugs...")
        try:
            response = requests.get(
                f"{self.base_url}/results/{self.project_id}/drugs",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print_success(f"Drugs retrieved: {count}")
                return True
            else:
                print_error(f"Get drugs failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Get drugs error: {e}")
            return False
    
    def test_get_modifications(self) -> bool:
        """Test get modifications endpoint"""
        if not self.project_id:
            print_warning("No project ID available, skipping modifications test")
            return False
        
        print_info(f"Testing GET /api/results/{self.project_id}/modifications...")
        try:
            response = requests.get(
                f"{self.base_url}/results/{self.project_id}/modifications",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print_success(f"Modifications retrieved: {count}")
                return True
            else:
                print_error(f"Get modifications failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Get modifications error: {e}")
            return False
    
    def test_update_project(self) -> bool:
        """Test update project endpoint"""
        if not self.project_id:
            print_warning("No project ID available, skipping update project test")
            return False
        
        print_info(f"Testing PATCH /api/projects/{self.project_id}/status...")
        try:
            # Update project status (available endpoint)
            update_data = {
                "status": "Processing"
            }
            response = requests.patch(
                f"{self.base_url}/projects/{self.project_id}/status",
                json=update_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Project status updated: {data.get('status')}")
                return True
            else:
                print_error(f"Update project failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Update project error: {e}")
            return False
    
    def test_delete_project(self) -> bool:
        """Test delete project endpoint"""
        if not self.project_id:
            print_warning("No project ID available, skipping delete project test")
            return False
        
        print_info(f"Testing DELETE /api/projects/{self.project_id}...")
        try:
            response = requests.delete(
                f"{self.base_url}/projects/{self.project_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                print_success("Project deleted successfully")
                self.project_id = None  # Clear project ID
                return True
            elif response.status_code == 404:
                print_error("Project not found for deletion")
                return False
            elif response.status_code == 405:
                print_warning("Delete method not allowed (endpoint may need server restart)")
                return False
            else:
                print_error(f"Delete project failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Delete project error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all endpoint tests"""
        print_header("VIRO-AI BACKEND SYSTEM TEST")
        print_info(f"Base URL: {BASE_URL}")
        print_info(f"API Base: {API_BASE}\n")
        
        results = {}
        
        # 1. Health check
        results["health_check"] = self.test_health_check()
        if not results["health_check"]:
            print_error("\nBackend server is not running. Please start it first.")
            return results
        
        # 2. Authentication tests
        print_header("AUTHENTICATION ENDPOINTS")
        results["register"] = self.test_register_user()
        if not results["register"]:
            print_error("User registration/login failed. Cannot continue.")
            return results
        
        results["get_current_user"] = self.test_get_current_user()
        results["update_profile"] = self.test_update_profile()
        
        # 3. Project tests
        print_header("PROJECT ENDPOINTS")
        results["create_project"] = self.test_create_project()
        if not results["create_project"]:
            print_warning("Project creation failed. Some tests will be skipped.")
        
        results["list_projects"] = self.test_list_projects()
        results["get_project"] = self.test_get_project()
        results["get_project_status"] = self.test_get_project_status()
        results["update_project"] = self.test_update_project()
        
        # 4. Results endpoints
        print_header("RESULTS ENDPOINTS")
        results["get_project_results"] = self.test_get_project_results()
        results["get_mutations"] = self.test_get_mutations()
        results["get_drugs"] = self.test_get_drugs()
        results["get_modifications"] = self.test_get_modifications()
        
        # 5. Cleanup
        print_header("CLEANUP")
        results["delete_project"] = self.test_delete_project()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        failed = total - passed
        
        # Group by category
        auth_tests = ["register", "get_current_user", "update_profile"]
        project_tests = ["create_project", "list_projects", "get_project", "get_project_status", "update_project", "delete_project"]
        results_tests = ["get_project_results", "get_mutations", "get_drugs", "get_modifications"]
        
        print(f"\n{Colors.BOLD}Authentication Endpoints:{Colors.RESET}")
        for test in auth_tests:
            status = "[PASS]" if results.get(test) else "[FAIL]"
            color = Colors.GREEN if results.get(test) else Colors.RED
            print(f"  {color}{status}{Colors.RESET} - {test}")
        
        print(f"\n{Colors.BOLD}Project Endpoints:{Colors.RESET}")
        for test in project_tests:
            status = "[PASS]" if results.get(test) else "[FAIL]"
            color = Colors.GREEN if results.get(test) else Colors.RED
            print(f"  {color}{status}{Colors.RESET} - {test}")
        
        print(f"\n{Colors.BOLD}Results Endpoints:{Colors.RESET}")
        for test in results_tests:
            status = "[PASS]" if results.get(test) else "[FAIL]"
            color = Colors.GREEN if results.get(test) else Colors.RED
            print(f"  {color}{status}{Colors.RESET} - {test}")
        
        print(f"\n{Colors.BOLD}Overall:{Colors.RESET}")
        print(f"  Total Tests: {total}")
        print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
        print(f"  Success Rate: {(passed/total*100):.1f}%")
        
        if passed == total:
            print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] ALL TESTS PASSED!{Colors.RESET}")
        elif passed >= total * 0.8:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}[WARNING] MOST TESTS PASSED{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}[ERROR] SOME TESTS FAILED{Colors.RESET}")


def main():
    """Main test function"""
    tester = EndpointTester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Return exit code
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    if passed == total:
        return 0
    elif passed >= total * 0.8:
        return 1  # Warning
    else:
        return 2  # Error


if __name__ == "__main__":
    sys.exit(main())

