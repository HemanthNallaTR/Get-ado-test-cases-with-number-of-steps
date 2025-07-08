"""
Direct Azure DevOps API Test Case Extraction Script
====================================================
This script extracts test case data from Azure DevOps using direct REST API calls.
No MCP (Model Context Protocol) required - just a Personal Access Token (PAT).

Requirements:
- Azure DevOps Personal Access Token (PAT) with Test Plans read permissions
- Python packages: requests, json, os, re, base64, pandas, openpyxl

Setup:
1. Set environment variable: AZURE_DEVOPS_PAT=your_pat_token_here
2. Run: python extract_test_cases.py

Output:
- 57 JSON files in json_output folder (Suite_1410044_TestCases.json to Suite_1410100_TestCases.json)
- 57 Excel files in excel_output folder (Suite_1410044_TestCases.xlsx to Suite_1410100_TestCases.xlsx)
- Each file contains structured test case data with step counts and assignments
"""

import json
import os
import re
import requests
import base64
import time
import argparse
from datetime import datetime

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  Warning: pandas not installed. Excel conversion will be skipped.")
    print("Install with: pip install pandas openpyxl")

class AzureDevOpsClient:
    def __init__(self, organization, project, pat_token):
        self.organization = organization
        self.project = project
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis"
        
        # Create authorization header
        credentials = f":{pat_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    def get_test_cases_for_suite(self, plan_id, suite_id):
        """Get test cases for a specific test suite with detailed work item info"""
        try:
            # Step 1: Get test cases from suite
            url = f"{self.base_url}/testplan/Plans/{plan_id}/Suites/{suite_id}/TestCase?api-version=7.1"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle response format - Azure DevOps returns data in 'value' array
            if isinstance(data, dict) and 'value' in data:
                test_cases = data['value']
            elif isinstance(data, list):
                test_cases = data
            else:
                print(f"⚠️  Unexpected response format for suite {suite_id}")
                return []
            
            # Step 2: Extract work item IDs
            if not test_cases:
                return []
            
            work_item_ids = []
            for tc in test_cases:
                if 'workItem' in tc and 'id' in tc['workItem']:
                    work_item_ids.append(tc['workItem']['id'])
            
            if not work_item_ids:
                return []
            
            # Step 3: Get detailed work item data with all fields
            ids_str = ','.join(map(str, work_item_ids))
            url = f"https://dev.azure.com/{self.organization}/_apis/wit/workitems?ids={ids_str}&$expand=all&api-version=7.1"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            work_items_data = response.json()
            
            # Handle work items response format
            if isinstance(work_items_data, dict) and 'value' in work_items_data:
                return work_items_data['value']
            elif isinstance(work_items_data, list):
                return work_items_data
            else:
                return []
        
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout for suite {suite_id} - retrying...")
            time.sleep(2)
            # Simple retry logic
            try:
                return self.get_test_cases_for_suite(plan_id, suite_id)
            except:
                print(f"❌ Retry failed for suite {suite_id}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error for suite {suite_id}: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error for suite {suite_id}: {e}")
            return []

def count_steps_from_xml(steps_xml):
    """Count test steps from ADO XML format"""
    if not steps_xml:
        return 0
    return len(re.findall(r'<step id=', steps_xml))

def process_ado_response(work_items, suite_id):
    """Process Azure DevOps work items to our JSON format"""
    
    if not work_items:
        return {
            "suiteId": suite_id,
            "suiteName": f"Suite_{suite_id}",
            "testCases": []
        }
    
    suite_name = f"Suite_{suite_id}"
    test_cases = []
    
    for work_item in work_items:
        # Direct API returns work items with 'fields' structure
        if "fields" in work_item:
            fields = work_item["fields"]
            
            # Extract basic information
            test_case_id = work_item.get("id")
            test_case_name = fields.get("System.Title", "")
            
            # Extract test steps from Microsoft.VSTS.TCM.Steps field
            steps_xml = fields.get("Microsoft.VSTS.TCM.Steps", "")
            number_of_steps = count_steps_from_xml(steps_xml)
            
            # Extract other fields
            assigned_to_obj = fields.get("System.AssignedTo", {})
            if isinstance(assigned_to_obj, dict):
                assigned_to = assigned_to_obj.get("displayName", "")
            else:
                assigned_to = str(assigned_to_obj) if assigned_to_obj else ""
            
            # Clean up assigned_to field (remove email)
            if assigned_to and "<" in assigned_to:
                assigned_to = assigned_to.split("<")[0].strip()
            
            test_cases.append({
                "testCaseId": test_case_id,
                "testCaseName": test_case_name,
                "numberOfSteps": number_of_steps,
                "assignedTo": assigned_to
            })
    
    return {
        "suiteId": suite_id,
        "suiteName": suite_name,
        "testCases": test_cases
    }

def create_suite_json(suite_data, json_output_dir):
    """Create JSON file with proper structure"""
    suite_id = suite_data["suiteId"]
    
    json_content = {
        "testPlan": {
            "id": 1410043,
            "name": "Corporate Tax Test Plan"
        },
        "project": "OnesourceGCR",
        "suite": suite_data,
        "summary": {
            "totalTestCases": len(suite_data.get("testCases", [])),
            "suiteId": suite_id,
            "generatedAt": datetime.now().isoformat(),
            "hasErrors": False
        }
    }
    
    os.makedirs(json_output_dir, exist_ok=True)
    
    filename = f"Suite_{suite_id}_TestCases.json"
    filepath = os.path.join(json_output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_content, f, indent=2, ensure_ascii=False)
    
    test_count = len(suite_data.get("testCases", []))
    print(f"✓ Created JSON: {filename} with {test_count} test cases")
    
    return filepath

def create_suite_excel(suite_data, excel_output_dir):
    """Create Excel file from suite data"""
    if not PANDAS_AVAILABLE:
        print("⚠️  Skipping Excel creation - pandas not installed")
        return None
        
    suite_id = suite_data["suiteId"]
    
    try:
        # Create Excel output directory
        os.makedirs(excel_output_dir, exist_ok=True)
        
        # Prepare data for Excel
        test_cases = suite_data.get("testCases", [])
        if not test_cases:
            # Create empty Excel file
            df = pd.DataFrame(columns=[
                "Test Case ID", "Test Case Name", "Number of Steps", "Assigned To"
            ])
        else:
            # Convert test cases to DataFrame
            df_data = []
            for tc in test_cases:
                df_data.append({
                    "Test Case ID": tc.get("testCaseId", ""),
                    "Test Case Name": tc.get("testCaseName", ""),
                    "Number of Steps": tc.get("numberOfSteps", 0),
                    "Assigned To": tc.get("assignedTo", "")
                })
            
            df = pd.DataFrame(df_data)
        
        # Create Excel file
        filename = f"Suite_{suite_id}_TestCases.xlsx"
        filepath = os.path.join(excel_output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Write test cases sheet
            df.to_excel(writer, sheet_name='Test Cases', index=False)
            
            # Write summary sheet
            summary_data = {
                "Metric": ["Suite ID", "Suite Name", "Total Test Cases", "Generated At"],
                "Value": [
                    suite_id,
                    suite_data.get("suiteName", f"Suite_{suite_id}"),
                    len(test_cases),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        print(f"✓ Created Excel: {filename} with {len(test_cases)} test cases")
        return filepath
        
    except Exception as e:
        print(f"❌ Error creating Excel file for suite {suite_id}: {str(e)}")
        return None

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Extract test cases from Azure DevOps Test Plans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_test_cases.py                    # Extract all suites (1410044 to 1410100)
  python extract_test_cases.py --suites 1410044   # Extract only suite 1410044
  python extract_test_cases.py --suites 1410044 1410045 1410050  # Extract specific suites
  python extract_test_cases.py --range 1410044 1410048  # Extract suites 1410044 to 1410048
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--suites', 
        type=int, 
        nargs='+',
        help='Specific suite IDs to extract (e.g., --suites 1410044 1410045 1410050)'
    )
    group.add_argument(
        '--range',
        type=int,
        nargs=2,
        metavar=('START', 'END'),
        help='Range of suite IDs to extract (e.g., --range 1410044 1410048)'
    )
    
    parser.add_argument(
        '--json-dir',
        default='json_output',
        help='Directory for JSON output files (default: json_output)'
    )
    
    parser.add_argument(
        '--excel-dir',
        default='excel_output',
        help='Directory for Excel output files (default: excel_output)'
    )
    
    return parser.parse_args()

def get_suite_ids_to_process(args):
    """Get list of suite IDs to process based on command line arguments"""
    if args.suites:
        # Specific suite IDs provided
        return args.suites
    elif args.range:
        # Range provided
        start_id, end_id = args.range
        if start_id > end_id:
            print(f"❌ ERROR: Start suite ID ({start_id}) must be less than or equal to end suite ID ({end_id})")
            return []
        return list(range(start_id, end_id + 1))
    else:
        # Default range
        return list(range(1410044, 1410101))  # 1410044 to 1410100

def extract_all_test_cases():
    """Main function to extract test cases for all suites"""
    
    print("Azure DevOps Direct API Test Case Extraction")
    print("=" * 50)
    
    # Check for PAT token
    pat_token = os.environ.get('AZURE_DEVOPS_PAT')
    if not pat_token:
        print("❌ ERROR: AZURE_DEVOPS_PAT environment variable not set")
        print("\nTo fix this:")
        print("1. Create a Personal Access Token in Azure DevOps")
        print("2. Set environment variable: AZURE_DEVOPS_PAT=your_token_here")
        print("3. Restart this script")
        return
    
    print(f"✅ PAT token found (length: {len(pat_token)})")
    
    # Initialize Azure DevOps client
    client = AzureDevOpsClient("tr-corp-tax", "OnesourceGCR", pat_token)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Get suite IDs to process
    suite_ids_to_process = get_suite_ids_to_process(args)
    if not suite_ids_to_process:
        print("⚠️  No valid suite IDs to process - check your input parameters")
        return
    
    # Setup output directories
    json_output_dir = args.json_dir
    excel_output_dir = args.excel_dir
    
    # Counters for summary
    processed_count = 0
    error_count = 0
    total_test_cases = 0
    
    # Display what we're going to process
    if len(suite_ids_to_process) <= 10:
        print(f"Extracting test cases for suites: {suite_ids_to_process}")
    else:
        print(f"Extracting test cases for {len(suite_ids_to_process)} suites: {suite_ids_to_process[0]} to {suite_ids_to_process[-1]}")
    print(f"JSON output directory: {json_output_dir}")
    print(f"Excel output directory: {excel_output_dir}")
    print("-" * 50)
    
    for suite_id in suite_ids_to_process:
        print(f"Processing suite {suite_id}...")
        
        try:
            # Get test case data from Azure DevOps
            work_items = client.get_test_cases_for_suite(1410043, suite_id)
            
            if work_items:
                print(f"  ✓ Retrieved {len(work_items)} work items from API")
            else:
                print(f"  ⚠️  No test cases found for suite {suite_id}")
            
            # Process the data
            suite_data = process_ado_response(work_items, suite_id)
            
            # Create JSON file
            create_suite_json(suite_data, json_output_dir)
            
            # Create Excel file (if pandas is available)
            if PANDAS_AVAILABLE:
                create_suite_excel(suite_data, excel_output_dir)
            
            processed_count += 1
            total_test_cases += len(suite_data.get("testCases", []))
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  ❌ Error processing suite {suite_id}: {str(e)}")
            error_count += 1
            continue
    
    # Print summary
    print("\n" + "=" * 50)
    print("EXTRACTION SUMMARY:")
    print(f"Total Suites Processed: {processed_count}")
    print(f"Total Errors: {error_count}")
    print(f"Total Test Cases Extracted: {total_test_cases}")
    print(f"JSON Output Directory: {json_output_dir}")
    print(f"Excel Output Directory: {excel_output_dir}")
    print("=" * 50)
    
    if total_test_cases > 0:
        print("🎉 SUCCESS: Real test case data extracted and converted to JSON and Excel!")
    else:
        print("⚠️  No test cases found - check permissions and suite IDs")

if __name__ == "__main__":
    extract_all_test_cases()
