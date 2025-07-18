import requests
import sys
import json
from datetime import datetime, timedelta

class InventoryUserTester:
    def __init__(self, base_url="https://272455ba-030f-4132-83b6-fa2f9889fad1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_info = None
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
    tester = InventoryUserTester()
    
    # Test login
    if not tester.test_login("admin", "admin123"):
        print("❌ Login failed, stopping tests")
        return 1

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