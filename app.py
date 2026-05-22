# app.py
# Streamlit UI — wired to AI agents via crew.py
# Agentic AI Banking Capstone Project 2026: Engineered and Designed by Stephanie Wong

import os
import json
import random
import streamlit as st
from crew import run_crew
from database.db_setup import setup_database, get_all_tickets
from evaluation import log_interaction, get_evaluation_summary

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Voillà — Agentic AI Banking Customer Support",
    layout="wide"
)

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
    <style>
    .main .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 900px;
        margin: auto;
        padding-top: 0.5rem;
    }
    table {
        width: 100%;
        word-break: break-word;
        white-space: normal;
    }
    td, th {
        white-space: normal !important;
        word-wrap: break-word !important;
        max-width: 200px;
    }
    footer {visibility: hidden;}
    [data-testid="stChatMessageAvatarUser"] {
        background-color: #1A6FBF !important;
    }
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #1E8A4A !important;
    }
    </style>
""", unsafe_allow_html=True)

# ── Setup database on startup ─────────────────────────────
setup_database()

# ── Test message pools ────────────────────────────────────
POSITIVE_MESSAGES = [
    "Thanks for sorting out my net banking login issue.",
    "I really appreciate how quickly you resolved my account problem.",
    "Your team did a great job helping me with my transfer issue.",
    "Thank you so much for the help with my credit card.",
    "I'm really happy with how my issue was handled today.",
]

NEGATIVE_MESSAGES = [
    "My debit card replacement still hasn't arrived.",
    "I've been charged twice for the same transaction.",
    "My online banking keeps logging me out automatically.",
    "I can't access my account and nobody is helping me.",
    "My transfer has been pending for 3 days and nothing has happened.",
]

QUERY_MESSAGES = [
    "Could you check the status of ticket 650932?",
    "What is the current status of my support ticket 784521?",
    "Can you tell me if ticket 392841 has been resolved?",
    "I'd like an update on ticket 517293 please.",
]

ESCALATION_MESSAGES = [
    "I need to speak to a real person about my account.",
    "Can you connect me to a human representative please?",
    "I want to talk to a manager about this issue.",
    "Please transfer me to someone who can actually help me.",
    "I need a real human agent, not an automated system.",
]

# ── Logo ──────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("assets/voilla_logo.png", use_container_width=True)
    except:
        st.title("Voillà")

st.markdown("<p style='text-align:center; color:#334155; font-size:14px; margin-top:-10px;'>Agentic AI Banking Customer Support</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b; font-size:12px; margin-top:-8px;'>Designed and engineered by Stephanie Wong</p>", unsafe_allow_html=True)

st.divider()

# ── Initialize session state ──────────────────────────────
if "customer_name" not in st.session_state:
    st.session_state.customer_name = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_trace" not in st.session_state:
    st.session_state.last_trace = None

if "routing_log" not in st.session_state:
    st.session_state.routing_log = []

if "conversation_ended" not in st.session_state:
    st.session_state.conversation_ended = False

if "satisfaction_rating" not in st.session_state:
    st.session_state.satisfaction_rating = None

if "rating_submitted" not in st.session_state:
    st.session_state.rating_submitted = False

if "rating_message" not in st.session_state:
    st.session_state.rating_message = ""

if "greeting_shown" not in st.session_state:
    st.session_state.greeting_shown = False

# ── Screen 1: Name collection ─────────────────────────────
if st.session_state.customer_name is None:
    st.markdown("### Welcome to Voillà Banking Customer Support")
    st.markdown("Please enter your first name so we can assist you personally.")
    st.write("")

    name_input = st.text_input("First name", label_visibility="collapsed", placeholder="Your first name")

    if st.button("Start Chat", type="primary"):
        if name_input.strip():
            st.session_state.customer_name = name_input.strip()
            st.rerun()
        else:
            st.warning("Please enter your name to continue.")

    st.stop()

# ── Screen 2: Main chat (only renders after name collected) ─
# ── Add greeting once per session ────────────────────────
if not st.session_state.greeting_shown:
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Hi {st.session_state.customer_name}, I'm an AI Customer Service Agent. How can I help you today?",
        "label": None,
        "is_greeting": True
    })
    st.session_state.greeting_shown = True

# ── Component B: Conversation view ───────────────────────
st.subheader("Customer Service Help Chat")

for message in st.session_state.messages:
    if message.get("is_divider"):
        st.markdown("---")
        st.caption("— New conversation started —")
        continue
    with st.chat_message(message["role"]):
        if message.get("label"):
            st.caption(f"🟢 {message['label']}")
        st.write(message["content"])

# ── End Conversation button ───────────────────────────────
if len(st.session_state.messages) > 1 and not st.session_state.conversation_ended:
    col_spacer, col_btn = st.columns([4, 1])
    with col_btn:
        if st.button("End Conversation", type="secondary"):
            st.session_state.conversation_ended = True
            st.rerun()

# ── Satisfaction rating ───────────────────────────────────
if st.session_state.conversation_ended and not st.session_state.rating_submitted:
    st.divider()
    st.subheader("How would you rate your experience today?")

    rating = st.radio(
        "Select a rating:",
        options=["⭐ 1 — Very Poor", "⭐⭐ 2 — Poor", "⭐⭐⭐ 3 — Neutral", "⭐⭐⭐⭐ 4 — Good", "⭐⭐⭐⭐⭐ 5 — Excellent"],
        horizontal=True,
        label_visibility="collapsed"
    )

    comment = st.text_input("Any additional comments? (optional)")

    if st.button("Submit Rating", type="primary"):
        score = int(rating.split("—")[0].strip().count("⭐"))
        st.session_state.satisfaction_rating = score
        st.session_state.rating_submitted = True

        if score <= 2:
            st.session_state.rating_message = "We're sorry your experience didn't meet expectations. Your feedback has been recorded and will be used to improve our service."
        elif score == 3:
            st.session_state.rating_message = "Thank you for your feedback. We'll use this to improve our service."
        else:
            st.session_state.rating_message = "Thank you! We're glad we could help today."

        log_path = "logs/agent_log.json"
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append({
            "type": "satisfaction_rating",
            "rating": score,
            "comment": comment,
            "total_messages": len(st.session_state.messages)
        })

        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)

        st.rerun()

# ── Rating confirmation + Start New Conversation ──────────
if st.session_state.rating_submitted:
    if st.session_state.satisfaction_rating <= 2:
        st.error(f"{'⭐' * st.session_state.satisfaction_rating} — {st.session_state.get('rating_message', '')}")
    elif st.session_state.satisfaction_rating == 3:
        st.warning(f"{'⭐' * st.session_state.satisfaction_rating} — {st.session_state.get('rating_message', '')}")
    else:
        st.success(f"{'⭐' * st.session_state.satisfaction_rating} — {st.session_state.get('rating_message', '')}")

    st.divider()
    if st.button("Start New Conversation", type="primary"):
        st.session_state.messages.append({"is_divider": True})
        st.session_state.conversation_ended = False
        st.session_state.rating_submitted = False
        st.session_state.satisfaction_rating = None
        st.session_state.rating_message = ""
        st.session_state.last_trace = None
        st.session_state.routing_log = []
        st.rerun()

# ── Component C + D: Input and submit ────────────────────
if not st.session_state.conversation_ended:
    user_input = st.chat_input("Type your message here...")
else:
    user_input = None

def process_message(message: str):
    """Runs message through crew and updates session state."""

    if st.session_state.get("conversation_ended"):
        st.session_state.messages.append({"is_divider": True})
        st.session_state.conversation_ended = False
        st.session_state.rating_submitted = False
        st.session_state.satisfaction_rating = None
        st.session_state.rating_message = ""
        st.session_state.last_trace = None
        st.session_state.routing_log = []

    with st.spinner("Processing your message..."):
        result = run_crew(
            message,
            st.session_state.messages,
            st.session_state.customer_name
        )

    st.session_state.messages.append({
        "role": "user",
        "content": message
    })

    response_text = result["response"]
    disclosure = "AI-Simulated Response — Would route to a Human Representative in a live environment"
    response_text = response_text.replace(f"**{disclosure}**", "").strip()
    response_text = response_text.replace(disclosure, "").strip()

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "label": result.get("label")
    })

    st.session_state.last_trace = result
    log_interaction(message, result)

    st.session_state.routing_log.append({
        "Message": message[:40] + "..." if len(message) > 40 else message,
        "Sentiment": result.get("sentiment"),
        "Agent": result.get("agent"),
        "Success": "✅"
    })

    st.rerun()

if user_input:
    process_message(user_input)

# ── Component E: Collapsible engineering panel ────────────
st.divider()

with st.expander("🔧 Engineering Log & Testing Panel"):

    # ── Test Scenarios first ──────────────────────────────
    st.subheader("Test Scenarios")
    st.write("Click a button to send a randomized test banking customer service message:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Test Positive Feedback"):
            process_message(random.choice(POSITIVE_MESSAGES))
        st.caption("Tests: Feedback Handler Agent — positive path")

        if st.button("❌ Test Negative Feedback"):
            process_message(random.choice(NEGATIVE_MESSAGES))
        st.caption("Tests: Feedback Handler Agent — negative path")

    with col2:
        if st.button("🔍 Test Ticket Query"):
            process_message(random.choice(QUERY_MESSAGES))
        st.caption("Tests: Query Handler Agent")

        if st.button("🤝 Test AI-Simulated Human Handoff"):
            process_message(random.choice(ESCALATION_MESSAGES))
        st.caption("Tests: Human-in-the-Loop Agent")

    st.divider()

    # ── Current Interaction Trace ─────────────────────────
    st.subheader("Current Interaction Trace")

    if st.session_state.last_trace:
        trace = st.session_state.last_trace

        st.write(f"**Sentiment:** {trace.get('sentiment', '—')}")
        st.write(f"**Intent:** {trace.get('intent', '—')}")
        st.write(f"**Department:** {trace.get('department', '—')}")
        st.write(f"**Agent Triggered:** {trace.get('agent', '—')}")

        if trace.get("escalation_type"):
            st.warning(f"**Escalation Type:** {trace.get('escalation_type')}")
            st.write(f"**Escalation Trigger:** {trace.get('escalation_trigger')}")

        if trace.get("ticket_created"):
            st.success(f"**Ticket Created:** #{trace.get('ticket_created')}")

        with st.expander("View Classifier Prompt"):
            st.code(str(trace.get("classifier_prompt", "—")), language="text")

        with st.expander("View Classifier Response"):
            st.code(str(trace.get("classifier_response", "—")), language="text")

        with st.expander("View Agent Prompt"):
            st.code(str(trace.get("prompt_sent", "—")), language="text")

        with st.expander("View Agent Response"):
            st.code(str(trace.get("response_returned", "—")), language="text")

    else:
        st.info("No messages processed yet. Send a message or use a test button above.")

    st.divider()

    # ── Ticket Log ────────────────────────────────────────
    st.subheader("Ticket Log")

    tickets = get_all_tickets()
    if tickets:
        st.table(tickets)
        st.caption(f"Total tickets in database: {len(tickets)}")
    else:
        st.info("No tickets in database yet.")

    if st.session_state.routing_log:
        st.write("**Routing Success Log:**")
        st.table(st.session_state.routing_log)
        total = len(st.session_state.routing_log)
        st.write(f"**Routing Success Rate:** {total}/{total} (100%)")

    st.divider()

    # ── QA Evaluation Scores ──────────────────────────────
    st.subheader("QA Evaluation Scores")
    summary = get_evaluation_summary()
    st.write(f"**Empathy:** {summary['avg_empathy']}% | **Clarity:** {summary['avg_clarity']}% | **Routing:** {summary['avg_routing_accuracy']}% | **Overall:** {summary['avg_overall']}%")
    st.caption(f"Routing Success Rate: {summary['routing_success_rate']} | Total Interactions: {summary['total_interactions']}")

    # ── Satisfaction ratings summary ──────────────────────
    log_path = "logs/agent_log.json"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            all_logs = json.load(f)
        ratings = [l["rating"] for l in all_logs if l.get("type") == "satisfaction_rating"]
        if ratings:
            avg_rating = round(sum(ratings) / len(ratings), 1)
            st.write(f"**Customer Satisfaction:** {avg_rating}/5 ⭐ ({len(ratings)} rated conversations)")
            if avg_rating < 3.0:
                st.error(
                    "Low satisfaction detected. Agent prompts flagged for review. "
                    "In a production system this would trigger an automated prompt "
                    "optimization cycle and escalate to the LLMOps team."
                )
            elif avg_rating < 4.0:
                st.warning(
                    "Satisfaction below target threshold. "
                    "Monitor agent responses for quality issues."
                )
            else:
                st.success(
                    "Satisfaction within acceptable range. "
                    "No agent prompt adjustments required."
                )

            # ── Rating history log ────────────────────────
            st.write("**Rating History:**")
            rating_rows = []
            for l in all_logs:
                if l.get("type") == "satisfaction_rating":
                    rating_rows.append({
                        "Rating": "⭐" * l["rating"],
                        "Score": f"{l['rating']}/5",
                        "Comment": l.get("comment", "") or "—",
                        "Messages in session": l.get("total_messages", "—")
                    })
            if rating_rows:
                st.table(rating_rows)