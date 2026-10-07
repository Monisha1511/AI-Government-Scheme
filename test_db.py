from database import fetch_all_schemes
from eligibility import get_eligible_schemes
from ranking import rank_schemes, generate_reason
from llm_handler import generate_llm_explanation

schemes = fetch_all_schemes()

user = {
    "age": 25,
    "income": 200000,
    "state": "Central",
    "category": "Farmer"
}

eligible = get_eligible_schemes(user, schemes)
ranked = rank_schemes(user, eligible)

top_scheme = ranked[0]

reasons = generate_reason(user, top_scheme)

llm_output = generate_llm_explanation(user, top_scheme, reasons)

print(llm_output)