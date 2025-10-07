import re
from typing import Tuple, Dict, Any, List
from collections import defaultdict

# Define required fields that survey should contain (can be extended)
REQUIRED_FIELDS = ["age", "smoker", "exercise", "diet", "alcohol", "medical_history"]

def parse_answers_from_json(input_json: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], float]:
    """
    Normalize keys and values from pre-parsed JSON input.
    Returns (answers, missing_fields, confidence)
    """
    answers = {}
    missing = []
    # Normalize keys to lowercase
    for k, v in input_json.items():
        answers[k.lower()] = v

    # find missing required fields ratio
    for f in REQUIRED_FIELDS:
        if f not in answers:
            missing.append(f)

    # Confidence: more fields present -> higher confidence
    present_ratio = (len(REQUIRED_FIELDS) - len(missing)) / max(1, len(REQUIRED_FIELDS))
    confidence = 0.7 + 0.3 * present_ratio  # base 0.7 up to 1.0
    return answers, missing, confidence


def _bool_from_text(text: str) -> bool:
    text = text.strip().lower()
    yes_words = {"yes", "y", "true", "1", "yes."}
    return any(tok in text for tok in yes_words)


def parse_answers_from_text(raw_text: str) -> Tuple[Dict[str, Any], List[str], float]:
    """
    Heuristic parsing from OCR text or free text.
    Looks for common patterns like "Age: 42", "Smoker: yes", etc.
    Returns (answers, missing_fields, confidence)
    """
    answers = {}
    text = raw_text.replace("\r", "\n")
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # regex patterns
    age_re = re.compile(r"age[:\s]*([0-9]{1,3})", re.IGNORECASE)
    smoker_re = re.compile(r"smok(?:er|ing)[:\s]*(yes|no|y|n|true|false)", re.IGNORECASE)
    exercise_re = re.compile(r"exercise[:\s]*([a-zA-Z0-9\s\-]+)", re.IGNORECASE)
    diet_re = re.compile(r"diet[:\s]*([a-zA-Z0-9\s\-]+)", re.IGNORECASE)
    alcohol_re = re.compile(r"alcohol[:\s]*(yes|no|rarely|often|sometimes|none)", re.IGNORECASE)
    medhist_re = re.compile(r"medical history[:\s]*([a-zA-Z0-9\,\-\s]+)", re.IGNORECASE)

    # search whole text
    m = age_re.search(raw_text)
    if m:
        answers["age"] = int(m.group(1))

    m = smoker_re.search(raw_text)
    if m:
        answers["smoker"] = _bool_from_text(m.group(1))

    m = exercise_re.search(raw_text)
    if m:
        answers["exercise"] = m.group(1).strip().lower()

    m = diet_re.search(raw_text)
    if m:
        answers["diet"] = m.group(1).strip().lower()

    m = alcohol_re.search(raw_text)
    if m:
        answers["alcohol"] = m.group(1).strip().lower()

    m = medhist_re.search(raw_text)
    if m:
        answers["medical_history"] = m.group(1).strip().lower()

    # If not found in regex, attempt keyword heuristics per line
    if "age" not in answers:
        for l in lines:
            m = re.search(r"\b([0-9]{1,3})\b", l)
            if "age" in l.lower() and m:
                answers["age"] = int(m.group(1))
                break

    # missing fields
    missing = [f for f in REQUIRED_FIELDS if f not in answers]

    # confidence heuristic: proportion of found fields
    present_ratio = (len(REQUIRED_FIELDS) - len(missing)) / max(1, len(REQUIRED_FIELDS))
    confidence = 0.6 + 0.4 * present_ratio  # base 0.6 up to 1.0
    return answers, missing, confidence
