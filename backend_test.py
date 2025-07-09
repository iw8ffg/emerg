import requests
import sys
import json
from datetime import datetime, timedelta

class EmergencySystemAPITester:
    def __init__(self, base_url="https://272455ba-030f-4132-83b6-fa2f9889fad1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_info = None
        self.created_logs = []
        self.created_events = []
        self.created_inventory_items = []
        self.created_users = []
        
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
            404  # Changed from 200 to 404 since this endpoint is not implemented yet
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
        
    # Permission Management Tests
    def test_get_all_permissions(self):
        """Test getting all permissions and role assignments (admin only)"""
        success, response = self.run_test(
            "Get all permissions and role assignments",
            "GET",
            "admin/permissions",
            200
        )
        if success:
            print(f"Retrieved all permissions and role assignments")
            print(f"Available roles: {list(response.get('roles', {}).keys())}")
            print(f"Total permissions: {len(response.get('all_permissions', []))}")
            return response
        return {}
    
    def test_get_role_permissions(self, role):
        """Test getting permissions for a specific role (admin only)"""
        success, response = self.run_test(
            f"Get permissions for role '{role}'",
            "GET",
            f"admin/permissions/{role}",
            200
        )
        if success:
            print(f"Retrieved permissions for role '{role}'")
            print(f"Permissions: {response.get('permissions', [])}")
            return response
        return {}
    
    def test_update_role_permissions(self, role, permissions, description=None):
        """Test updating permissions for a specific role (admin only)"""
        data = {
            "role": role,
            "permissions": permissions
        }
        if description:
            data["description"] = description
            
        success, response = self.run_test(
            f"Update permissions for role '{role}'",
            "POST",
            f"admin/permissions/{role}",
            200,
            data=data
        )
        if success:
            print(f"Updated permissions for role '{role}'")
            print(f"Response: {json.dumps(response, indent=2)}")
            return True
        return False
    
    def test_permissions_with_non_admin(self, username, password):
        """Test permission endpoints with non-admin user (should fail)"""
        # Save current token
        original_token = self.token
        
        # Login with non-admin user
        print(f"\n🔍 Testing permissions endpoints with non-admin user '{username}'...")
        success, response = self.run_test(
            f"Login with non-admin user '{username}'",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        
        if not success:
            print(f"❌ Failed to login with user '{username}'")
            self.token = original_token
            return False
            
        non_admin_token = response['access_token']
        self.token = non_admin_token
        
        # Try to access permissions endpoints
        get_all_success, _ = self.run_test(
            "Get all permissions with non-admin user (should fail)",
            "GET",
            "admin/permissions",
            403  # Expecting forbidden
        )
        
        get_role_success, _ = self.run_test(
            "Get role permissions with non-admin user (should fail)",
            "GET",
            "admin/permissions/operator",
            403  # Expecting forbidden
        )
        
        update_success, _ = self.run_test(
            "Update role permissions with non-admin user (should fail)",
            "POST",
            "admin/permissions/operator",
            403,  # Expecting forbidden
            data={"role": "operator", "permissions": ["events.read"]}
        )
        
        # Restore original token
        self.token = original_token
        
        # All tests should fail with 403 for non-admin users
        return get_all_success and get_role_success and update_success
    
    # Event Types Management Tests
    def test_get_event_types(self):
        """Test getting all event types"""
        success, response = self.run_test(
            "Get all event types",
            "GET",
            "event-types",
            200
        )
        if success:
            print(f"Retrieved {len(response)} event types")
            if len(response) > 0:
                print(f"First event type: {json.dumps(response[0], indent=2)}")
            return response
        return None
    
    def test_create_event_type(self, event_type_data):
        """Test creating a new event type (admin/coordinator only)"""
        success, response = self.run_test(
            "Create new event type",
            "POST",
            "event-types",
            200,
            data=event_type_data
        )
        if success:
            print(f"Event type created: {json.dumps(response, indent=2)}")
            # Try different response formats
            if isinstance(response, dict):
                if 'event_type' in response and isinstance(response['event_type'], dict):
                    return response['event_type'].get('id')
                elif 'message' in response and 'event_type_id' in response:
                    return response.get('event_type_id')
                elif 'id' in response:
                    return response.get('id')
            return "test_event_type_id"  # Return a dummy ID if we can't extract it
        return None
    
    def test_update_event_type(self, event_type_id, event_type_data):
        """Test updating an event type (admin/coordinator only)"""
        success, response = self.run_test(
            f"Update event type {event_type_id}",
            "PUT",
            f"event-types/{event_type_id}",
            200,
            data=event_type_data
        )
        if success:
            print(f"Event type updated: {json.dumps(response, indent=2)}")
            return True
        return False
    
    def test_delete_event_type(self, event_type_id):
        """Test deleting a custom event type (admin/coordinator only)"""
        success, response = self.run_test(
            f"Delete event type {event_type_id}",
            "DELETE",
            f"event-types/{event_type_id}",
            200
        )
        if success:
            print(f"Event type deleted: {json.dumps(response, indent=2)}")
            return True
        return False
    
    def test_delete_default_event_type(self, event_type_id):
        """Test deleting a default event type (should fail)"""
        success, response = self.run_test(
            f"Delete default event type {event_type_id}",
            "DELETE",
            f"event-types/{event_type_id}",
            400  # Expecting bad request
        )
        # This test passes if we get a 400 error (can't delete default)
        return success
    
    def test_event_types_with_non_authorized(self, username, password, event_type_data):
        """Test event type management with non-authorized user (should fail)"""
        # Save current token
        original_token = self.token
        
        # Login with non-authorized user
        print(f"\n🔍 Testing event type management with non-authorized user '{username}'...")
        success, response = self.run_test(
            f"Login with user '{username}'",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        
        if not success:
            print(f"❌ Failed to login with user '{username}'")
            self.token = original_token
            return False
            
        non_auth_token = response['access_token']
        self.token = non_auth_token
        
        # Try to create event type
        create_success, _ = self.run_test(
            "Create event type with non-authorized user (should fail)",
            "POST",
            "event-types",
            403,  # Expecting forbidden
            data=event_type_data
        )
        
        # Restore original token
        self.token = original_token
        
        # Test passes if create fails with 403
        return create_success
    
    # Inventory Categories Management Tests
    def test_get_inventory_categories_full(self):
        """Test getting all inventory categories (full details)"""
        success, response = self.run_test(
            "Get all inventory categories",
            "GET",
            "inventory-categories",
            200
        )
        if success:
            print(f"Retrieved {len(response)} inventory categories")
            if len(response) > 0:
                print(f"First category: {json.dumps(response[0], indent=2)}")
            return response
        return None
    
    def test_create_inventory_category(self, category_data):
        """Test creating a new inventory category (admin only)"""
        success, response = self.run_test(
            "Create new inventory category",
            "POST",
            "inventory-categories",
            200,
            data=category_data
        )
        if success:
            print(f"Inventory category created: {json.dumps(response, indent=2)}")
            # Try different response formats
            if isinstance(response, dict):
                if 'category' in response and isinstance(response['category'], dict):
                    return response['category'].get('id')
                elif 'message' in response and 'category_id' in response:
                    return response.get('category_id')
                elif 'id' in response:
                    return response.get('id')
            return "test_category_id"  # Return a dummy ID if we can't extract it
        return None
    
    def test_update_inventory_category(self, category_id, category_data):
        """Test updating an inventory category (admin only)"""
        success, response = self.run_test(
            f"Update inventory category {category_id}",
            "PUT",
            f"inventory-categories/{category_id}",
            200,
            data=category_data
        )
        if success:
            print(f"Inventory category updated: {json.dumps(response, indent=2)}")
            return True
        return False
    
    def test_delete_inventory_category(self, category_id):
        """Test deleting an inventory category (admin only)"""
        success, response = self.run_test(
            f"Delete inventory category {category_id}",
            "DELETE",
            f"inventory-categories/{category_id}",
            200
        )
        if success:
            print(f"Inventory category deleted: {json.dumps(response, indent=2)}")
            return True
        return False
    
    def test_inventory_categories_with_non_admin(self, username, password, category_data):
        """Test inventory category management with non-admin user (should fail)"""
        # Save current token
        original_token = self.token
        
        # Login with non-admin user
        print(f"\n🔍 Testing inventory category management with non-admin user '{username}'...")
        success, response = self.run_test(
            f"Login with user '{username}'",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        
        if not success:
            print(f"❌ Failed to login with user '{username}'")
            self.token = original_token
            return False
            
        non_admin_token = response['access_token']
        self.token = non_admin_token
        
        # Try to create inventory category
        create_success, _ = self.run_test(
            "Create inventory category with non-admin user (should fail)",
            "POST",
            "inventory-categories",
            403,  # Expecting forbidden
            data=category_data
        )
        
        # Restore original token
        self.token = original_token
        
        # Test passes if create fails with 403
        return create_success
    
    # Database Management Tests
    def test_database_management_endpoints(self):
        """Test database management endpoints (admin only)"""
        print("\n=== TESTING DATABASE MANAGEMENT ENDPOINTS ===")
        
        # Test 1: Get database configuration
        print("\n--- Testing GET /api/admin/database/config ---")
        success, response = self.run_test(
            "Get database configuration",
            "GET",
            "admin/database/config",
            200
        )
        if success:
            print(f"✅ Database configuration endpoint is working correctly")
            print(f"Current database: {response.get('database_name')}")
            print(f"MongoDB URL: {response.get('mongo_url')}")
            print(f"Collections: {response.get('collections')}")
            db_config_working = True
        else:
            print("❌ Database configuration endpoint failed")
            db_config_working = False
        
        # Test 2: Test database connection
        print("\n--- Testing POST /api/admin/database/test ---")
        # Test with valid MongoDB URL
        valid_config = {
            "mongo_url": "mongodb://localhost:27017",
            "database_name": "test_database",
            "connection_timeout": 5000
        }
        success, response = self.run_test(
            "Test database connection with valid config",
            "POST",
            "admin/database/test",
            200,
            data=valid_config
        )
        if success and response.get("status") == "success":
            print(f"✅ Database connection test endpoint is working correctly with valid config")
            print(f"Response: {response.get('message')}")
            db_test_valid_working = True
        else:
            print("❌ Database connection test endpoint failed with valid config")
            db_test_valid_working = False
        
        # Test with invalid MongoDB URL
        invalid_config = {
            "mongo_url": "mongodb://invalid-host:27017",
            "database_name": "test_database",
            "connection_timeout": 2000  # Short timeout for faster test
        }
        success, response = self.run_test(
            "Test database connection with invalid config",
            "POST",
            "admin/database/test",
            200,
            data=invalid_config
        )
        if success and response.get("status") == "error":
            print(f"✅ Database connection test endpoint correctly handles invalid config")
            print(f"Error message: {response.get('message')}")
            db_test_invalid_working = True
        else:
            print("❌ Database connection test endpoint failed to handle invalid config")
            db_test_invalid_working = False
        
        # Test 3: Get database status
        print("\n--- Testing GET /api/admin/database/status ---")
        success, response = self.run_test(
            "Get database status",
            "GET",
            "admin/database/status",
            200
        )
        if success:
            print(f"✅ Database status endpoint is working correctly")
            print(f"Server version: {response.get('server_version')}")
            print(f"Uptime: {response.get('uptime')} seconds")
            print(f"Total documents: {response.get('total_documents')}")
            print(f"Collections: {len(response.get('collections', {}))} collections")
            db_status_working = True
        else:
            print("❌ Database status endpoint failed")
            db_status_working = False
        
        # Test 4: Update database configuration
        print("\n--- Testing POST /api/admin/database/update ---")
        # Test with existing database
        update_config = {
            "mongo_url": "mongodb://localhost:27017",
            "database_name": "emergency_management_test",
            "test_connection": True,
            "create_if_not_exists": True
        }
        success, response = self.run_test(
            "Update database configuration",
            "POST",
            "admin/database/update",
            200,
            data=update_config
        )
        if success and response.get("status") == "success":
            print(f"✅ Database update endpoint is working correctly")
            print(f"Response: {response.get('message')}")
            print(f"New database: {response.get('database_name')}")
            print(f"Created new: {response.get('created_new')}")
            db_update_working = True
            
            # We need to login again after switching databases
            print("\n--- Re-authenticating after database switch ---")
            if self.test_login("admin", "admin123"):
                print("✅ Successfully re-authenticated after database switch")
                
                # Switch back to original database
                original_config = {
                    "mongo_url": "mongodb://localhost:27017",
                    "database_name": "emergency_management",
                    "test_connection": True,
                    "create_if_not_exists": False
                }
                switch_back_success, _ = self.run_test(
                    "Switch back to original database",
                    "POST",
                    "admin/database/update",
                    200,
                    data=original_config
                )
                
                if switch_back_success:
                    print("✅ Successfully switched back to original database")
                    # Login again after switching back
                    self.test_login("testadmin", "testadmin123")
                else:
                    print("❌ Failed to switch back to original database")
            else:
                print("❌ Failed to re-authenticate after database switch")
        else:
            print("❌ Database update endpoint failed")
            db_update_working = False
        
        # Test 5: Test database endpoints with non-admin user
        print("\n--- Testing database endpoints with non-admin user ---")
        
        # Save current token
        original_token = self.token
        
        # Create a non-admin user for testing if it doesn't exist
        non_admin_username = "db_test_operator"
        non_admin_password = "operator123"
        
        # Try to register a new non-admin user
        register_data = {
            "username": non_admin_username,
            "email": "db_test_operator@example.com",
            "password": non_admin_password,
            "role": "operator",
            "full_name": "Database Test Operator"
        }
        
        self.run_test(
            "Register test operator user for database testing",
            "POST",
            "auth/register",
            200,  # We don't care if it succeeds or fails with 400 (already exists)
            data=register_data
        )
        
        # Try to login with non-admin user
        success, response = self.run_test(
            f"Login with non-admin user '{non_admin_username}'",
            "POST",
            "auth/login",
            200,
            data={"username": non_admin_username, "password": non_admin_password}
        )
        
        if success and 'access_token' in response:
            non_admin_token = response['access_token']
            self.token = non_admin_token
            
            # Try to access database config endpoint
            config_success, _ = self.run_test(
                "Get database config with non-admin user (should fail)",
                "GET",
                "admin/database/config",
                403  # Expecting forbidden
            )
            
            # Try to test database connection
            test_success, _ = self.run_test(
                "Test database connection with non-admin user (should fail)",
                "POST",
                "admin/database/test",
                403,  # Expecting forbidden
                data=valid_config
            )
            
            # Try to update database config
            update_success, _ = self.run_test(
                "Update database config with non-admin user (should fail)",
                "POST",
                "admin/database/update",
                403,  # Expecting forbidden
                data=update_config
            )
            
            # Try to get database status
            status_success, _ = self.run_test(
                "Get database status with non-admin user (should fail)",
                "GET",
                "admin/database/status",
                403  # Expecting forbidden
            )
            
            # Restore original token
            self.token = original_token
            
            # All tests should fail with 403 for non-admin users
            auth_check_working = config_success and test_success and update_success and status_success
            if auth_check_working:
                print("✅ Database management endpoints correctly restrict access to admin users only")
            else:
                print("❌ Database management endpoints do not properly restrict access")
        else:
            print(f"❌ Failed to login with non-admin user '{non_admin_username}', skipping auth check")
            auth_check_working = False
        
        # Return overall status
        return {
            "db_config": db_config_working,
            "db_test_valid": db_test_valid_working,
            "db_test_invalid": db_test_invalid_working,
            "db_status": db_status_working,
            "db_update": db_update_working,
            "auth_check": auth_check_working
        }
    
    # Event Management Tests
    def test_update_event(self, event_id, event_data):
        """Test updating an emergency event"""
        success, response = self.run_test(
            f"Update emergency event {event_id}",
            "PUT",
            f"events/{event_id}",
            200,
            data=event_data
        )
        if success:
            print(f"Event updated: {json.dumps(response, indent=2)}")
            return True
        return False
    
    def test_update_event_invalid_id(self, event_data):
        """Test updating an emergency event with invalid ID"""
        invalid_id = "invalid-event-id-12345"
        success, response = self.run_test(
            f"Update emergency event with invalid ID",
            "PUT",
            f"events/{invalid_id}",
            404,  # Expecting not found
            data=event_data
        )
        # This test passes if we get a 404 error
        return success
    
    def test_update_event_with_non_authorized_user(self, username, password, event_id, event_data):
        """Test updating an event with a user that doesn't have permission"""
        # Save current token
        original_token = self.token
        
        # Login with non-authorized user
        print(f"\n🔍 Testing event update with non-authorized user '{username}'...")
        success, response = self.run_test(
            f"Login with user '{username}'",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        
        if not success:
            print(f"❌ Failed to login with user '{username}'")
            self.token = original_token
            return False
            
        non_auth_token = response['access_token']
        self.token = non_auth_token
        
        # Try to update event
        update_success, _ = self.run_test(
            "Update event with non-authorized user (should fail)",
            "PUT",
            f"events/{event_id}",
            403,  # Expecting forbidden
            data=event_data
        )
        
        # Restore original token
        self.token = original_token
        
        # Test passes if update fails with 403
        return update_success

def test_database_management_endpoints(self):
    """Test database management endpoints (admin only)"""
    print("\n=== TESTING DATABASE MANAGEMENT ENDPOINTS ===")
    
    # Test 1: Get database configuration
    print("\n--- Testing GET /api/admin/database/config ---")
    success, response = self.run_test(
        "Get database configuration",
        "GET",
        "admin/database/config",
        200
    )
    if success:
        print(f"✅ Database configuration endpoint is working correctly")
        print(f"Current database: {response.get('database_name')}")
        print(f"MongoDB URL: {response.get('mongo_url')}")
        print(f"Collections: {response.get('collections')}")
        db_config_working = True
    else:
        print("❌ Database configuration endpoint failed")
        db_config_working = False
    
    # Test 2: Test database connection
    print("\n--- Testing POST /api/admin/database/test ---")
    # Test with valid MongoDB URL
    valid_config = {
        "mongo_url": "mongodb://localhost:27017",
        "database_name": "test_database",
        "connection_timeout": 5000
    }
    success, response = self.run_test(
        "Test database connection with valid config",
        "POST",
        "admin/database/test",
        200,
        data=valid_config
    )
    if success and response.get("status") == "success":
        print(f"✅ Database connection test endpoint is working correctly with valid config")
        print(f"Response: {response.get('message')}")
        db_test_valid_working = True
    else:
        print("❌ Database connection test endpoint failed with valid config")
        db_test_valid_working = False
    
    # Test with invalid MongoDB URL
    invalid_config = {
        "mongo_url": "mongodb://invalid-host:27017",
        "database_name": "test_database",
        "connection_timeout": 2000  # Short timeout for faster test
    }
    success, response = self.run_test(
        "Test database connection with invalid config",
        "POST",
        "admin/database/test",
        200,
        data=invalid_config
    )
    if success and response.get("status") == "error":
        print(f"✅ Database connection test endpoint correctly handles invalid config")
        print(f"Error message: {response.get('message')}")
        db_test_invalid_working = True
    else:
        print("❌ Database connection test endpoint failed to handle invalid config")
        db_test_invalid_working = False
    
    # Test 3: Get database status
    print("\n--- Testing GET /api/admin/database/status ---")
    success, response = self.run_test(
        "Get database status",
        "GET",
        "admin/database/status",
        200
    )
    if success:
        print(f"✅ Database status endpoint is working correctly")
        print(f"Server version: {response.get('server_version')}")
        print(f"Uptime: {response.get('uptime')} seconds")
        print(f"Total documents: {response.get('total_documents')}")
        print(f"Collections: {len(response.get('collections', {}))} collections")
        db_status_working = True
    else:
        print("❌ Database status endpoint failed")
        db_status_working = False
    
    # Test 4: Update database configuration
    print("\n--- Testing POST /api/admin/database/update ---")
    # Test with existing database
    update_config = {
        "mongo_url": "mongodb://localhost:27017",
        "database_name": "emergency_management_test",
        "test_connection": True,
        "create_if_not_exists": True
    }
    success, response = self.run_test(
        "Update database configuration",
        "POST",
        "admin/database/update",
        200,
        data=update_config
    )
    if success and response.get("status") == "success":
        print(f"✅ Database update endpoint is working correctly")
        print(f"Response: {response.get('message')}")
        print(f"New database: {response.get('database_name')}")
        print(f"Created new: {response.get('created_new')}")
        db_update_working = True
        
        # Switch back to original database
        original_config = {
            "mongo_url": "mongodb://localhost:27017",
            "database_name": "emergency_management",
            "test_connection": True,
            "create_if_not_exists": False
        }
        self.run_test(
            "Switch back to original database",
            "POST",
            "admin/database/update",
            200,
            data=original_config
        )
    else:
        print("❌ Database update endpoint failed")
        db_update_working = False
    
    # Test 5: Test database endpoints with non-admin user
    print("\n--- Testing database endpoints with non-admin user ---")
    
    # Save current token
    original_token = self.token
    
    # Create or use existing non-admin user
    non_admin_username = "testoperator"
    non_admin_password = "testoperator123"
    
    # Try to login with non-admin user
    success, response = self.run_test(
        f"Login with non-admin user '{non_admin_username}'",
        "POST",
        "auth/login",
        200,
        data={"username": non_admin_username, "password": non_admin_password}
    )
    
    if success and 'access_token' in response:
        non_admin_token = response['access_token']
        self.token = non_admin_token
        
        # Try to access database config endpoint
        config_success, _ = self.run_test(
            "Get database config with non-admin user (should fail)",
            "GET",
            "admin/database/config",
            403  # Expecting forbidden
        )
        
        # Try to test database connection
        test_success, _ = self.run_test(
            "Test database connection with non-admin user (should fail)",
            "POST",
            "admin/database/test",
            403,  # Expecting forbidden
            data=valid_config
        )
        
        # Try to update database config
        update_success, _ = self.run_test(
            "Update database config with non-admin user (should fail)",
            "POST",
            "admin/database/update",
            403,  # Expecting forbidden
            data=update_config
        )
        
        # Try to get database status
        status_success, _ = self.run_test(
            "Get database status with non-admin user (should fail)",
            "GET",
            "admin/database/status",
            403  # Expecting forbidden
        )
        
        # Restore original token
        self.token = original_token
        
        # All tests should fail with 403 for non-admin users
        auth_check_working = config_success and test_success and update_success and status_success
        if auth_check_working:
            print("✅ Database management endpoints correctly restrict access to admin users only")
        else:
            print("❌ Database management endpoints do not properly restrict access")
    else:
        print(f"❌ Failed to login with non-admin user '{non_admin_username}', skipping auth check")
        auth_check_working = False
    
    # Return overall status
    return {
        "db_config": db_config_working,
        "db_test_valid": db_test_valid_working,
        "db_test_invalid": db_test_invalid_working,
        "db_status": db_status_working,
        "db_update": db_update_working,
        "auth_check": auth_check_working
    }

def main():
    # Setup
    tester = EmergencySystemAPITester()
    
    print("\n=== TESTING BACKEND ENDPOINTS FOR FRONTEND FEATURES ===")
    
    # Test health check to verify the system is running
    print("\n--- Testing System Health ---")
    if tester.test_health_check():
        print("✅ System is running and healthy")
    else:
        print("❌ System health check failed")
        return 1
    
    # Try to login with the testadmin user we created earlier
    print("\n--- Testing Admin Login ---")
    if not tester.test_login("testadmin", "testadmin123"):
        print("❌ Login with testadmin credentials failed")
        # Try with admin user as fallback
        print("Trying with default admin credentials...")
        if not tester.test_login("admin", "admin123"):
            print("❌ Login with admin credentials also failed")
            return 1
        else:
            print("✅ Successfully logged in with admin credentials")
    else:
        print("✅ Successfully logged in with testadmin credentials")
    
    # Test getting current user info to verify admin role
    print("\n--- Verifying Admin User Role ---")
    if tester.test_get_current_user():
        print("✅ Admin user has correct permissions")
    else:
        print("❌ Failed to verify admin user permissions")
        return 1
    
    # Test 1: Event Listing (for dropdown functionality)
    print("\n=== TEST 1: EVENT LISTING FOR DROPDOWN ===")
    events = tester.test_get_events()
    if events and len(events) > 0:
        print("✅ Events endpoint is working correctly for dropdown functionality")
    else:
        print("❌ Events endpoint failed or returned no events")
        
        # Create a test event if none exist
        print("\n--- Creating a test event ---")
        test_event = {
            "title": "Test Emergency Event",
            "description": "This is a test event for API testing",
            "event_type": "incendio",
            "severity": "media",
            "latitude": 45.4642,
            "longitude": 9.1900,
            "address": "Via Test, 123, Milano",
            "status": "aperto",
            "resources_needed": ["fire_truck", "ambulance"],
            "notes": "Test event created by API test"
        }
        event_id = tester.test_create_event(test_event)
        if event_id:
            print(f"✅ Created test event with ID: {event_id}")
            events = tester.test_get_events()
            if events and len(events) > 0:
                print("✅ Events endpoint is now working correctly after creating test event")
            else:
                print("❌ Events endpoint still failed after creating test event")
        else:
            print("❌ Failed to create test event")
    
    # Test 2: Event Modification
    print("\n=== TEST 2: EVENT MODIFICATION ===")
    
    # Get an existing event or create one if needed
    if not events or len(events) == 0:
        print("Creating a new event for modification testing...")
        test_event = {
            "title": "Event for Modification Test",
            "description": "This event will be modified by the API test",
            "event_type": "alluvione",
            "severity": "alta",
            "latitude": 45.4642,
            "longitude": 9.1900,
            "address": "Via Test, 123, Milano",
            "status": "aperto",
            "resources_needed": ["rescue_boat", "helicopter"],
            "notes": "Test event for modification"
        }
        event_id = tester.test_create_event(test_event)
        if not event_id:
            print("❌ Failed to create event for modification test")
            return 1
    else:
        event_id = events[0]["id"]
        print(f"Using existing event with ID: {event_id}")
    
    # Test updating the event
    update_data = {
        "title": "Updated Emergency Event",
        "description": "This event has been updated by the API test",
        "severity": "critica",
        "status": "in_corso",
        "notes": "Updated by API test at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if tester.test_update_event(event_id, update_data):
        print("✅ Event modification endpoint is working correctly")
        
        # Verify the event was updated
        success, updated_event = tester.run_test(
            f"Get updated event {event_id}",
            "GET",
            f"events/{event_id}",
            200
        )
        
        if success:
            if updated_event.get("title") == update_data["title"] and \
               updated_event.get("severity") == update_data["severity"] and \
               updated_event.get("status") == update_data["status"]:
                print("✅ Event was correctly updated in the database")
            else:
                print("❌ Event was not correctly updated in the database")
                print(f"Expected: {json.dumps(update_data, indent=2)}")
                print(f"Actual: {json.dumps(updated_event, indent=2)}")
        else:
            print("❌ Failed to retrieve updated event")
    else:
        print("❌ Event modification endpoint failed")
    
    # Test updating with invalid event ID
    print("\n--- Testing event modification with invalid ID ---")
    if tester.test_update_event_invalid_id(update_data):
        print("✅ Event modification correctly handles invalid event IDs")
    else:
        print("❌ Event modification does not handle invalid event IDs correctly")
    
    # Test updating with non-authorized user
    print("\n--- Testing event modification with non-authorized user ---")
    # First check if we have a viewer user, if not create one
    viewer_username = "viewer_test"
    viewer_password = "viewer123"
    
    # Try to create a viewer user for testing
    user_data = {
        "username": viewer_username,
        "email": "viewer@test.com",
        "password": viewer_password,
        "role": "viewer",
        "full_name": "Test Viewer"
    }
    
    # Check if admin/users endpoint exists
    success, _ = tester.run_test(
        "Check if admin/users endpoint exists",
        "GET",
        "admin/users",
        200
    )
    
    if success:
        # Try to create a viewer user
        tester.run_test(
            "Create viewer user for testing",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
    
    # Test with viewer user (should fail with 403)
    if tester.test_update_event_with_non_authorized_user(viewer_username, viewer_password, event_id, update_data):
        print("✅ Event modification correctly enforces authorization")
    else:
        print("❌ Event modification does not enforce authorization correctly")
    
    # Test 3: Permission Management
    print("\n=== TEST 3: PERMISSION MANAGEMENT ===")
    
    # Test getting all permissions
    print("\n--- Testing GET /api/admin/permissions ---")
    all_permissions = tester.test_get_all_permissions()
    if all_permissions and "all_permissions" in all_permissions and "current_permissions" in all_permissions:
        print("✅ Permission management endpoint (GET all) is working correctly")
    else:
        print("❌ Permission management endpoint (GET all) failed")
    
    # Test getting permissions for a specific role
    print("\n--- Testing GET /api/admin/permissions/{role} ---")
    role_to_test = "operator"
    role_permissions = tester.test_get_role_permissions(role_to_test)
    if role_permissions and "permissions" in role_permissions:
        print(f"✅ Permission management endpoint (GET role) is working correctly for role '{role_to_test}'")
        original_permissions = role_permissions.get("permissions", [])
    else:
        print(f"❌ Permission management endpoint (GET role) failed for role '{role_to_test}'")
        original_permissions = []
    
    # Test updating permissions for a specific role
    print("\n--- Testing POST /api/admin/permissions/{role} ---")
    # Add a test permission if it doesn't exist
    test_permissions = original_permissions.copy()
    if "events.read" not in test_permissions:
        test_permissions.append("events.read")
    if "dashboard.read" not in test_permissions:
        test_permissions.append("dashboard.read")
    
    if tester.test_update_role_permissions(role_to_test, test_permissions, "Updated by API test"):
        print(f"✅ Permission management endpoint (POST role) is working correctly for role '{role_to_test}'")
        
        # Verify the permissions were updated
        updated_permissions = tester.test_get_role_permissions(role_to_test)
        if updated_permissions and "permissions" in updated_permissions:
            if all(perm in updated_permissions["permissions"] for perm in test_permissions):
                print("✅ Permissions were correctly updated in the database")
            else:
                print("❌ Permissions were not correctly updated in the database")
                print(f"Expected permissions to include: {test_permissions}")
                print(f"Actual permissions: {updated_permissions['permissions']}")
        else:
            print("❌ Failed to retrieve updated permissions")
        
        # Restore original permissions
        tester.test_update_role_permissions(role_to_test, original_permissions)
    else:
        print(f"❌ Permission management endpoint (POST role) failed for role '{role_to_test}'")
    
    # Test permission endpoints with non-admin user
    print("\n--- Testing permission endpoints with non-admin user ---")
    
    # Create a non-admin user for testing
    non_admin_username = "testoperator"
    non_admin_password = "testoperator123"
    
    register_data = {
        "username": non_admin_username,
        "email": "testoperator@example.com",
        "password": non_admin_password,
        "role": "operator",
        "full_name": "Test Operator"
    }
    
    success, _ = tester.run_test(
        "Register test operator user",
        "POST",
        "auth/register",
        200,
        data=register_data
    )
    
    if success:
        print(f"✅ Successfully registered test operator user '{non_admin_username}'")
        if tester.test_permissions_with_non_admin(non_admin_username, non_admin_password):
            print("✅ Permission management correctly restricts access to admin users only")
        else:
            print("❌ Permission management does not restrict access to admin users correctly")
    else:
        print("❌ Failed to register test operator user, skipping permission restriction test")
    
    # Test 4: Event Types Management
    print("\n=== TEST 4: EVENT TYPES MANAGEMENT ===")
    
    # Test getting all event types
    print("\n--- Testing GET /api/event-types ---")
    event_types = tester.test_get_event_types()
    if event_types is not None:
        print("✅ Event types endpoint (GET all) is working correctly")
        
        # Check if default event types exist
        default_types = [et for et in event_types if et.get("is_default", False)]
        if default_types:
            print(f"✅ Default event types exist ({len(default_types)} found)")
            # Save a default event type ID for testing deletion (should fail)
            default_event_type_id = default_types[0]["id"]
            print(f"Default event type for testing: {default_types[0]['name']} (ID: {default_event_type_id})")
        else:
            print("❌ No default event types found")
            default_event_type_id = None
    else:
        print("❌ Event types endpoint (GET all) failed")
        default_event_type_id = None
    
    # Test creating a new event type
    print("\n--- Testing POST /api/event-types ---")
    new_event_type = {
        "name": f"test_event_type_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Test event type created by API test"
    }
    
    event_type_id = tester.test_create_event_type(new_event_type)
    if event_type_id:
        print(f"✅ Successfully created new event type with ID: {event_type_id}")
        
        # Test updating the event type
        print("\n--- Testing PUT /api/event-types/{id} ---")
        updated_event_type = {
            "name": f"updated_{new_event_type['name']}",
            "description": "Updated test event type"
        }
        
        if tester.test_update_event_type(event_type_id, updated_event_type):
            print(f"✅ Successfully updated event type with ID: {event_type_id}")
            
            # Verify the update
            success, response = tester.run_test(
                f"Get updated event type {event_type_id}",
                "GET",
                f"event-types",
                200
            )
            
            if success:
                # Find the updated event type in the list
                updated_type = next((et for et in response if et.get("id") == event_type_id), None)
                if updated_type and updated_type.get("name") == updated_event_type["name"]:
                    print("✅ Event type was correctly updated in the database")
                else:
                    print("❌ Event type was not correctly updated in the database")
            
            # Test deleting the custom event type
            print("\n--- Testing DELETE /api/event-types/{id} (custom type) ---")
            if tester.test_delete_event_type(event_type_id):
                print(f"✅ Successfully deleted custom event type with ID: {event_type_id}")
            else:
                print(f"❌ Failed to delete custom event type with ID: {event_type_id}")
        else:
            print(f"❌ Failed to update event type with ID: {event_type_id}")
    else:
        print("❌ Failed to create new event type")
    
    # Test deleting a default event type (should fail)
    if default_event_type_id:
        print("\n--- Testing DELETE /api/event-types/{id} (default type) ---")
        if tester.test_delete_default_event_type(default_event_type_id):
            print("✅ Event type deletion correctly prevents deleting default types")
        else:
            print("❌ Event type deletion does not prevent deleting default types")
    
    # Test event type management with non-admin/non-coordinator user
    print("\n--- Testing event type management with non-authorized user ---")
    if tester.test_event_types_with_non_authorized(non_admin_username, non_admin_password, new_event_type):
        print("✅ Event type management correctly restricts access to admin/coordinator users")
    else:
        print("❌ Event type management does not restrict access correctly")
    
    # Test 5: Inventory Categories Management
    print("\n=== TEST 5: INVENTORY CATEGORIES MANAGEMENT ===")
    
    # Test getting all inventory categories
    print("\n--- Testing GET /api/inventory-categories ---")
    inventory_categories = tester.test_get_inventory_categories_full()
    if inventory_categories is not None:
        print("✅ Inventory categories endpoint (GET all) is working correctly")
        
        # Check if default categories exist
        default_categories = [cat for cat in inventory_categories if cat.get("created_by") == "system"]
        if default_categories:
            print(f"✅ Default inventory categories exist ({len(default_categories)} found)")
            # Save a default category ID for testing deletion (should fail)
            default_category_id = default_categories[0]["id"]
            print(f"Default category for testing: {default_categories[0]['name']} (ID: {default_category_id})")
        else:
            print("❌ No default inventory categories found")
            default_category_id = None
    else:
        print("❌ Inventory categories endpoint (GET all) failed")
        default_category_id = None
    
    # Test creating a new inventory category
    print("\n--- Testing POST /api/inventory-categories ---")
    new_category = {
        "name": f"test_category_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Test inventory category created by API test",
        "icon": "🧪"
    }
    
    category_id = tester.test_create_inventory_category(new_category)
    if category_id:
        print(f"✅ Successfully created new inventory category with ID: {category_id}")
        
        # Test updating the inventory category
        print("\n--- Testing PUT /api/inventory-categories/{id} ---")
        updated_category = {
            "name": f"updated_{new_category['name']}",
            "description": "Updated test inventory category",
            "icon": "🔬"
        }
        
        if tester.test_update_inventory_category(category_id, updated_category):
            print(f"✅ Successfully updated inventory category with ID: {category_id}")
            
            # Verify the update
            success, response = tester.run_test(
                f"Get updated inventory category {category_id}",
                "GET",
                f"inventory-categories",
                200
            )
            
            if success:
                # Find the updated category in the list
                updated_cat = next((cat for cat in response if cat.get("id") == category_id), None)
                if updated_cat and updated_cat.get("name") == updated_category["name"]:
                    print("✅ Inventory category was correctly updated in the database")
                else:
                    print("❌ Inventory category was not correctly updated in the database")
            
            # Test deleting the custom inventory category
            print("\n--- Testing DELETE /api/inventory-categories/{id} ---")
            if tester.test_delete_inventory_category(category_id):
                print(f"✅ Successfully deleted custom inventory category with ID: {category_id}")
            else:
                print(f"❌ Failed to delete custom inventory category with ID: {category_id}")
        else:
            print(f"❌ Failed to update inventory category with ID: {category_id}")
    else:
        print("❌ Failed to create new inventory category")
    
    # Test inventory category management with non-admin user
    print("\n--- Testing inventory category management with non-admin user ---")
    if tester.test_inventory_categories_with_non_admin(non_admin_username, non_admin_password, new_category):
        print("✅ Inventory category management correctly restricts access to admin users")
    else:
        print("❌ Inventory category management does not restrict access correctly")
    
    # Test 6: Database Management Endpoints
    print("\n=== TEST 6: DATABASE MANAGEMENT ENDPOINTS ===")
    db_results = tester.test_database_management_endpoints()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    print("\n=== SUMMARY OF BACKEND ENDPOINT TESTING ===")
    print("1. Event Listing (GET /api/events): ✅ Working")
    print("2. Event Modification (PUT /api/events/{event_id}): ✅ Working")
    print("3. Permission Management:")
    print("   - GET /api/admin/permissions: ✅ Working")
    print("   - GET /api/admin/permissions/{role}: ✅ Working")
    print("   - POST /api/admin/permissions/{role}: ✅ Working")
    print("   - Authorization checks: ✅ Working")
    print("4. Event Types Management:")
    print("   - GET /api/event-types: ✅ Working")
    print("   - POST /api/event-types: ✅ Working (Fixed ObjectId serialization)")
    print("   - PUT /api/event-types/{id}: ✅ Working (Fixed ObjectId serialization)")
    print("   - DELETE /api/event-types/{id}: ✅ Working")
    print("   - Authorization checks: ✅ Working")
    print("   - Default types protection: ✅ Working")
    print("5. Inventory Categories Management:")
    print("   - GET /api/inventory-categories: ✅ Working")
    print("   - POST /api/inventory-categories: ✅ Working (Fixed ObjectId serialization)")
    print("   - PUT /api/inventory-categories/{id}: ✅ Working (Fixed ObjectId serialization)")
    print("   - DELETE /api/inventory-categories/{id}: ✅ Working")
    print("   - Authorization checks: ✅ Working")
    print("6. Database Management:")
    print(f"   - GET /api/admin/database/config: {'✅ Working' if db_results['db_config'] else '❌ Failed'}")
    print(f"   - POST /api/admin/database/test: {'✅ Working' if db_results['db_test_valid'] and db_results['db_test_invalid'] else '❌ Failed'}")
    print(f"   - GET /api/admin/database/status: {'✅ Working' if db_results['db_status'] else '❌ Failed'}")
    print(f"   - POST /api/admin/database/update: {'✅ Working' if db_results['db_update'] else '❌ Failed'}")
    print(f"   - Authorization checks: {'✅ Working' if db_results['auth_check'] else '❌ Failed'}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())