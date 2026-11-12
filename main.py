from validate import run_tests
from pathlib import Path
from patch import propose_patch
import argparse

MAX_PATCH_ATTEMPTS = 3
attempt_history = []
parser = argparse.ArgumentParser()
parser.add_argument("file", type=Path)
parser.add_argument("--test-file")
args = parser.parse_args()

passed, report = run_tests(args.test_file)

if passed:
    print("baseline tests passed")
    print(report)
else:
    print("baseline tests failed")
    source = args.file.read_text(encoding="utf-8")
    candidate = propose_patch(source)
    try:
        args.file.write_text(candidate, encoding="utf-8")
        patch_passed, patch_report = run_tests(args.test_file)
    finally:
        args.file.write_text(source, encoding="utf-8")
    attempt_history.append({
        "attempt": 1,
        "candidate": candidate,
        "passed": patch_passed,
        "report": patch_report
    })
    print("Patch passed: ", patch_passed)
    print(patch_report)
    

