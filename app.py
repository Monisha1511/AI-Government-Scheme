import streamlit as st
from database import fetch_all_schemes
from eligibility import get_eligible_schemes
from ranking import rank_schemes
from llm_handler import (
    extract_user_profile,
    generate_llm_explanation,
    generate_llm_rejection_reason,
    rag_scheme_advisor,
    ask_llm
)
import json
from vector_search import retrieve_relevant_schemes
# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Government Scheme Advisor",
    page_icon="🇮🇳",
    layout="wide"   # 🔥 IMPORTANT CHANGE
)
# ================= SESSION =================
if "ranked_results" not in st.session_state:
    st.session_state.ranked_results = None

if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if "messages" not in st.session_state:
    st.session_state.messages = []
# ================= HEADER =================
st.title("🇮🇳 AI-Based Government Decision Intelligence System")
st.caption("LLM + Multi-Criteria Decision Model")
st.markdown("---")
# ================= MAIN LAYOUT =================
left_col, right_col = st.columns([1, 1.2])  # 🔥 SPLIT SCREEN
# ==================================================
# LEFT SIDE → INPUT
# ==================================================
with left_col:

    st.header("Choose Input Mode")

    input_mode = st.radio(
        "Select how you want to enter your profile",
        ["AI Describe Profile", "Manual Form"]
    )

    # ---------------- AI MODE ----------------
    if input_mode == "AI Describe Profile":

        st.subheader("💬 Describe Your Profile")

        user_text = st.text_area(
            "Example: I am a 28 year old farmer earning 2 lakhs from Tamil Nadu"
        )

        if st.button("🧠 Analyze Using AI"):

            if not user_text.strip():
                st.warning("Please enter your profile description.")

            else:
                with st.spinner("Extracting profile..."):

                    profile_json = extract_user_profile(user_text)

                    try:
                        user = json.loads(profile_json)
                    except:
                        st.error("AI could not extract profile")
                        st.stop()

                    st.success("Profile Extracted")
                    st.json(user)

                    schemes = fetch_all_schemes()
                    eligible = get_eligible_schemes(user, schemes)

                    if not eligible:
                        st.error("No eligible schemes found.")

                        reason = generate_llm_rejection_reason(user, schemes)
                        st.write(reason)

                    else:
                        ranked = rank_schemes(user, eligible)
                        st.session_state.ranked_results = ranked
                        st.session_state.user_profile = user

    # ---------------- MANUAL MODE ----------------
    else:

        st.subheader("📋 Enter Your Details")

        age = st.slider("Age", 18, 70, 25)

        income_option = st.selectbox(
            "Income",
            ["Below ₹1.5L", "₹1.5L - ₹3L", "₹3L - ₹6L", "Above ₹6L"]
        )

        state = st.selectbox(
            "State",
            ["Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh", "Central"]
        )

        category = st.selectbox(
            "Category",
            ["General", "OBC", "MBC", "SC", "ST"]
        )

        occupation = st.selectbox(
            "Occupation",
            ["Farmer", "Student", "Worker", "Unemployed"]
        )

        if st.button("🔍 Find Schemes"):

            income_map = {
                "Below ₹1.5L": 150000,
                "₹1.5L - ₹3L": 300000,
                "₹3L - ₹6L": 600000,
                "Above ₹6L": 800000
            }

            user = {
                "age": age,
                "income": income_map[income_option],
                "state": state,
                "category": category,
                "occupation": occupation
            }

            st.json(user)

            schemes = fetch_all_schemes()
            eligible = get_eligible_schemes(user, schemes)

            if not eligible:
                st.error("No eligible schemes found.")
            else:
                ranked = rank_schemes(user, eligible)
                st.session_state.ranked_results = ranked
                st.session_state.user_profile = user
# ==================================================
# RIGHT SIDE → OUTPUT
# ==================================================
with right_col:

    if st.session_state.ranked_results:

        ranked = st.session_state.ranked_results
        user = st.session_state.user_profile
        schemes = fetch_all_schemes()

        st.subheader("📊 AI Dashboard")

        total = len(schemes)
        eligible = len(ranked)
        avg = sum(s['score'] for s in ranked) / len(ranked)
        best = ranked[0]['score']

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Schemes", total)
        c2.metric("Eligible", eligible)
        c3.metric("Avg Score", f"{round(avg,1)}%")
        c4.metric("Best Score", f"{best}%")

        st.markdown("---")

        # 🎯 TOP SCHEME
        scheme = ranked[0]

        st.subheader(f"📌 {scheme['scheme_name']}")
        st.progress(scheme['score'] / 100)
        st.write(f"Match Score: {scheme['score']}%")

        explanation = generate_llm_explanation(user, scheme)

        st.markdown("### 🤖 AI Explanation")
        st.write(explanation)

        if scheme.get("apply_link"):
            st.link_button("Apply Now", scheme["apply_link"])

        st.markdown("---")
        # 🤖 AI ADVISOR
        st.subheader("🤖 AI Advisor")

        try:
            advice = rag_scheme_advisor(user, ranked)
            st.write(advice)
        except:
            st.write("Advisor unavailable")
# ==================================================
# CHATBOT (FULL WIDTH)
# ==================================================
st.markdown("---")
st.header("💬 AI Chatbot")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask about schemes...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    schemes = fetch_all_schemes()
    relevant = retrieve_relevant_schemes(prompt, schemes)

    context = ""
    for s in relevant:
        context += f"{s['scheme_name']} - {s['benefits']}\n"

    answer = ask_llm(f"""
    Answer based on schemes:
    {context}

    Question: {prompt}
    """)

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})