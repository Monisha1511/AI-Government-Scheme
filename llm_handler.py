from groq import Groq
import json
import re

# ==========================================
# Configure Groq API
# ==========================================
client = Groq(api_key="Your Own API key")


# ==========================================
# Safe LLM Call
# ==========================================


def ask_llm(prompt):
    
    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:

        if "429" in str(e):
            return "⚠️ AI quota reached. Please try again later."

        return "⚠️ AI service unavailable."


# ==========================================
# 1️⃣ Extract User Profile from Text
# (Regex → faster and no API needed)
# ==========================================
def extract_user_profile(user_text):

    try:

        # AGE
        age_match = re.search(r'(\d+)\s*year', user_text.lower())
        age = int(age_match.group(1)) if age_match else 0

        # INCOME
        income_match = re.search(r'(\d+(\.\d+)?)\s*lakh', user_text.lower())
        income = int(float(income_match.group(1)) * 100000) if income_match else 0

        # CATEGORY
        if "farmer" in user_text.lower():
            category = "Farmer"
        elif "student" in user_text.lower():
            category = "Student"
        elif "worker" in user_text.lower():
            category = "Worker"
        else:
            category = "General"

        # STATE
        states = ["tamil nadu", "kerala", "karnataka", "andhra pradesh", "central"]
        state = "Unknown"

        for s in states:
            if s in user_text.lower():
                state = s.title()
                break

        user = {
            "age": age,
            "income": income,
            "category": category,
            "state": state
        }

        return json.dumps(user)

    except:

        return json.dumps({
            "age": 0,
            "income": 0,
            "category": "Unknown",
            "state": "Unknown"
        })


# ==========================================
# 2️⃣ Generate Scheme Explanation
# ==========================================
def generate_llm_explanation(user, scheme):

    prompt = f"""
User Profile:
Age: {user['age']}
Income: {user['income']}
Category: {user['category']}
State: {user['state']}

Government Scheme:
Name: {scheme['scheme_name']}
Benefits: {scheme['benefits']}

Explain briefly why this scheme is suitable for the user.
"""

    response = ask_llm(prompt)

    if "⚠️" in response:
        return f"""
Recommended Scheme: {scheme['scheme_name']}

This scheme matches your eligibility criteria.

Benefits:
{scheme['benefits']}
"""

    return response


# ==========================================
# 3️⃣ Eligibility Rejection Analysis
# ==========================================
def generate_llm_rejection_reason(user, schemes):

    prompt = f"""
User Profile:
Age: {user['age']}
Income: {user['income']}
Category: {user['category']}
State: {user['state']}

Available Government Schemes:
{schemes}

Explain why the user may not qualify for these schemes.
Suggest possible improvements to become eligible.
"""

    return ask_llm(prompt)


# ==========================================
# 4️⃣ RAG Scheme Advisor
# ==========================================
def rag_scheme_advisor(user, schemes):

    if not schemes:
        return "No eligible schemes found."

    scheme_context = build_scheme_context(schemes)

    prompt = f"""
You are an AI Government Scheme Advisor.

User Profile:
Age: {user['age']}
Income: {user['income']}
Category: {user['category']}
State: {user['state']}

Available Schemes:
{scheme_context}

Instructions:
1. Recommend the BEST scheme for the user.
2. Explain why it matches the user profile.
3. Keep answer short (4-5 lines).

Answer:
"""

    return ask_llm(prompt)

def build_scheme_context(schemes):

    context = ""

    for s in schemes[:5]:
        context += f"""
Scheme Name: {s['scheme_name']}
Benefits: {s['benefits']}
Income Limit: {s['income_limit']}
Category: {s['category']}
State: {s['state']}
"""

    return context
