# agents/core/feedback_agent.py
# Feedback Handler Agent — handles positive and negative feedback
# Agentic AI Banking Customer Support
# Purdue University (Online) via Simplilearn

import os
import random
import anthropic
from database.db_setup import insert_ticket

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def generate_ticket_number() -> str:
    """Generates a unique 6-digit ticket number."""
    return str(random.randint(100000, 999999))

def handle_positive_feedback(message: str, intent: str) -> dict:
    """
    Generates a warm personalized thank-you response.
    """
    prompt = (
        f'You are a warm and professional banking customer support agent.\n\n'
        f'A customer has sent positive feedback: "{message}"\n\n'
        f'Write a brief, genuine thank-you response. '
        f'Keep it to 1-2 sentences. Be warm but professional. '
        f'Do not use generic phrases like "I understand your concern". '
        f'Acknowledge what they said specifically.\n\n'
        f'Return only the response message, no extra text.'
    )

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.content[0].text.strip()

    return {
        "agent": "FeedbackHandlerAgent",
        "path": "positive",
        "response": response_text,
        "ticket_created": None,
        "prompt_sent": prompt,
        "response_returned": response_text
    }

def handle_negative_feedback(message: str, intent: str, department: str) -> dict:
    """
    Creates a ticket and generates an empathetic response.
    """
    # Generate unique ticket number
    ticket_id = generate_ticket_number()

    # Insert ticket into database
    insert_ticket(
        ticket_id=ticket_id,
        customer_message=message,
        sentiment="Negative Feedback",
        intent=intent,
        department=department
    )

    # Generate empathetic response
    prompt = (
        f'You are an empathetic banking customer support agent.\n\n'
        f'A customer has reported an issue: "{message}"\n\n'
        f'Their concern has been categorized as: {intent}\n\n'
        f'A support ticket #{ticket_id} has been created for them.\n\n'
        f'Write a brief empathetic response acknowledging their issue and '
        f'informing them their ticket #{ticket_id} has been created. '
        f'Keep it to 2 sentences maximum. Be genuine and professional.\n\n'
        f'Return only the response message, no extra text.'
    )

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.content[0].text.strip()

    return {
        "agent": "FeedbackHandlerAgent",
        "path": "negative",
        "response": response_text,
        "ticket_created": ticket_id,
        "prompt_sent": prompt,
        "response_returned": response_text
    }

def handle_feedback(message: str, classification: dict) -> dict:
    """
    Main entry point. Routes to positive or negative path.
    """
    sentiment = classification.get("sentiment")
    intent = classification.get("intent", "Complaint")
    department = classification.get("department", "Customer Relations")

    if sentiment == "Positive Feedback":
        return handle_positive_feedback(message, intent)
    else:
        return handle_negative_feedback(message, intent, department)


if __name__ == "__main__":
    # Test positive path
    print("\n" + "="*50)
    print("TEST: Positive Feedback")
    result = handle_positive_feedback(
        "Thanks for sorting out my net banking login issue.",
        "General Feedback"
    )
    print(f"Response: {result['response']}")
    print(f"Ticket Created: {result['ticket_created']}")

    # Test negative path
    print("\n" + "="*50)
    print("TEST: Negative Feedback")
    result = handle_negative_feedback(
        "My debit card replacement still hasn't arrived.",
        "Complaint",
        "Customer Relations"
    )
    print(f"Response: {result['response']}")
    print(f"Ticket Created: {result['ticket_created']}")