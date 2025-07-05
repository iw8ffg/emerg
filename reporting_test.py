import requests
import sys
from datetime import datetime, timedelta
import time

class ReportingSystemTester:
    def __init__(self, base_url="https://5f984545-e129-4cc2-a34a-9e9847a0f0a0.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    # For multipart/form-data
                    del headers['Content-Type']
                    response = requests.post(url, headers=headers, data=data, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json() if response.content and 'application/json' in response.headers.get('Content-Type', '') else {}
                except:
                    return success, {"raw_content": "Binary content (likely a file)"}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                    print(f"Error detail: {error_detail}")
                except:
                    print(f"Could not parse error response: {response.text[:200]}")
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
            self.user = response.get('user', {})
            print(f"Logged in as {self.user.get('username')} with role {self.user.get('role')}")
            return True
        return False

    def test_get_report_templates(self):
        """Test getting report templates"""
        success, response = self.run_test(
            "Get Report Templates",
            "GET",
            "reports/templates",
            200
        )
        if success:
            print(f"Available report templates: {', '.join(response.get('templates', {}).keys())}")
            print(f"Filter options: {list(response.get('filter_options', {}).keys())}")
        return success, response

    def test_generate_events_report_pdf(self):
        """Test generating events report in PDF format"""
        today = datetime.now()
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = {
            "report_type": "events",
            "format": "pdf",
            "start_date": start_date,
            "end_date": today.strftime('%Y-%m-%d'),
            "event_type": "incendio",
            "severity": "alta"
        }
        
        success, response = self.run_test(
            "Generate Events PDF Report",
            "POST",
            "reports/generate",
            200,
            data=data
        )
        return success

    def test_generate_events_report_excel(self):
        """Test generating events report in Excel format"""
        today = datetime.now()
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = {
            "report_type": "events",
            "format": "excel",
            "start_date": start_date,
            "end_date": today.strftime('%Y-%m-%d')
        }
        
        success, response = self.run_test(
            "Generate Events Excel Report",
            "POST",
            "reports/generate",
            200,
            data=data
        )
        return success

    def test_generate_logs_report_pdf(self):
        """Test generating logs report in PDF format"""
        today = datetime.now()
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = {
            "report_type": "logs",
            "format": "pdf",
            "start_date": start_date,
            "end_date": today.strftime('%Y-%m-%d'),
            "priority": "normale",
            "operator": "admin"
        }
        
        success, response = self.run_test(
            "Generate Logs PDF Report",
            "POST",
            "reports/generate",
            200,
            data=data
        )
        return success

    def test_generate_statistics_report_pdf(self):
        """Test generating statistics report in PDF format"""
        data = {
            "report_type": "statistics",
            "format": "pdf"
        }
        
        success, response = self.run_test(
            "Generate Statistics PDF Report",
            "POST",
            "reports/generate",
            200,
            data=data
        )
        return success

def main():
    # Setup
    tester = ReportingSystemTester()
    
    # Login
    if not tester.test_login("admin", "admin123"):
        print("❌ Login failed, stopping tests")
        return 1
    
    # Get report templates
    templates_success, templates_data = tester.test_get_report_templates()
    if not templates_success:
        print("❌ Failed to get report templates, but continuing with tests")
    
    # Test report generation
    events_pdf_success = tester.test_generate_events_report_pdf()
    events_excel_success = tester.test_generate_events_report_excel()
    logs_pdf_success = tester.test_generate_logs_report_pdf()
    stats_pdf_success = tester.test_generate_statistics_report_pdf()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    # Summary of report generation tests
    print("\n📋 Report Generation Summary:")
    print(f"Events PDF Report: {'✅ Success' if events_pdf_success else '❌ Failed'}")
    print(f"Events Excel Report: {'✅ Success' if events_excel_success else '❌ Failed'}")
    print(f"Logs PDF Report: {'✅ Success' if logs_pdf_success else '❌ Failed'}")
    print(f"Statistics PDF Report: {'✅ Success' if stats_pdf_success else '❌ Failed'}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())