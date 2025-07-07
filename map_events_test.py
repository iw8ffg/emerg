import requests
import sys
import json
from datetime import datetime

class MapEventsTester:
    def __init__(self, base_url="https://5f984545-e129-4cc2-a34a-9e9847a0f0a0.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_events = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

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
            "Login",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"User logged in: {response['user']['username']} ({response['user']['role']})")
            return True
        return False

    def test_create_event(self, event_data):
        """Create a test event with coordinates"""
        success, response = self.run_test(
            f"Create event: {event_data['title']}",
            "POST",
            "events",
            200,
            data=event_data
        )
        if success and 'event_id' in response:
            print(f"Created event with ID: {response['event_id']}")
            self.created_events.append(response['event_id'])
            return response['event_id']
        return None

    def test_get_map_events(self, params=None):
        """Test the map events endpoint with filters"""
        endpoint = "events/map"
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{endpoint}?{query_string}"
            
        success, response = self.run_test(
            f"Get map events {params if params else ''}",
            "GET",
            endpoint,
            200
        )
        
        if success:
            events = response.get('events', [])
            print(f"Retrieved {len(events)} events for map")
            
            # Verify event structure
            if events:
                print("Verifying event structure...")
                required_fields = ['id', 'title', 'description', 'event_type', 'severity', 
                                  'status', 'latitude', 'longitude', 'created_at']
                
                missing_fields = [field for field in required_fields if field not in events[0]]
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                else:
                    print(f"✅ All required fields present")
                    
                # Print first event details
                print(f"First event: {json.dumps(events[0], indent=2)}")
                
            return events
        return []

def main():
    # Setup
    tester = MapEventsTester()
    
    # Run tests
    if not tester.test_login("admin", "admin123"):
        print("❌ Login failed, stopping tests")
        return 1
    
    # Create test events with coordinates for map testing
    test_events = [
        {
            "title": "Incendio Duomo Milano",
            "description": "Incendio di grave entità presso il Duomo di Milano",
            "event_type": "incendio",
            "severity": "critica",
            "latitude": 45.4642,
            "longitude": 9.1900,
            "address": "Piazza del Duomo, Milano",
            "status": "aperto",
            "notes": "Evento di test per la mappa"
        },
        {
            "title": "Alluvione Colosseo",
            "description": "Alluvione nei pressi del Colosseo",
            "event_type": "alluvione",
            "severity": "alta",
            "latitude": 41.8902,
            "longitude": 12.4922,
            "address": "Piazza del Colosseo, Roma",
            "status": "in_corso",
            "notes": "Evento di test per la mappa"
        },
        {
            "title": "Blackout Firenze Centro",
            "description": "Interruzione di corrente nel centro storico",
            "event_type": "blackout",
            "severity": "media",
            "latitude": 43.7696,
            "longitude": 11.2558,
            "address": "Piazza della Signoria, Firenze",
            "status": "aperto",
            "notes": "Evento di test per la mappa"
        }
    ]
    
    for event in test_events:
        tester.test_create_event(event)
    
    # Test 1: Get all map events
    all_events = tester.test_get_map_events()
    
    # Test 2: Filter by status
    active_events = tester.test_get_map_events({"status": "active"})
    print(f"Active events: {len(active_events)}")
    
    # Test 3: Filter by event type
    incendio_events = tester.test_get_map_events({"event_type": "incendio"})
    print(f"Incendio events: {len(incendio_events)}")
    
    # Test 4: Filter by severity
    critica_events = tester.test_get_map_events({"severity": "critica"})
    print(f"Critical severity events: {len(critica_events)}")
    
    # Test 5: Combined filters
    combined_events = tester.test_get_map_events({
        "status": "active",
        "event_type": "incendio"
    })
    print(f"Active incendio events: {len(combined_events)}")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())