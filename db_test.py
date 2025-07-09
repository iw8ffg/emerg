import requests
import json
import time
from datetime import datetime

class DatabaseManagementTester:
    def __init__(self, base_url="https://272455ba-030f-4132-83b6-fa2f9889fad1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_info = None
        
        # Print the base URL being used
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
            "Login with admin credentials",
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
            print(f"New database: {response.get('database_name')}")
            print(f"Created new: {response.get('created_new')}")
        return success, response

    def run_database_tests(self):
        """Run all database management tests"""
        print("\n=== TESTING DATABASE MANAGEMENT ENDPOINTS ===")
        
        # Test 1: Get database configuration
        print("\n--- Testing GET /api/admin/database/config ---")
        config_success, config_response = self.test_database_config()
        
        if not config_success:
            print("❌ Database configuration endpoint failed, cannot continue tests")
            return False
        
        # Store original database info
        original_mongo_url = config_response.get('mongo_url')
        original_database_name = config_response.get('database_name')
        print(f"Original database: {original_database_name}")
        print(f"Original MongoDB URL: {original_mongo_url}")
        
        # Test 2: Get database status
        print("\n--- Testing GET /api/admin/database/status ---")
        status_success, status_response = self.test_database_status()
        
        if not status_success:
            print("❌ Database status endpoint failed")
        
        # Test 3: Test current database connection
        print("\n--- Testing POST /api/admin/database/test with current config ---")
        current_test_success, current_test_response = self.test_database_connection(
            original_mongo_url, 
            original_database_name
        )
        
        if not current_test_success or current_test_response.get('status') != 'success':
            print("❌ Database connection test with current config failed")
        
        # Test 4: Test connection with invalid MongoDB URL
        print("\n--- Testing POST /api/admin/database/test with invalid config ---")
        invalid_test_success, invalid_test_response = self.test_database_connection(
            "mongodb://invalid-host:27017", 
            original_database_name,
            2000  # Short timeout for faster test
        )
        
        if not invalid_test_success or invalid_test_response.get('status') != 'error':
            print("❌ Database connection test with invalid config failed")
        
        # Test 5: Update to a test database
        test_database_name = f"{original_database_name}_test"
        print(f"\n--- Testing POST /api/admin/database/update to {test_database_name} ---")
        update_success, update_response = self.test_database_update(
            original_mongo_url,
            test_database_name
        )
        
        if not update_success:
            print("❌ Database update endpoint failed")
            return False
        
        if update_response.get('status') != 'success':
            print(f"❌ Database update failed: {update_response.get('message')}")
            return False
        
        # Verify the database was switched
        print("\n--- Verifying database switch ---")
        verify_config_success, verify_config_response = self.test_database_config()
        
        if not verify_config_success:
            print("❌ Failed to verify database switch")
        else:
            current_db = verify_config_response.get('database_name')
            if current_db == test_database_name:
                print(f"✅ Successfully switched to {test_database_name}")
            else:
                print(f"❌ Failed to switch database. Still using: {current_db}")
        
        # Switch back to original database
        print(f"\n--- Switching back to original database {original_database_name} ---")
        switch_back_success, switch_back_response = self.test_database_update(
            original_mongo_url,
            original_database_name,
            test_connection=True,
            create_if_not_exists=False
        )
        
        if not switch_back_success or switch_back_response.get('status') != 'success':
            print(f"❌ Failed to switch back to original database: {switch_back_response.get('message')}")
            return False
        
        # Final verification
        final_verify_success, final_verify_response = self.test_database_config()
        
        if not final_verify_success:
            print("❌ Failed to verify final database state")
            return False
        
        final_db = final_verify_response.get('database_name')
        if final_db == original_database_name:
            print(f"✅ Successfully switched back to {original_database_name}")
        else:
            print(f"❌ Failed to switch back to original database. Currently using: {final_db}")
        
        # Print test summary
        print("\n=== DATABASE MANAGEMENT TEST SUMMARY ===")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run) * 100:.2f}%")
        
        return self.tests_passed == self.tests_run

def main():
    # Create tester instance
    tester = DatabaseManagementTester()
    
    # Login with admin credentials
    if not tester.test_login("admin", "admin123"):
        print("❌ Login failed, cannot continue tests")
        return 1
    
    # Run database management tests
    tester.run_database_tests()
    
    return 0

if __name__ == "__main__":
    main()