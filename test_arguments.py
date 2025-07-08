"""
Test script to verify specific suite ID functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_test_cases import parse_arguments, get_suite_ids_to_process

def test_argument_parsing():
    """Test different argument combinations"""
    
    print("🧪 Testing argument parsing...")
    
    # Test cases
    test_cases = [
        # (args, expected_description)
        ([], "Default range (1410044 to 1410100)"),
        (["--suites", "1410044"], "Single suite"),
        (["--suites", "1410044", "1410045", "1410050"], "Multiple specific suites"),
        (["--range", "1410044", "1410048"], "Range of suites"),
        (["--suites", "1410044", "--json-dir", "custom_json"], "Custom JSON directory"),
        (["--range", "1410044", "1410046", "--excel-dir", "custom_excel"], "Custom Excel directory"),
    ]
    
    for args, description in test_cases:
        try:
            print(f"\n📋 Testing: {description}")
            print(f"   Arguments: {args}")
            
            # Mock sys.argv
            original_argv = sys.argv
            sys.argv = ["extract_test_cases.py"] + args
            
            # Parse arguments
            parsed_args = parse_arguments()
            suite_ids = get_suite_ids_to_process(parsed_args)
            
            print(f"   Suite IDs: {suite_ids[:5]}{'...' if len(suite_ids) > 5 else ''} (total: {len(suite_ids)})")
            print(f"   JSON dir: {parsed_args.json_dir}")
            print(f"   Excel dir: {parsed_args.excel_dir}")
            print("   ✅ Success")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        finally:
            # Restore sys.argv
            sys.argv = original_argv

def test_edge_cases():
    """Test edge cases and error conditions"""
    
    print("\n🧪 Testing edge cases...")
    
    # Test invalid range
    try:
        original_argv = sys.argv
        sys.argv = ["extract_test_cases.py", "--range", "1410048", "1410044"]  # Invalid: start > end
        
        parsed_args = parse_arguments()
        suite_ids = get_suite_ids_to_process(parsed_args)
        
        if not suite_ids:
            print("✅ Invalid range properly handled (empty list returned)")
        else:
            print(f"❌ Invalid range not handled properly: {suite_ids}")
            
    except Exception as e:
        print(f"❌ Error in invalid range test: {e}")
    finally:
        sys.argv = original_argv

if __name__ == "__main__":
    print("🚀 Testing Azure DevOps Script Argument Parsing")
    print("=" * 60)
    
    test_argument_parsing()
    test_edge_cases()
    
    print("\n✅ Argument parsing tests completed!")
    print("\nExample usage:")
    print("  python extract_test_cases.py --suites 1410044")
    print("  python extract_test_cases.py --suites 1410044 1410045")
    print("  python extract_test_cases.py --range 1410044 1410048")
