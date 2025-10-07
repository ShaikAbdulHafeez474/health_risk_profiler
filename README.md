# Health Risk Profiler (Backend) - Problem 6

Simple FastAPI backend that accepts a typed JSON survey or an uploaded scanned form image,
extracts answers (via simple parsing/OCR), maps to risk factors, computes a rule-based risk score,
and returns actionable, non-diagnostic recommendations.

## Features
- Accepts JSON (`/analyze-text`) and image uploads (`/analyze-image`).
- Uses EasyOCR for scanned form parsing.
- Rule-based factor extraction and scoring.
- Guardrail: returns `incomplete_profile` if >50% required fields missing.
- Produces JSON outputs consistent with submission guidelines.

## Setup (local)
1. Create a Python 3.9+ virtualenv and activate it.
2. Install dependencies:
