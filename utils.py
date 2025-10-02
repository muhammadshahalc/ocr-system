# utils.py
def initialize_record():
    """Initialize an empty medical record structure."""
    return {
        "patient": {
            "name": None,
            "age": None,
            "gender": None,
            "date_of_report": None
        },
        "tests": [],
        "diagnosis": "Not Mentioned"
    }


def merge_records(base_record, new_record):
    """Merge a new page record into the base record."""
    if not new_record or not isinstance(new_record, dict):
        return base_record

    # Merge patient info
    for key in base_record["patient"]:
        if base_record["patient"][key] is None and new_record.get("patient", {}).get(key) is not None:
            base_record["patient"][key] = new_record["patient"][key]

    # Merge tests (avoid duplicates)
    existing_tests = {test['test_name'] for test in base_record["tests"]}
    for test in new_record.get("tests", []):
        if test.get('test_name') and test['test_name'] not in existing_tests:
            base_record["tests"].append(test)
            existing_tests.add(test['test_name'])

    # Merge diagnosis
    new_diag = new_record.get("diagnosis")
    if new_diag and isinstance(new_diag, str) and new_diag.strip() and new_diag != "Not Mentioned":
        if base_record["diagnosis"] and base_record["diagnosis"] != "Not Mentioned":
            base_record["diagnosis"] += "; " + new_diag
        else:
            base_record["diagnosis"] = new_diag

    if not base_record["diagnosis"]:
        base_record["diagnosis"] = "Not Mentioned"

    return base_record
