def calculate_score(user, scheme):

    score = 0

    # Weights
    weights = {
        "income": 0.30,
        "age": 0.20,
        "category": 0.30,
        "state": 0.10,
        "occupation": 0.10
    }

    # Income Score
    if user["income"] <= scheme["income_limit"]:
        score += weights["income"]

    # Age Score
    if scheme["min_age"] <= user["age"] <= scheme["max_age"]:
        score += weights["age"]

    # Category Score
    if scheme["category"] == user["category"]:
        score += weights["category"]
    elif scheme["category"] == "General":
        score += weights["category"] * 0.5

    # State Score
    if scheme["state"] == user["state"] or scheme["state"] == "Central":
        score += weights["state"]

    # Occupation Relevance
    if user["category"].lower() in scheme["scheme_name"].lower():
        score += weights["occupation"]

    # Convert to percentage
    score = round(score * 100)

    return score


def rank_schemes(user, eligible_schemes):

    for scheme in eligible_schemes:
        scheme["score"] = calculate_score(user, scheme)

    ranked = sorted(eligible_schemes, key=lambda x: x["score"], reverse=True)

    return ranked