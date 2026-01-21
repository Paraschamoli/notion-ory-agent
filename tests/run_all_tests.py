import subprocess
import sys
import os

def run_test(test_file):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    result = subprocess.run([sys.executable, test_file], 
                          capture_output=True, 
                          text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"Errors:\n{result.stderr}")
    
    return result.returncode == 0

def main():
    """Run all test files."""
    test_files = [
        "test_config.py",
        "test_api.py", 
        "test_mcp.py",
        "test_notion.py",
        "test_kratos.py",
        "test_hydra.py"
    ]
    
    print("Running all tests for Notion Ory Agent")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            if run_test(test_path):
                passed += 1
            else:
                failed += 1
        else:
            print(f"\n⚠️  Test file not found: {test_file}")
    
    print(f"\n{'='*60}")
    print(f"Test Summary: {passed} passed, {failed} failed")
    print('='*60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)