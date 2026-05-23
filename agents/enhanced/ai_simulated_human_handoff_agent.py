# Copyright (c) 2026 Stephanie Wong. All rights reserved. This source code is submitted for academic evaluation purposes only. No license is granted for any other use, reproduction, modification, or distribution without explicit written permission from the copyright holder.
# agents/enhanced/ai_simulated_human_handoff_agent.py
# AI-Simulated Human Handoff Agent
# Simulates escalation to a human representative
# In a live environment this would route to a real human agent
# Agentic AI Banking Customer Support
# Agentic AI Banking Capstone Project 2026: Engineered and Designed by Stephanie Wong 

import os
import anthropic

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── Disclosure label ──────────────────────────────────────
DISCLOSURE_LABEL = "AI-Simulated Response — Would route to a Human Representative in a live environment"

def handle_handoff(message: str, classification: dict) -> dict:
    """
    Main entry point for AI-Simulated Human Handoff.
    Generates a warm, first-person response simulating a human representative.
    """
    escalation_type = classification.get("escalation_type", "Customer Requested")
    escalation_trigger = classification.get("escalation_trigger", "Customer requested human agent")
    intent = classification.get("intent", "Human Agent Request")

    # ── Build context-aware prompt ────────────────────────
    prompt = (
        f'You are simulating a warm, senior banking customer service representative '
        f'who has just received an escalated case.\n\n'
        f'Customer message: "{message}"\n\n'
        f'Escalation reason: {escalation_trigger}\n\n'
        f'Write a brief, warm, first-person response that:\n'
        f'- Acknowledges the customer personally\n'
        f'- Shows genuine empathy and urgency\n'
        f'- Explains that a specialist will handle their case\n'
        f'- Gives them confidence their issue will be resolved\n\n'
        f'Keep it to 2-3 sentences. Sound human and genuine, not robotic.\n\n'
        f'Return only the response message, no extra text.'
    )

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.content[0].text.strip()

    return {
        "agent": "AISimulatedHumanHandoffAgent",
        "response": response_text,
        "label": DISCLOSURE_LABEL,
        "escalation_type": escalation_type,
        "escalation_trigger": escalation_trigger,
        "ticket_created": None,
        "prompt_sent": prompt,
        "response_returned": response_text
    }


if __name__ == "__main__":
    # Test explicit escalation
    print("\n" + "="*50)
    print("TEST: Explicit — Customer Requested")
    result = handle_handoff(
        "I need to speak to a real person about my account.",
        {
            "escalation_type": "Customer Requested",
            "escalation_trigger": "Customer explicitly requested human agent",
            "intent": "Human Agent Request"
        }
    )
    print(f"Label: {result['label']}")
    print(f"Response: {result['response']}")
    print(f"Escalation Type: {result['escalation_type']}")

    # Test auto escalation — fraud
    print("\n" + "="*50)
    print("TEST: Auto-Detected — Fraud Report")
    result = handle_handoff(
        "There is an unauthorized charge on my account I did not make.",
        {
            "escalation_type": "Auto-Detected",
            "escalation_trigger": "Auto-escalation triggered: Fraud Report detected",
            "intent": "Fraud Report"
        }
    )
    print(f"Label: {result['label']}")
    print(f"Response: {result['response']}")
    print(f"Escalation Type: {result['escalation_type']}")

    # Test auto escalation — legal threat
    print("\n" + "="*50)
    print("TEST: Auto-Detected — Legal Threat")
    result = handle_handoff(
        "I am going to contact my lawyer if this is not resolved today.",
        {
            "escalation_type": "Auto-Detected",
            "escalation_trigger": "Auto-escalation triggered: Legal Threat detected",
            "intent": "Legal Threat"
        }
    )
    print(f"Label: {result['label']}")
    print(f"Response: {result['response']}")
    print(f"Escalation Type: {result['escalation_type']}")