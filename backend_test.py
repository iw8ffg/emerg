import requests
import sys
import json
from datetime import datetime, timedelta

class EmergencySystemAPITester:
    def __init__(self, base_url="https://5f984545-e129-4cc2-a34a-9e9847a0f0a0.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_info = None
        self.created_logs = []
        self.created_events = []
        self.created_inventory_items = []
        self.created_users = []

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

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get current user info",
            "GET",
            "auth/me",
            200
        )
        if success:
            print(f"User info: {json.dumps(response, indent=2)}")
        return success

    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        success, response = self.run_test(
            "Get dashboard statistics",
            "GET",
            "dashboard/stats",
            200
        )
        if success:
            print(f"Dashboard stats: {json.dumps(response, indent=2)}")
        return success
        
    def test_get_report_templates(self):
        """Test getting report templates"""
        success, response = self.run_test(
            "Get report templates",
            "GET",
            "reports/templates",
            200
        )
        if success:
            print(f"Available report templates: {len(response.get('templates', {}))} templates")
            print(f"Available filter options: {list(response.get('filter_options', {}).keys())}")
        return success
        
    def test_generate_pdf_event_report(self):
        """Test generating PDF report for events"""
        report_data = {
            "report_type": "events",
            "format": "pdf",
            "start_date": "2025-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "event_type": "incendio"
        }
        
        # For this test, we need to check the content-type header
        url = f"{self.base_url}/api/reports/generate"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        print(f"\n🔍 Testing PDF Event Report generation...")
        self.tests_run += 1
        
        try:
            response = requests.post(url, json=report_data, headers=headers)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                content_type = response.headers.get('content-type')
                is_pdf = 'application/pdf' in content_type
                print(f"✅ Passed - Status: {response.status_code}, Content-Type: {content_type}")
                if is_pdf:
                    print(f"✅ Successfully generated PDF report ({len(response.content)} bytes)")
                else:
                    print(f"❌ Response is not a PDF: {content_type}")
                return success
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
            
    def test_generate_excel_event_report(self):
        """Test generating Excel report for events"""
        report_data = {
            "report_type": "events",
            "format": "excel",
            "start_date": "2025-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # For this test, we need to check the content-type header
        url = f"{self.base_url}/api/reports/generate"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        print(f"\n🔍 Testing Excel Event Report generation...")
        self.tests_run += 1
        
        try:
            response = requests.post(url, json=report_data, headers=headers)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                content_type = response.headers.get('content-type')
                is_excel = 'spreadsheetml' in content_type
                print(f"✅ Passed - Status: {response.status_code}, Content-Type: {content_type}")
                if is_excel:
                    print(f"✅ Successfully generated Excel report ({len(response.content)} bytes)")
                else:
                    print(f"❌ Response is not an Excel file: {content_type}")
                return success
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
            
    def test_generate_pdf_log_report(self):
        """Test generating PDF report for operational logs"""
        report_data = {
            "report_type": "logs",
            "format": "pdf",
            "start_date": "2025-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "priority": "normale",
            "operator": "admin"
        }
        
        url = f"{self.base_url}/api/reports/generate"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        print(f"\n🔍 Testing PDF Log Report generation...")
        self.tests_run += 1
        
        try:
            response = requests.post(url, json=report_data, headers=headers)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                content_type = response.headers.get('content-type')
                is_pdf = 'application/pdf' in content_type
                print(f"✅ Passed - Status: {response.status_code}, Content-Type: {content_type}")
                if is_pdf:
                    print(f"✅ Successfully generated PDF log report ({len(response.content)} bytes)")
                else:
                    print(f"❌ Response is not a PDF: {content_type}")
                return success
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
            
    def test_generate_pdf_statistics_report(self):
        """Test generating PDF report for statistics"""
        report_data = {
            "report_type": "statistics",
            "format": "pdf"
        }
        
        url = f"{self.base_url}/api/reports/generate"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        print(f"\n🔍 Testing PDF Statistics Report generation...")
        self.tests_run += 1
        
        try:
            response = requests.post(url, json=report_data, headers=headers)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                content_type = response.headers.get('content-type')
                is_pdf = 'application/pdf' in content_type
                print(f"✅ Passed - Status: {response.status_code}, Content-Type: {content_type}")
                if is_pdf:
                    print(f"✅ Successfully generated PDF statistics report ({len(response.content)} bytes)")
                else:
                    print(f"❌ Response is not a PDF: {content_type}")
                return success
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_get_events(self):
        """Test getting events list"""
        success, response = self.run_test(
            "Get events list",
            "GET",
            "events",
            200
        )
        if success:
            print(f"Retrieved {len(response)} events")
            if len(response) > 0:
                print(f"First event: {json.dumps(response[0], indent=2)}")
            return response
        return []
        
    def test_get_map_events(self, params=None):
        """Test getting events for map display with optional filters"""
        endpoint = "events/map"
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"events/map?{query_params}"
            
        success, response = self.run_test(
            f"Get map events {params if params else ''}",
            "GET",
            endpoint,
            200
        )
        if success:
            events = response.get('events', [])
            print(f"Retrieved {len(events)} events for map display")
            if len(events) > 0:
                print(f"First map event: {json.dumps(events[0], indent=2)}")
                
                # Verify event structure for map
                required_fields = ['id', 'title', 'description', 'event_type', 'severity', 
                                  'status', 'latitude', 'longitude', 'created_at']
                missing_fields = [field for field in required_fields if field not in events[0]]
                
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                else:
                    print(f"✅ All required fields present in map events")
                    
            return events
        return []

    def test_create_event(self, event_data):
        """Test creating a new event"""
        success, response = self.run_test(
            "Create new emergency event",
            "POST",
            "events",
            200,
            data=event_data
        )
        if success:
            print(f"Event created: {json.dumps(response, indent=2)}")
            event_id = response.get('event_id')
            if event_id:
                self.created_events.append(event_id)
            return event_id
        return None

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health check",
            "GET",
            "health",
            200
        )
        return success
        
    def test_get_logs(self):
        """Test getting operational logs"""
        success, response = self.run_test(
            "Get operational logs",
            "GET",
            "logs",
            200
        )
        if success:
            print(f"Retrieved {len(response)} operational logs")
            if len(response) > 0:
                print(f"First log: {json.dumps(response[0], indent=2)}")
            return response
        return []
        
    def test_create_log(self, log_data):
        """Test creating a new operational log"""
        success, response = self.run_test(
            "Create new operational log",
            "POST",
            "logs",
            200,
            data=log_data
        )
        if success:
            print(f"Log created: {json.dumps(response, indent=2)}")
            log_id = response.get('log_id')
            if log_id:
                self.created_logs.append(log_id)
            return log_id
        return None
        
    # Inventory Management Tests
    def test_get_inventory(self, params=None):
        """Test getting inventory items with optional filters"""
        endpoint = "inventory"
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"inventory?{query_params}"
            
        success, response = self.run_test(
            f"Get inventory items {params if params else ''}",
            "GET",
            endpoint,
            200
        )
        if success:
            print(f"Retrieved {len(response)} inventory items")
            if len(response) > 0:
                print(f"First item: {json.dumps(response[0], indent=2)}")
            return response
        return []
    
    def test_create_inventory_item(self, item_data):
        """Test creating a new inventory item"""
        success, response = self.run_test(
            "Create new inventory item",
            "POST",
            "inventory",
            200,
            data=item_data
        )
        if success:
            print(f"Inventory item created: {json.dumps(response, indent=2)}")
            item_id = response.get('item_id')
            if item_id:
                self.created_inventory_items.append(item_id)
            return item_id
        return None
    
    def test_get_inventory_item(self, item_id):
        """Test getting a specific inventory item"""
        success, response = self.run_test(
            f"Get inventory item {item_id}",
            "GET",
            f"inventory/{item_id}",
            200
        )
        if success:
            print(f"Retrieved inventory item: {json.dumps(response, indent=2)}")
            return response
        return None
    
    def test_update_inventory_item(self, item_id, item_data):
        """Test updating an inventory item"""
        success, response = self.run_test(
            f"Update inventory item {item_id}",
            "PUT",
            f"inventory/{item_id}",
            200,
            data=item_data
        )
        if success:
            print(f"Inventory item updated: {json.dumps(response, indent=2)}")
            return True
        return False
    
    def test_delete_inventory_item(self, item_id):
        """Test deleting an inventory item"""
        success, response = self.run_test(
            f"Delete inventory item {item_id}",
            "DELETE",
            f"inventory/{item_id}",
            200
        )
        if success:
            print(f"Inventory item deleted: {json.dumps(response, indent=2)}")
            if item_id in self.created_inventory_items:
                self.created_inventory_items.remove(item_id)
            return True
        return False
    
    def test_update_inventory_quantity(self, item_id, quantity_change, reason, location=None):
        """Test updating inventory quantity"""
        data = {
            "quantity_change": quantity_change,
            "reason": reason
        }
        if location:
            data["location"] = location
            
        success, response = self.run_test(
            f"Update inventory quantity for item {item_id}",
            "POST",
            f"inventory/{item_id}/update-quantity",
            200,
            data=data
        )
        if success:
            print(f"Inventory quantity updated: {json.dumps(response, indent=2)}")
            return response.get('new_quantity')
        return None
    
    def test_get_inventory_categories(self):
        """Test getting inventory categories"""
        success, response = self.run_test(
            "Get inventory categories",
            "GET",
            "inventory/categories",
            200
        )
        if success:
            print(f"Retrieved categories: {json.dumps(response, indent=2)}")
            return response.get('categories', [])
        return []
    
    def test_get_inventory_locations(self):
        """Test getting inventory locations"""
        success, response = self.run_test(
            "Get inventory locations",
            "GET",
            "inventory/locations",
            200
        )
        if success:
            print(f"Retrieved locations: {json.dumps(response, indent=2)}")
            return response.get('locations', [])
        return []
    
    def test_get_inventory_alerts(self):
        """Test getting inventory alerts"""
        success, response = self.run_test(
            "Get inventory alerts",
            "GET",
            "inventory/alerts",
            200
        )
        if success:
            print(f"Retrieved alerts: {json.dumps(response, indent=2)}")
            print(f"Low stock items: {len(response.get('low_stock_items', []))}")
            print(f"Expiring items: {len(response.get('expiring_items', []))}")
            print(f"Total alerts: {response.get('total_alerts', 0)}")
            return response
        return {}
    
    # User Management Tests
    def test_get_admin_users(self):
        """Test getting all users (admin only)"""
        success, response = self.run_test(
            "Get all users (admin only)",
            "GET",
            "admin/users",
            200
        )
        if success:
            print(f"Retrieved {len(response)} users")
            if len(response) > 0:
                print(f"First user: {json.dumps(response[0], indent=2)}")
            return response
        return []
    
    def test_create_user(self, user_data):
        """Test creating a new user (admin only)"""
        success, response = self.run_test(
            "Create new user (admin only)",
            "POST",
            "admin/users",
            200,
            data=user_data
        )
        if success:
            print(f"User created: {json.dumps(response, indent=2)}")
            if user_data.get('username'):
                self.created_users.append(user_data['username'])
            return True
        return False
    
    def test_update_user(self, username, user_data):
        """Test updating a user (admin only)"""
        success, response = self.run_test(
            f"Update user {username} (admin only)",
            "PUT",
            f"admin/users/{username}",
            200,
            data=user_data
        )
        if success:
            print(f"User updated: {json.dumps(response, indent=2)}")
            return True
        return False
    
    def test_delete_user(self, username):
        """Test deleting a user (admin only)"""
        success, response = self.run_test(
            f"Delete user {username} (admin only)",
            "DELETE",
            f"admin/users/{username}",
            200
        )
        if success:
            print(f"User deleted: {json.dumps(response, indent=2)}")
            if username in self.created_users:
                self.created_users.remove(username)
            return True
        return False
    
    def test_reset_user_password(self, username):
        """Test resetting a user's password (admin only)"""
        success, response = self.run_test(
            f"Reset password for user {username} (admin only)",
            "POST",
            f"admin/users/{username}/reset-password",
            200
        )
        if success:
            print(f"Password reset: {json.dumps(response, indent=2)}")
            return response.get('message')
        return None
    
    def test_get_admin_stats(self):
        """Test getting admin statistics (admin only)"""
        success, response = self.run_test(
            "Get admin statistics (admin only)",
            "GET",
            "admin/stats",
            200
        )
        if success:
            print(f"Admin stats: {json.dumps(response, indent=2)}")
            return response
        return {}

def main():
    # Setup
    tester = EmergencySystemAPITester()
    
    print("\n=== TESTING AUTOMATIC INITIALIZATION FUNCTIONALITY ===")
    
    # Test health check to verify the system is running
    print("\n--- Testing System Health ---")
    if tester.test_health_check():
        print("✅ System is running and healthy")
    else:
        print("❌ System health check failed")
        return 1
    
    # Test login with admin credentials (should be automatically created)
    print("\n--- Testing Admin Login with Auto-Created Credentials ---")
    if not tester.test_login("admin", "admin123"):
        print("❌ Login with auto-created admin credentials failed, initialization may not have worked")
        return 1
    else:
        print("✅ Successfully logged in with auto-created admin credentials")
        print("✅ Admin user was automatically created during initialization")

    # Test getting current user info to verify admin role
    print("\n--- Verifying Admin User Role ---")
    if tester.test_get_current_user():
        print("✅ Admin user has correct permissions")
    else:
        print("❌ Failed to verify admin user permissions")
    
    # Test getting dashboard stats to verify database initialization
    print("\n--- Verifying Database Initialization ---")
    tester.test_get_dashboard_stats()
    
    # Test getting users to verify sample users were created
    print("\n--- Verifying Sample Users Creation ---")
    users = tester.test_get_admin_users()
    
    # Check for expected sample users
    expected_users = ["admin", "coordinatore1", "operatore1", "magazziniere1"]
    found_users = [user.get("username") for user in users]
    
    for username in expected_users:
        if username in found_users:
            print(f"✅ Sample user '{username}' was automatically created")
        else:
            print(f"❌ Sample user '{username}' was not found")
    
    # Test login with sample user credentials
    print("\n--- Testing Sample User Credentials ---")
    
    # Save admin token for later
    admin_token = tester.token
    
    # Test coordinatore1 login
    coord_tester = EmergencySystemAPITester()
    if coord_tester.test_login("coordinatore1", "coord123"):
        print("✅ Successfully logged in with coordinatore1 credentials")
    else:
        print("❌ Login with coordinatore1 credentials failed")
    
    # Test operatore1 login
    oper_tester = EmergencySystemAPITester()
    if oper_tester.test_login("operatore1", "oper123"):
        print("✅ Successfully logged in with operatore1 credentials")
    else:
        print("❌ Login with operatore1 credentials failed")
    
    # Test magazziniere1 login
    magaz_tester = EmergencySystemAPITester()
    if magaz_tester.test_login("magazziniere1", "magaz123"):
        print("✅ Successfully logged in with magazziniere1 credentials")
    else:
        print("❌ Login with magazziniere1 credentials failed")
    
    # Restore admin token
    tester.token = admin_token
    
    # Test getting inventory to verify sample inventory items
    print("\n--- Verifying Sample Inventory Items ---")
    inventory = tester.test_get_inventory()
    
    if len(inventory) > 0:
        print(f"✅ Found {len(inventory)} sample inventory items")
        
        # Check for expected categories
        categories = tester.test_get_inventory_categories()
        if categories:
            print(f"✅ Inventory categories initialized: {categories}")
        
        # Check for expected locations
        locations = tester.test_get_inventory_locations()
        if locations:
            print(f"✅ Inventory locations initialized: {locations}")
    else:
        print("❌ No sample inventory items found")
    
    # Test getting resources to verify sample trained resources
    print("\n--- Verifying Sample Trained Resources ---")
    success, resources = tester.run_test(
        "Get trained resources",
        "GET",
        "resources",
        200
    )
    
    if success and len(resources) > 0:
        print(f"✅ Found {len(resources)} sample trained resources")
        print(f"Sample resource: {resources[0]['full_name']} ({resources[0]['role']})")
    else:
        print("❌ No sample trained resources found")
    
    # Test getting logs to verify initialization log
    print("\n--- Verifying Initialization Log ---")
    logs = tester.test_get_logs()
    
    init_logs = [log for log in logs if "Inizializzazione Sistema" in log.get("action", "")]
    if init_logs:
        print(f"✅ Found initialization log: {init_logs[0]['action']}")
        print(f"   Details: {init_logs[0]['details']}")
    else:
        print("❌ No initialization log found")
    
    # Print summary of database initialization
    print("\n=== DATABASE INITIALIZATION SUMMARY ===")
    stats = tester.test_get_dashboard_stats()
    
    print(f"✅ Users: {len(users)}")
    print(f"✅ Inventory Items: {stats.get('inventory_items', 0)}")
    print(f"✅ Trained Resources: {stats.get('trained_resources', 0)}")
    print(f"✅ Operational Logs: {stats.get('total_logs', 0)}")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())