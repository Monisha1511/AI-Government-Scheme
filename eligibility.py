def check_eligibility(user, scheme):
    # Age Check
    if not (scheme["min_age"] <= user["age"] <= scheme["max_age"]):
        return False

    # Income Check
    if user["income"] > scheme["income_limit"]:
        return False

    # State Check (Central schemes allowed for all states)
    if scheme["state"] != "Central" and scheme["state"] != user["state"]:
        return False

    # Category Check (General means open to all)
    if scheme["category"] != "General" and scheme["category"] != user["category"]:
        return False

    return True

def get_eligible_schemes(user, schemes):
    eligible = []
    for scheme in schemes:
        if check_eligibility(user, scheme):
            eligible.append(scheme)
    return eligible