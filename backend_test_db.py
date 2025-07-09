import requests
import json
import time
from datetime import datetime

class EmergencySystemAPITester:
    def __init__(self, base_url="https://272455ba-030f-4132-83b6-fa2f9889fad1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_info = None
        
        print(f"Using API base URL: {self.base_url}")
        
        # Test the base URL with a health check
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print(f"✅ API is accessible at {self.base_url}")
            else:
                print(f"⚠️ API returned status code {response.status_code} at {self.base_url}")
        except Exception as e:
            print(f"⚠️ Error connecting to API at {self.base_url}: {str(e)}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self, username, password):
        """Test login and get token"""
        success, response = self.run_test(
            f"Login with {username}",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_info = response.get('user', {})
            print(f"Logged in as: {self.user_info.get('username')} (Role: {self.user_info.get('role')})")
            return True
        return False

    def test_database_config(self):
        """Test getting database configuration"""
        success, response = self.run_test(
            "Get database configuration",
            "GET",
            "admin/database/config",
            200
        )
        if success:
            print(f"Current database: {response.get('database_name')}")
            print(f"MongoDB URL: {response.get('mongo_url')}")
            print(f"Collections: {response.get('collections')}")
        return success, response

    def test_database_connection(self, mongo_url, database_name, connection_timeout=5000):
        """Test database connection"""
        data = {
            "mongo_url": mongo_url,
            "database_name": database_name,
            "connection_timeout": connection_timeout
        }
        success, response = self.run_test(
            f"Test database connection to {database_name}",
            "POST",
            "admin/database/test",
            200,
            data=data
        )
        if success:
            print(f"Status: {response.get('status')}")
            print(f"Message: {response.get('message')}")
        return success, response

    def test_database_status(self):
        """Test getting database status"""
        success, response = self.run_test(
            "Get database status",
            "GET",
            "admin/database/status",
            200
        )
        if success:
            print(f"Server version: {response.get('server_version')}")
            print(f"Uptime: {response.get('uptime')} seconds")
            print(f"Total documents: {response.get('total_documents')}")
            print(f"Collections: {len(response.get('collections', {}))} collections")
        return success, response

    def test_database_update(self, mongo_url, database_name, test_connection=True, create_if_not_exists=True):
        """Test updating database configuration"""
        data = {
            "mongo_url": mongo_url,
            "database_name": database_name,
            "test_connection": test_connection,
            "create_if_not_exists": create_if_not_exists
        }
        success, response = self.run_test(
            f"Update database to {database_name}",
            "POST",
            "admin/database/update",
            200,
            data=data
        )
        if success:
            print(f"Status: {response.get('status')}")
            print(f"Message: {response.get('message')}")
            if response.get('status') == 'success':
                print(f"New database: {response.get('database_name')}")
                print(f"Created new: {response.get('created_new')}")
            else:
                print(f"Error: {response.get('message')}")
        return success, response

    def test_database_management(self):
        """Test all database management endpoints"""
        print("\n=== TESTING DATABASE MANAGEMENT ENDPOINTS ===")
        
        # Test 1: Get database configuration
        print("\n--- Test 1: GET /api/admin/database/config ---")
        config_success, config_response = self.test_database_config()
        if not config_success:
            print("❌ Database configuration endpoint failed")
            return False
        
        original_mongo_url = config_response.get('mongo_url')
        original_database_name = config_response.get('database_name')
        
        # Test 2: Get database status
        print("\n--- Test 2: GET /api/admin/database/status ---")
        status_success, _ = self.test_database_status()
        if not status_success:
            print("❌ Database status endpoint failed")
        
        # Test 3: Test database connection with valid config
        print("\n--- Test 3: POST /api/admin/database/test with valid config ---")
        valid_test_success, valid_test_response = self.test_database_connection(
            original_mongo_url, 
            original_database_name
        )
        if not valid_test_success or valid_test_response.get('status') != 'success':
            print("❌ Database connection test with valid config failed")
        
        # Test 4: Test database connection with invalid config
        print("\n--- Test 4: POST /api/admin/database/test with invalid config ---")
        invalid_test_success, invalid_test_response = self.test_database_connection(
            "mongodb://invalid-host:27017", 
            original_database_name,
            2000  # Short timeout for faster test
        )
        if not invalid_test_success or invalid_test_response.get('status') != 'error':
            print("❌ Database connection test with invalid config failed")
        
        # Test 5: Update to a test database
        test_database_name = f"{original_database_name}_test"
        print(f"\n--- Test 5: POST /api/admin/database/update to {test_database_name} ---")
        update_success, update_response = self.test_database_update(
            original_mongo_url,
            test_database_name
        )
        if not update_success or update_response.get('status') != 'success':
            print("❌ Database update endpoint failed")
        else:
            # Re-authenticate after database switch
            print("\n--- Re-authenticating after database switch ---")
            if not self.test_login("admin", "admin123"):
                print("⚠️ Login with admin failed after database switch, trying testadmin...")
                if not self.test_login("testadmin", "testadmin123"):
                    print("❌ All login attempts failed after database switch")
                    return False
            
            # Verify the database was switched
            verify_config_success, verify_config_response = self.test_database_config()
            if verify_config_success:
                current_db = verify_config_response.get('database_name')
                if current_db == test_database_name:
                    print(f"✅ Successfully switched to {test_database_name}")
                else:
                    print(f"❌ Failed to switch database. Still using: {current_db}")
            
            # Switch back to original database
            print(f"\n--- Switching back to original database {original_database_name} ---")
            switch_back_success, switch_back_response = self.test_database_update(
                original_mongo_url,
                original_database_name
            )
            if not switch_back_success or switch_back_response.get('status') != 'success':
                print(f"❌ Failed to switch back to original database")
            
            # Re-authenticate after switching back
            print("\n--- Re-authenticating after switching back ---")
            if not self.test_login("testadmin", "testadmin123"):
                print("⚠️ Login with testadmin failed after switching back, trying admin...")
                if not self.test_login("admin", "admin123"):
                    print("❌ All login attempts failed after switching back")
                    return False
        
        # Print findings
        print("\n=== DATABASE MANAGEMENT FINDINGS ===")
        print("1. GET /api/admin/database/config endpoint: " + ("✅ Working" if config_success else "❌ Not working"))
        print("2. GET /api/admin/database/status endpoint: " + ("✅ Working" if status_success else "❌ Not working"))
        print("3. POST /api/admin/database/test endpoint: " + ("✅ Working" if valid_test_success else "❌ Not working"))
        print("4. POST /api/admin/database/update endpoint: " + ("✅ Working" if update_success else "❌ Not working"))
        print("\n5. Database switch functionality: " + ("✅ Working but requires re-authentication" if update_success else "❌ Not working"))
        print("   - When switching databases, the current authentication token becomes invalid")
        print("   - This is because user information is stored in the database")
        print("   - After switching, you need to re-authenticate with credentials valid in the new database")
        print("   - The frontend should handle re-authentication after database switch")
        
        return True

def main():
    # Create tester instance
    tester = EmergencySystemAPITester()
    
    # Login with admin credentials
    print("\n--- Authenticating with admin credentials ---")
    if not tester.test_login("testadmin", "testadmin123"):
        print("⚠️ Login with testadmin failed, trying admin...")
        if not tester.test_login("admin", "admin123"):
            print("❌ Login failed, cannot continue tests")
            return 1
    
    # Test database management endpoints
    tester.test_database_management()
    
    # Print test summary
    print("\n=== TEST SUMMARY ===")
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run) * 100:.2f}%")
    
    return 0

if __name__ == "__main__":
    main()