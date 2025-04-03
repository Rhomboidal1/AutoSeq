# run_tests.py
import os
import sys

# Calculate the project's root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels

# Add the project's root directory to sys.path
sys.path.append(project_root)

# Now we can import config.py
from AutoSeq.config import MseqConfig  

def run_tests():
    test_modules = [
        "test_regex.py",
        "test_path.py",
        "test_log_service.py"
    ]

    print("Running utility module tests:")
    print("=" * 50)

    for test_module in test_modules:
        print(f"\nRunning {test_module}:")
        print("-" * 50)
        # Construct the full path to the test module
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), test_module)
        # Execute the test module
        os.system(f"python {test_path}")
        print("-" * 50)

    print("\nAll tests completed")

if __name__ == "__main__":
    run_tests()