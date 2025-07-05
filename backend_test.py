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
        return success

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
            return response.get('event_id')
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
    tester.test_get_events()
    
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
        
    # Test getting events again to verify the new event is in the list
    tester.test_get_events()

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())