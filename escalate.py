import json
from pathlib import Path
from uuid import uuid4

def save_escalation(source_file, test_file, source,
        test_source, baseline_report, attempt_history, report_dir):
    report = {
        "status": "needs_human_review",
        "source_file": str(source_file),
        "test_file": str(test_file),
        "original_source": source,
        "test_source": test_source,
        "baseline_failure": baseline_report,
        "attempts": attempt_history
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"escalation-{uuid4().hex}.json"

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )
    return report_path