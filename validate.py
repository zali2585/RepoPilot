import subprocess
import sys

def run_tests(test_file):
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", 
         "-s", "demo", "-p", test_file, "-v"],
        capture_output=True,
        text=True,
    )
    passed = result.returncode == 0
    return passed, result.stderr