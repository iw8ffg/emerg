import requests
import json
import time
from datetime import datetime

class DatabaseSwitchRealWorldTester:
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

    def test_real_world_scenario(self):
        """Test a real-world scenario of switching from emergency_management to emergency_management_test"""
        print("\n=== TESTING REAL-WORLD DATABASE SWITCH SCENARIO ===")
        
        # Step 1: Login with admin credentials
        print("\n--- Step 1: Login with admin credentials ---")
        if not self.test_login("testadmin", "testadmin123"):
            print("⚠️ Login with testadmin failed, trying admin...")
            if not self.test_login("admin", "admin123"):
                print("❌ Login failed, cannot continue tests")
                return False
        
        # Step 2: Get current database configuration
        print("\n--- Step 2: Get current database configuration ---")
        config_success, config_response = self.test_database_config()
        if not config_success:
            print("❌ Database configuration endpoint failed, cannot continue tests")
            return False
        
        original_mongo_url = config_response.get('mongo_url')
        original_database_name = config_response.get('database_name')
        print(f"Original database: {original_database_name}")
        
        # Step 3: Switch to emergency_management_test database
        target_database = "emergency_management_test"
        print(f"\n--- Step 3: Switch to {target_database} database ---")
        update_success, update_response = self.test_database_update(
            original_mongo_url,
            target_database,
            test_connection=True,
            create_if_not_exists=True
        )
        
        if not update_success:
            print("❌ Database update endpoint failed")
            return False
        
        if update_response.get('status') != 'success':
            print(f"❌ Database update failed: {update_response.get('message')}")
            return False
        
        # Step 4: Re-authenticate after database switch
        print("\n--- Step 4: Re-authenticate after database switch ---")
        if not self.test_login("admin", "admin123"):
            print("⚠️ Login with admin failed after database switch, trying testadmin...")
            if not self.test_login("testadmin", "testadmin123"):
                print("❌ All login attempts failed after database switch")
                return False
        
        # Step 5: Verify the database was switched
        print("\n--- Step 5: Verify the database was switched ---")
        verify_config_success, verify_config_response = self.test_database_config()
        
        if not verify_config_success:
            print("❌ Failed to verify database switch")
            return False
        
        current_db = verify_config_response.get('database_name')
        if current_db == target_database:
            print(f"✅ Successfully switched to {target_database}")
        else:
            print(f"❌ Failed to switch database. Still using: {current_db}")
            return False
        
        # Step 6: Switch back to original database
        print(f"\n--- Step 6: Switch back to original database {original_database_name} ---")
        switch_back_success, switch_back_response = self.test_database_update(
            original_mongo_url,
            original_database_name,
            test_connection=True,
            create_if_not_exists=False
        )
        
        if not switch_back_success:
            print("❌ Database update endpoint failed when switching back")
            return False
        
        if switch_back_response.get('status') != 'success':
            print(f"❌ Database update failed when switching back: {switch_back_response.get('message')}")
            return False
        
        # Step 7: Re-authenticate after switching back
        print("\n--- Step 7: Re-authenticate after switching back ---")
        if not self.test_login("testadmin", "testadmin123"):
            print("⚠️ Login with testadmin failed after switching back, trying admin...")
            if not self.test_login("admin", "admin123"):
                print("❌ All login attempts failed after switching back")
                return False
        
        # Step 8: Final verification
        print("\n--- Step 8: Final verification ---")
        final_verify_success, final_verify_response = self.test_database_config()
        
        if not final_verify_success:
            print("❌ Failed to verify final database state")
            return False
        
        final_db = final_verify_response.get('database_name')
        if final_db == original_database_name:
            print(f"✅ Successfully switched back to {original_database_name}")
        else:
            print(f"❌ Failed to switch back to original database. Currently using: {final_db}")
            return False
        
        # Print test summary
        print("\n=== REAL-WORLD DATABASE SWITCH TEST SUMMARY ===")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run) * 100:.2f}%")
        
        # Print findings
        print("\n=== FINDINGS ===")
        print("1. Database switch functionality is working correctly")
        print("2. The issue is with authentication after switching databases:")
        print("   - When switching to a new database, the current authentication token becomes invalid")
        print("   - This is because user information is stored in the database")
        print("   - After switching, you need to re-authenticate with credentials valid in the new database")
        print("3. Recommendation: The frontend should handle re-authentication after database switch")
        print("   - After a successful database switch, the frontend should prompt the user to login again")
        print("   - This ensures the user has valid credentials in the new database")
        
        return True

def main():
    # Create tester instance
    tester = DatabaseSwitchRealWorldTester()
    
    # Test real-world scenario
    tester.test_real_world_scenario()
    
    return 0

if __name__ == "__main__":
    main()