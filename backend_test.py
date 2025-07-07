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
    
    # Test creating a new event
    event_data = {
        "id": f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "title": "Test Incendio Boschivo",
        "description": "Incendio in zona boschiva, richiesto intervento immediato",
        "event_type": "incendio",
        "severity": "alta",
        "latitude": 45.4642,
        "longitude": 9.1900,
        "address": "Via Test, Milano",
        "notes": "Vento forte, situazione critica",
        "status": "aperto",
        "created_by": "admin",
        "resources_needed": []
    }
    
    event_id = tester.test_create_event(event_data)
    if not event_id:
        print("❌ Event creation failed")
    else:
        print(f"✅ Event created with ID: {event_id}")
    
    # Test creating events for map testing
    print("\n--- Testing Map Events Functionality ---")
    
    # Create test events with coordinates for map testing
    map_test_events = [
        {
            "id": f"map-test-1-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": "Incendio Duomo Milano",
            "description": "Incendio di grave entità presso il Duomo di Milano",
            "event_type": "incendio",
            "severity": "critica",
            "latitude": 45.4642,
            "longitude": 9.1900,
            "address": "Piazza del Duomo, Milano",
            "status": "aperto",
            "notes": "Evento di test per la mappa",
            "created_by": "admin",
            "resources_needed": []
        },
        {
            "id": f"map-test-2-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": "Alluvione Colosseo",
            "description": "Alluvione nei pressi del Colosseo",
            "event_type": "alluvione",
            "severity": "alta",
            "latitude": 41.8902,
            "longitude": 12.4922,
            "address": "Piazza del Colosseo, Roma",
            "status": "in_corso",
            "notes": "Evento di test per la mappa",
            "created_by": "admin",
            "resources_needed": []
        },
        {
            "id": f"map-test-3-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": "Blackout Firenze Centro",
            "description": "Interruzione di corrente nel centro storico",
            "event_type": "blackout",
            "severity": "media",
            "latitude": 43.7696,
            "longitude": 11.2558,
            "address": "Piazza della Signoria, Firenze",
            "status": "aperto",
            "notes": "Evento di test per la mappa",
            "created_by": "admin",
            "resources_needed": []
        }
    ]
    
    map_event_ids = []
    for event in map_test_events:
        event_id = tester.test_create_event(event)
        if event_id:
            map_event_ids.append(event_id)
            print(f"✅ Created map test event: {event['title']} with ID: {event_id}")
        else:
            print(f"❌ Failed to create map test event: {event['title']}")
    
    # Test getting map events
    if map_event_ids:
        # Test 1: Get all map events
        map_events = tester.test_get_map_events()
        
        # Test 2: Filter by status
        active_map_events = tester.test_get_map_events({"status": "active"})
        print(f"Active map events: {len(active_map_events)}")
        
        # Test 3: Filter by event type
        incendio_map_events = tester.test_get_map_events({"event_type": "incendio"})
        print(f"Incendio map events: {len(incendio_map_events)}")
        
        # Test 4: Filter by severity
        critica_map_events = tester.test_get_map_events({"severity": "critica"})
        print(f"Critical severity map events: {len(critica_map_events)}")
        
        # Test 5: Combined filters
        combined_map_events = tester.test_get_map_events({
            "status": "active",
            "event_type": "incendio"
        })
        print(f"Active incendio map events: {len(combined_map_events)}")
    else:
        print("❌ No map test events created, skipping map events tests")
    
    # Test getting operational logs
    logs = tester.test_get_logs()
    initial_log_count = len(logs)
    print(f"Initial log count: {initial_log_count}")
    
    # Test creating operational logs with different priorities
    # Test 1: Normal priority log without operator field (should be set automatically by backend)
    log_data_normal = {
        "action": "Controllo magazzino attrezzature",
        "details": "Verifica scorte attrezzature antincendio. Tutto in ordine, scorte sufficienti per 2 settimane",
        "priority": "normale",
        "event_id": event_id if event_id else None
        # No operator field - should be set automatically by backend
    }
    
    log_id_normal = tester.test_create_log(log_data_normal)
    if not log_id_normal:
        print("❌ Normal priority log creation failed")
    else:
        print(f"✅ Normal priority log created with ID: {log_id_normal}")
    
    # Test 2: High priority log without operator field
    log_data_high = {
        "action": "Aggiornamento emergenza incendio",
        "details": "Situazione sotto controllo, mezzi aerei in arrivo",
        "priority": "alta",
        "event_id": event_id if event_id else None
        # No operator field - should be set automatically by backend
    }
    
    log_id_high = tester.test_create_log(log_data_high)
    if not log_id_high:
        print("❌ High priority log creation failed")
    else:
        print(f"✅ High priority log created with ID: {log_id_high}")
    
    # Test 3: Low priority log without operator field
    log_data_low = {
        "action": "Routine di controllo",
        "details": "Controllo routine sistemi comunicazione",
        "priority": "bassa",
        "event_id": None
        # No operator field - should be set automatically by backend
    }
    
    log_id_low = tester.test_create_log(log_data_low)
    if not log_id_low:
        print("❌ Low priority log creation failed")
    else:
        print(f"✅ Low priority log created with ID: {log_id_low}")
    
    # Test getting logs again to verify the new logs are in the list
    updated_logs = tester.test_get_logs()
    if len(updated_logs) > initial_log_count:
        print(f"✅ Log count increased from {initial_log_count} to {len(updated_logs)}")
    else:
        print(f"❌ Log count did not increase as expected")
    
    # Test getting dashboard stats again to verify log count updated
    tester.test_get_dashboard_stats()
    
    # Test report functionality
    print("\n--- Testing Report Functionality ---")
    
    # Test getting report templates
    tester.test_get_report_templates()
    
    # Test generating PDF event report
    tester.test_generate_pdf_event_report()
    
    # Test generating Excel event report
    tester.test_generate_excel_event_report()
    
    # Test generating PDF log report
    tester.test_generate_pdf_log_report()
    
    # Test generating PDF statistics report
    tester.test_generate_pdf_statistics_report()
    
    # Test inventory management functionality
    print("\n--- Testing Inventory Management ---")
    
    # Test getting inventory items
    initial_inventory = tester.test_get_inventory()
    initial_inventory_count = len(initial_inventory)
    print(f"Initial inventory count: {initial_inventory_count}")
    
    # Test creating a new inventory item
    tomorrow = datetime.now() + timedelta(days=1)
    next_year = datetime.now() + timedelta(days=365)
    
    inventory_item_data = {
        "name": "Kit Pronto Soccorso",
        "category": "medicinali",
        "quantity": 25,
        "unit": "pz",
        "location": "Magazzino A, Scaffale 2",
        "min_quantity": 5,
        "max_quantity": 50,
        "expiry_date": next_year.strftime("%Y-%m-%d"),
        "supplier": "MedSupply Italia",
        "cost_per_unit": 45.50,
        "notes": "Kit completi per emergenze mediche"
    }
    
    item_id = tester.test_create_inventory_item(inventory_item_data)
    if not item_id:
        print("❌ Inventory item creation failed")
    else:
        print(f"✅ Inventory item created with ID: {item_id}")
        
        # Test getting the created item
        item = tester.test_get_inventory_item(item_id)
        if item:
            print(f"✅ Retrieved created inventory item")
        else:
            print(f"❌ Failed to retrieve created inventory item")
        
        # Test updating the item
        updated_item_data = inventory_item_data.copy()
        updated_item_data["quantity"] = 30
        updated_item_data["notes"] = "Kit completi per emergenze mediche - Aggiornato"
        
        if tester.test_update_inventory_item(item_id, updated_item_data):
            print(f"✅ Updated inventory item")
        else:
            print(f"❌ Failed to update inventory item")
        
        # Test updating quantity
        new_quantity = tester.test_update_inventory_quantity(
            item_id, 
            5, 
            "Aggiunta scorte da nuovo fornitore"
        )
        if new_quantity:
            print(f"✅ Updated inventory quantity to {new_quantity}")
        else:
            print(f"❌ Failed to update inventory quantity")
    
    # Test getting inventory with filters
    filtered_inventory = tester.test_get_inventory({"category": "medicinali"})
    print(f"Filtered inventory (medicinali): {len(filtered_inventory)} items")
    
    # Test getting inventory categories
    categories = tester.test_get_inventory_categories()
    print(f"Inventory categories: {categories}")
    
    # Test getting inventory locations
    locations = tester.test_get_inventory_locations()
    print(f"Inventory locations: {locations}")
    
    # Test getting inventory alerts
    alerts = tester.test_get_inventory_alerts()
    
    # Create an item that will trigger low stock alert
    low_stock_item_data = {
        "name": "Maschere Antipolvere",
        "category": "attrezzature",
        "quantity": 3,
        "unit": "pz",
        "location": "Magazzino B, Scaffale 1",
        "min_quantity": 10,
        "max_quantity": 50,
        "supplier": "Safety Equipment SRL",
        "notes": "Maschere per protezione da polveri sottili"
    }
    
    low_stock_item_id = tester.test_create_inventory_item(low_stock_item_data)
    if low_stock_item_id:
        print(f"✅ Created low stock item with ID: {low_stock_item_id}")
    
    # Create an item that will trigger expiry alert
    expiring_item_data = {
        "name": "Medicinali di Emergenza",
        "category": "medicinali",
        "quantity": 15,
        "unit": "pz",
        "location": "Magazzino A, Scaffale 3",
        "min_quantity": 5,
        "expiry_date": tomorrow.strftime("%Y-%m-%d"),
        "supplier": "Pharma Italia",
        "notes": "Medicinali per emergenze - PROSSIMI ALLA SCADENZA"
    }
    
    expiring_item_id = tester.test_create_inventory_item(expiring_item_data)
    if expiring_item_id:
        print(f"✅ Created expiring item with ID: {expiring_item_id}")
    
    # Check alerts again after creating items that should trigger alerts
    updated_alerts = tester.test_get_inventory_alerts()
    if updated_alerts.get('total_alerts', 0) > alerts.get('total_alerts', 0):
        print(f"✅ Alerts increased from {alerts.get('total_alerts', 0)} to {updated_alerts.get('total_alerts', 0)}")
    else:
        print(f"❌ Alerts did not increase as expected")
    
    # Test user management functionality (admin only)
    print("\n--- Testing User Management (Admin Only) ---")
    
    # Test getting admin stats
    admin_stats = tester.test_get_admin_stats()
    
    # Test getting all users
    users = tester.test_get_admin_users()
    initial_user_count = len(users)
    print(f"Initial user count: {initial_user_count}")
    
    # Test creating a new user
    test_username = f"operatore1_{datetime.now().strftime('%H%M%S')}"
    user_data = {
        "username": test_username,
        "full_name": "Mario Rossi",
        "email": f"{test_username}@emergency.local",
        "password": "password123",
        "role": "operator",
        "active": True
    }
    
    if tester.test_create_user(user_data):
        print(f"✅ Created user: {test_username}")
        
        # Test updating the user
        update_data = {
            "full_name": "Mario Rossi Updated",
            "role": "warehouse"
        }
        
        if tester.test_update_user(test_username, update_data):
            print(f"✅ Updated user: {test_username}")
        else:
            print(f"❌ Failed to update user: {test_username}")
        
        # Test resetting user password
        reset_message = tester.test_reset_user_password(test_username)
        if reset_message:
            print(f"✅ Reset password for user: {test_username}")
            print(f"Reset message: {reset_message}")
        else:
            print(f"❌ Failed to reset password for user: {test_username}")
        
        # Test deleting the user
        if tester.test_delete_user(test_username):
            print(f"✅ Deleted user: {test_username}")
        else:
            print(f"❌ Failed to delete user: {test_username}")
    else:
        print(f"❌ Failed to create user: {test_username}")
    
    # Test getting users again to verify changes
    updated_users = tester.test_get_admin_users()
    print(f"Final user count: {len(updated_users)}")
    
    # Test getting admin stats again
    updated_admin_stats = tester.test_get_admin_stats()
    
    # Clean up created inventory items
    print("\n--- Cleaning Up Test Data ---")
    for item_id in tester.created_inventory_items:
        if tester.test_delete_inventory_item(item_id):
            print(f"✅ Cleaned up inventory item: {item_id}")
        else:
            print(f"❌ Failed to clean up inventory item: {item_id}")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())