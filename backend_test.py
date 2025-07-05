import requests
import sys
import json
from datetime import datetime

class EmergencySystemAPITester:
    def __init__(self, base_url="https://5f984545-e129-4cc2-a34a-9e9847a0f0a0.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_info = None
        self.created_logs = []
        self.created_events = []

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

def main():
    # Setup
    tester = EmergencySystemAPITester()
    
    # Test health check
    tester.test_health_check()
    
    # Test login
    if not tester.test_login("admin", "admin123"):
        print("❌ Login failed, stopping tests")
        return 1

    # Test getting current user info
    tester.test_get_current_user()
    
    # Test getting dashboard stats
    tester.test_get_dashboard_stats()
    
    # Test getting events
    events = tester.test_get_events()
    
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

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())