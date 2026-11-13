from validate import run_tests
from pathlib import Path
from patch import propose_patch
import argparse
from checks import duplicate_reason
from ollama import ResponseError
from escalate import save_escalation

MAX_PATCH_ATTEMPTS = 3

parser = argparse.ArgumentParser()
parser.add_argument("file", type=Path)
parser.add_argument("--test-file", type=Path, required=True)
parser.add_argument("--report-dir", type=Path, default=Path("reports"))
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
    infrastructure_failed = False
    for attempt in range(1, 4):
        # checks if patch is syntactically correct code/not empty
        try:
            candidate = propose_patch(source, test_source, report, attempt_history)
        except (ConnectionError, ResponseError) as error:
            infrastructure_failed = True
            print(f"Ollama error: {error}")
            print("Stopping RepoPilot: model services unavailable or request failed.")
            break
        except (ValueError, SyntaxError) as error:
            print(f"Attempt {attempt}: Generation failed: {error}")

            attempt_history.append({
                "attempt": attempt,
                "candidate": None,
                "passed": False,
                "report": str(error),
                "status": "generation_failed"
            })

            continue
        # checks if patch already exists
        reason = duplicate_reason(candidate, source, attempt_history)
        if reason:
            print(f"Attempt {attempt} rejected: {reason}")
            attempt_history.append({
                "attempt": attempt,
                "candidate": candidate,
                "passed": False,
                "report": reason,
                "status": "duplicate"

            })
            continue
        # temporarily apply and run unit tests
        try:
            args.file.write_text(candidate, encoding="utf-8")

            print("Starting candidate validation")
            patch_passed, patch_report = run_tests(args.test_file)
            print("Validation finished:", patch_passed)
            print("Validation report:", patch_report)
        finally:
            args.file.write_text(source, encoding="utf-8")
        attempt_history.append({
            "attempt": attempt,
            "candidate": candidate,
            "status": "passed" if patch_passed else "test_failed",
            "passed": patch_passed,
            "report": patch_report
        })
        if patch_passed:
            print("Patch passed: ")
            print(patch_report)
            break
    for entry in attempt_history:
        print(
            f"Attempt {entry['attempt']}:",
            "PASS" if entry["passed"] else "FAIL"
            )
    if not infrastructure_failed and len(attempt_history) == 3 and not any(entry["passed"] for entry in attempt_history):
        report_path = save_escalation(
            args.file,
            args.test_file,
            source,
            test_source,
            report,
            attempt_history,
            args.report_dir
    )

        print(f"Escalation report saved: {report_path}")

    

