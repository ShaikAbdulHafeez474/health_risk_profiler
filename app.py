
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from ocr import image_to_text
from parser import parse_answers_from_text, parse_answers_from_json
from risk_engine import (
    extract_factors,
    score_risk,
    generate_recommendations,
)
from utils.validators import validate_required_fields, REQUIRED_FIELDS

app = FastAPI(title="Health Risk Profiler", version="1.0")

class TextInput(BaseModel):
    answers: Dict[str, Any]

@app.post("/analyze-text")
async def analyze_text(input: TextInput):
    answers, missing, conf = parse_answers_from_json(input.answers)
    # guardrail
    if validate_required_fields(answers):
        return JSONResponse(
            status_code=400,
            content={"status": "incomplete_profile", "reason": ">50% fields missing", "answers": answers},
        )

    factors, factors_conf = extract_factors(answers)
    score_info = score_risk(answers, factors)
    recs = generate_recommendations(factors)

    result = {
        "answers": answers,
        "missing_fields": missing,
        "confidence": round(conf, 2),
        "factors": factors,
        "factors_confidence": round(factors_conf, 2),
        "risk_level": score_info["risk_level"],
        "score": score_info["score"],
        "rationale": score_info["rationale"],
        "recommendations": recs,
        "status": "ok"
    }
    return JSONResponse(content=result)


@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Step 1: Read file
        image_bytes = await file.read()

        # Step 2: OCR
        print("Running image_to_text()...")
        text, ocr_conf = image_to_text(image_bytes)
        print("OCR done.")

        # Step 3: Parse
        print("Running parse_answers_from_text()...")
        answers, missing, parse_conf = parse_answers_from_text(text)
        print("Parsing done.")

        # Step 4: Validation
        print("Validating fields...")
        if validate_required_fields(answers):
            return JSONResponse(
                status_code=400,
                content={"status": "incomplete_profile", "reason": ">50% fields missing", "raw_text": text},
            )

        # Step 5: Extraction + Scoring
        print("Extracting factors...")
        factors, factors_conf = extract_factors(answers)
        print("Scoring risk...")
        score_info = score_risk(answers, factors)
        print("Generating recommendations...")
        recs = generate_recommendations(factors)

        # Step 6: Success
        result = {
            "raw_text": text,
            "answers": answers,
            "missing_fields": missing,
            "confidence": round(ocr_conf * parse_conf, 2),
            "factors": factors,
            "factors_confidence": round(factors_conf, 2),
            "risk_level": score_info["risk_level"],
            "score": score_info["score"],
            "rationale": score_info["rationale"],
            "recommendations": recs,
            "status": "ok"
        }
        return JSONResponse(content=result)

    except Exception as e:
        import traceback
        print("ERROR TRACEBACK:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
