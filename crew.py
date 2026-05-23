# Copyright (c) 2026 Stephanie Wong. All rights reserved. This source code is submitted for academic evaluation purposes only. No license is granted for any other use, reproduction, modification, or distribution without explicit written permission from the copyright holder.
# crew.py
# CrewAI orchestration — wires all agents together
# Agentic AI Banking Capstone Project 2026: Engineered and Designed by Stephanie Wong

import os
import anthropic
from crewai import Agent, Task, Crew, Process
from agents.core.classifier_agent import classify_message
from agents.core.feedback_agent import handle_feedback
from agents.core.query_agent import handle_query
from agents.enhanced.ai_simulated_human_handoff_agent import handle_handoff
from database.db_setup import setup_database

# Ensure database is set up on startup
setup_database()

# ── Initialize Anthropic client ───────────────────────────
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── LLM model string for CrewAI ──────────────────────────
claude_llm = "anthropic/claude-sonnet-4-5"

# ── Self-service intents — no ticket needed ───────────────
SELF_SERVICE_INTENTS = [
    "Payment or Card Declined",
    "Login or Password Help",
    "Balance or Transaction Inquiry",
    "Ticket Status Inquiry",
    "Card Activation",
    "Account Information Update",
    "Transfer Processing Time",
    "Fee or Interest Rate Question",
    "How to Set Up Direct Deposit",
    "How to Dispute a Charge",
    "App or Website Troubleshooting",
    "Product Question",
    "General Feedback",
]

# ── Define CrewAI Agents ──────────────────────────────────
classifier_agent = Agent(
    role="Customer Message Classifier",
    goal="Classify incoming customer messages into the correct category and route to the appropriate agent",
    backstory=(
        "You are an expert banking customer support classifier with years of experience "
        "identifying customer sentiment, intent, and urgency. You ensure every message "
        "reaches the right team quickly and accurately."
    ),
    llm=claude_llm,
    verbose=True,
    allow_delegation=False
)

feedback_agent = Agent(
    role="Customer Feedback Handler",
    goal="Handle positive and negative customer feedback with empathy and professionalism",
    backstory=(
        "You are a compassionate banking support specialist who excels at acknowledging "
        "customer experiences. You celebrate positive feedback warmly and handle complaints "
        "with genuine empathy, always creating support tickets when needed."
    ),
    llm=claude_llm,
    verbose=True,
    allow_delegation=False
)

query_agent = Agent(
    role="Ticket Query Specialist",
    goal="Look up ticket status and provide accurate updates to customers",
    backstory=(
        "You are a meticulous support specialist who ensures customers always know "
        "the status of their support tickets. You provide clear, accurate updates "
        "and help customers understand next steps."
    ),
    llm=claude_llm,
    verbose=True,
    allow_delegation=False
)

handoff_agent = Agent(
    role="AI-Simulated Human Representative",
    goal="Simulate a warm human escalation response for cases requiring human intervention",
    backstory=(
        "You simulate a senior banking customer service representative handling escalated cases. "
        "In a live environment this role would be fulfilled by a real human agent. "
        "You respond with warmth, urgency, and genuine empathy to build customer confidence."
    ),
    llm=claude_llm,
    verbose=True,
    allow_delegation=False
)

# ── Shared response rules ─────────────────────────────────
RESPONSE_RULES = (
    f'Important rules:\n'
    f'- Do not use emojis under any circumstances\n'
    f'- Do not sign off with any internal role names, agent names, or system labels\n'
    f'- Do not end with a formal sign-off or team name\n'
    f'- Do not share incorrect information\n'
    f'- Keep response concise and professional\n'
    f'- Sound like a real bank representative, not a chatbot\n'
)

# ── Format conversation history ───────────────────────────
def format_history(conversation_history: list) -> str:
    """Formats recent conversation history for context injection."""
    if not conversation_history:
        return "No previous messages."
    lines = []
    for msg in conversation_history:
        if msg.get("is_divider") or msg.get("is_greeting"):
            continue
        role = "Customer" if msg["role"] == "user" else "Agent"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines) if lines else "No previous messages."

# ── Self-service handler ──────────────────────────────────
def handle_self_service(message: str, classification: dict, conversation_history: list = None) -> dict:
    """
    Handles Tier 3 self-service messages that don't need a ticket.
    Uses Claude's general banking knowledge with conversation context.
    """
    intent = classification.get("intent", "General")
    history_text = format_history(conversation_history or [])

    prompt = (
        f'You are a knowledgeable banking customer service specialist '
        f'at a major US bank.\n\n'
        f'Recent conversation context:\n{history_text}\n\n'
        f'Current customer message: "{message}"\n'
        f'Intent identified: {intent}\n\n'
        f'Use the conversation context to understand what the customer is referring to. '
        f'Respond helpfully using your banking knowledge. '
        f'Give clear, actionable steps or information relevant to their specific situation.\n\n'
        f'Important rules:\n'
        f'- Do not use emojis under any circumstances\n'
        f'- Do not sign off with any internal role names, agent names, or system labels\n'
        f'- Do not end with a formal sign-off or team name\n'
        f'- Do not share incorrect information — if unsure, advise the customer to '
        f'contact the bank directly via phone or branch\n'
        f'- Keep response concise and professional\n'
        f'- Sound like a real bank representative, not a chatbot\n\n'
        f'Return only the response message, no extra text.'
    )

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.content[0].text.strip()

    return {
        "agent": "Self-Service Handler",
        "response": response_text,
        "label": None,
        "ticket_created": None,
        "prompt_sent": prompt,
        "response_returned": response_text
    }

# ── Main orchestration function ───────────────────────────
def run_crew(message: str, conversation_history: list = None, customer_name: str = None) -> dict:
    """
    Main orchestration function.
    Classifies the message then routes to the correct agent.
    Accepts conversation history for contextual responses.
    """

    # ── Step 1: Classify the message ─────────────────────
    classification = classify_message(message)
    sentiment = classification.get("sentiment")
    intent = classification.get("intent", "")
    tier = classification.get("tier", 3)

    # ── Step 2: Format history for context ───────────────
    history_text = format_history(conversation_history or [])

    # ── Step 3: Route based on sentiment + tier ───────────
    feedback_result = None

    if sentiment == "Escalation Request":
        task = Task(
            description=(
                f'Recent conversation:\n{history_text}\n\n'
                f'You are handling an escalated banking support case.\n'
                f'Current customer message: "{message}"\n'
                f'Escalation reason: {classification.get("escalation_trigger")}\n\n'
                f'Use the conversation context to personalize your response.\n'
                f'Write a warm, empathetic response that:\n'
                f'- Acknowledges the customer personally\n'
                f'- Shows genuine urgency and care\n'
                f'- Assures them a specialist will handle their case\n'
                f'- Gives them confidence their issue will be resolved\n\n'
                f'- Aim for 2-3 sentences. Only go longer if additional detail is genuinely helpful\n'
                f'- Do not promise specific timeframes for human contact\n'
                f'- Do not make commitments the bank cannot guarantee\n'
                + RESPONSE_RULES
            ),
            expected_output="A warm empathetic escalation response",
            agent=handoff_agent
        )

    elif sentiment == "Positive Feedback":
        task = Task(
            description=(
                f'Recent conversation:\n{history_text}\n\n'
                f'You are handling positive feedback from a banking customer.\n'
                f'Current customer message: "{message}"\n\n'
                f'Write a warm, genuine thank-you response in 2-3 sentences that:\n'
                f'- Begin with exactly: "Thank you for your kind words, {customer_name or "Valued Customer"}!"\n'
                f'- Acknowledges what they specifically said\n'
                f'- Expresses genuine appreciation\n'
                f'- Is personable and human\n\n'
                + RESPONSE_RULES
            ),
            expected_output="A warm personalized thank-you message in 2-3 sentences",
            agent=feedback_agent
        )

    elif sentiment == "Negative Feedback" and intent in SELF_SERVICE_INTENTS:
        result = handle_self_service(message, classification, conversation_history)
        result["sentiment"] = sentiment
        result["intent"] = intent
        result["department"] = classification.get("department")
        result["escalation_type"] = None
        result["escalation_trigger"] = None
        result["classifier_prompt"] = classification.get("prompt_sent")
        result["classifier_response"] = classification.get("response_returned")
        result["ticket_created"] = None
        return result

    elif sentiment == "Negative Feedback":
        feedback_result = handle_feedback(message, classification)
        ticket_id = feedback_result.get("ticket_created")

        task = Task(
            description=(
                f'Recent conversation:\n{history_text}\n\n'
                f'You are handling a complaint from a banking customer.\n'
                f'Current customer message: "{message}"\n'
                f'Issue type: {intent}\n'
                f'Support ticket #{ticket_id} has been created for this case.\n\n'
                f'Use the conversation context to acknowledge their full situation.\n'
                f'Write an empathetic response in 2-3 sentences that:\n'
                f'- Acknowledges their specific issue with genuine understanding\n'
                f'- Informs them ticket #{ticket_id} has been created\n'
                f'- Reassures them the team will follow up\n\n'
                + RESPONSE_RULES
            ),
            expected_output=f"An empathetic 2-3 sentence response mentioning ticket #{ticket_id}",
            agent=feedback_agent
        )

    elif sentiment == "Query" and intent == "Ticket Status Inquiry":
        query_result = handle_query(message, classification)
        status_info = query_result.get("response")

        task = Task(
            description=(
                f'Recent conversation:\n{history_text}\n\n'
                f'You are handling a ticket status inquiry from a banking customer.\n'
                f'Current customer message: "{message}"\n'
                f'Database result: {status_info}\n\n'
                f'Relay this ticket status information clearly and professionally '
                f'in 1-2 sentences.\n\n'
                + RESPONSE_RULES
            ),
            expected_output="A clear 1-2 sentence ticket status update",
            agent=query_agent
        )

    else:
        result = handle_self_service(message, classification, conversation_history)
        result["sentiment"] = sentiment
        result["intent"] = intent
        result["department"] = classification.get("department")
        result["escalation_type"] = None
        result["escalation_trigger"] = None
        result["classifier_prompt"] = classification.get("prompt_sent")
        result["classifier_response"] = classification.get("response_returned")
        result["ticket_created"] = None
        return result

    # ── Step 4: Create and run the Crew ──────────────────
    crew = Crew(
        agents=[classifier_agent, feedback_agent, query_agent, handoff_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    crew_result = crew.kickoff()

    # ── Step 5: Clean response ────────────────────────────
    response_text = str(crew_result)
    disclosure = "AI-Simulated Response — Would route to a Human Representative in a live environment"
    response_text = response_text.replace(f"**{disclosure}**", "").strip()
    response_text = response_text.replace(disclosure, "").strip()

    # ── Step 6: Build result dict ─────────────────────────
    result = {
        "agent": task.agent.role,
        "response": response_text,
        "label": disclosure if sentiment == "Escalation Request" else None,
        "sentiment": classification.get("sentiment"),
        "intent": classification.get("intent"),
        "department": classification.get("department"),
        "escalation_type": classification.get("escalation_type"),
        "escalation_trigger": classification.get("escalation_trigger"),
        "ticket_created": feedback_result.get("ticket_created") if feedback_result else None,
        "classifier_prompt": classification.get("prompt_sent"),
        "classifier_response": classification.get("response_returned"),
        "prompt_sent": task.description,
        "response_returned": response_text
    }

    return result