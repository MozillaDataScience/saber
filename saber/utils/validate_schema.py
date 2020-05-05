from jsonschema import validate
import json


experiment_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "publish_date": {"type": "string"},
        "author": {"type": "string"},
        "email": {"type": "string"},
        "file": {"type": "string"},
        "experiment_slug": {"type": "string"},
        "experimenter_name": {"type": "string"},
        "start_date": {"type": "string"},
        "last_date_full_data": {"type": "string"},
        "num_dates_enrollment": {"type": "number"},
        "analysis_start_days": {"type": "number"},
        "analysis_length_days": {"type": "number"},
        "n_resamples": {"type": "number"},
        "target_percent": {"type": "number"},
        "versions": {"type": "string"},
        "dataset_id": {"type": "string"},
        "metrics": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "user_defined_metrics": {
            "type": "object",
            "propertyNames": {
                "pattern": "^[A-Za-z_][A-Za-z0-9_]*$",
            }
        }
    },
    "required": [
        # required for mpr
        "title", "publish_date", "author", "file", "experiment_slug",
        # required for mozanalysis
        "start_date", "last_date_full_data", "num_dates_enrollment",
        "analysis_start_days", "analysis_length_days", "n_resamples",
        "dataset_id", "metrics"
    ]
}

def validate_schema(json_file):
    report = json.load(open(json_file))
    validate(instance=report, schema=experiment_schema)

    print("Schema validated. :)")

    return report