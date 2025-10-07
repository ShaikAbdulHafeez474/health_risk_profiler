from typing import Tuple, List, Dict, Any

# Simple mapping rules for factor extraction
def extract_factors(answers: Dict[str, Any]) -> Tuple[List[str], float]:
    factors = []
    # Smoking
    if "smoker" in answers and bool(answers["smoker"]):
        factors.append("smoking")

    # Diet
    diet = answers.get("diet", "")
    if isinstance(diet, str):
        if any(x in diet.lower() for x in ["high sugar", "sugar", "junk", "fast food", "fried", "fatty"]):
            factors.append("poor diet")

    # Exercise
    ex = answers.get("exercise", "")
    if isinstance(ex, str) and any(x in ex.lower() for x in ["rare", "never", "rarely", "none"]):
        factors.append("low exercise")

    # Alcohol
    alc = answers.get("alcohol", "")
    if isinstance(alc, str) and any(x in alc.lower() for x in ["often", "daily", "frequent"]):
        factors.append("high alcohol")

    # Age-related factor
    age = answers.get("age")
    if isinstance(age, int):
        if age >= 60:
            factors.append("age>60")
        elif age >= 40:
            factors.append("age>40")

    # confidence: more factors found -> higher confidence in factors list
    factors_conf = 0.7 + 0.15 * min(len(factors), 2)  # up to ~1.0
    return factors, round(min(factors_conf, 0.99), 2)


def score_risk(answers: Dict[str, Any], factors: List[str]) -> Dict[str, Any]:
    """
    Rule-based scoring:
      - smoking: +30
      - poor diet: +20
      - low exercise: +20
      - high alcohol: +15
      - age>40: +10
      - age>60: +20 (instead of age>40)
    Thresholds:
      0-30 low, 31-60 medium, >60 high
    """
    score = 0
    rationale = []

    if "smoking" in factors:
        score += 30
        rationale.append("smoking")

    if "poor diet" in factors:
        score += 20
        rationale.append("poor diet")

    if "low exercise" in factors:
        score += 20
        rationale.append("low activity")

    if "high alcohol" in factors:
        score += 15
        rationale.append("high alcohol use")

    if "age>60" in factors:
        score += 20
        rationale.append("age > 60")
    elif "age>40" in factors:
        score += 10
        rationale.append("age > 40")

    # cap score at 100
    score = max(0, min(score, 100))

    if score <= 30:
        level = "low"
    elif score <= 60:
        level = "medium"
    else:
        level = "high"

    return {"score": score, "risk_level": level, "rationale": rationale}


def generate_recommendations(factors: List[str]) -> List[str]:
    recs = []
    if "smoking" in factors:
        recs.append("Consider smoking cessation resources and counseling.")
    if "poor diet" in factors:
        recs.append("Reduce high-sugar foods; increase fruits, vegetables, and whole grains.")
    if "low exercise" in factors:
        recs.append("Aim for at least 30 minutes of moderate activity (walking) daily.")
    if "high alcohol" in factors:
        recs.append("Reduce alcohol intake; consult healthcare provider for safe reduction.")
    if "age>60" in factors or "age>40" in factors:
        recs.append("Schedule regular health check-ups and lipid/blood pressure monitoring.")
    if not recs:
        recs.append("Maintain current healthy habits; re-evaluate annually.")
    return recs
