
from typing import List, Dict, Any

REQUIRED_FIELDS = ["age", "smoker", "exercise", "diet", "alcohol", "medical_history"]

def validate_required_fields(answers: Dict[str, Any]) -> bool:
    """
    Return True if >50% of required fields are missing (i.e., trigger guardrail).
    """
    missing = [f for f in REQUIRED_FIELDS if f not in answers]
    missing_ratio = len(missing) / len(REQUIRED_FIELDS)
    return missing_ratio > 0.5
