from validate import run_tests
from pathlib import Path
from patch import propose_patch
import argparse

MAX_PATCH_ATTEMPTS = 3

parser = argparse.ArgumentParser()
parser.add_argument("file", type=Path)
parser.add_argument("--test-file", type=Path, required=True)
args = parser.parse_args()

passed, report = run_tests(args.test_file)


if passed:
    print("baseline tests passed")
    print(report)
else:
    print("baseline tests failed")
    source = args.file.read_text(encoding="utf-8")
    test_source = args.test_file.read_text(encoding="utf-8")
    attempt_history = []
    for attempt in range(1, 4):
        candidate = propose_patch(source, test_source, report, attempt_history)
        try:
            args.file.write_text(candidate, encoding="utf-8")
            patch_passed, patch_report = run_tests(args.test_file)
        finally:
            args.file.write_text(source, encoding="utf-8")
        attempt_history.append({
            "attempt": attempt,
            "candidate": candidate,
            "passed": patch_passed,
            "report": patch_report
        })
        if patch_passed:
            print("Patch passed: ")
            print(patch_report)
            break
    if not patch_passed:
        print("All 3 patch attempts failed. Escalate to human review")

    

