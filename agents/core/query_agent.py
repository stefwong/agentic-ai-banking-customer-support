# agents/core/query_agent.py
# Query Handler Agent — looks up ticket status from database
# Agentic AI Banking Customer Support
# Purdue University (Online) via Simplilearn

import os
import re
import anthropic
from database.db_setup import get_ticket_status

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def extract_ticket_number(message: str) -> str | None:
    """
    Extracts a 6-digit ticket number from a customer message.
    Returns the ticket number as a string or None if not found.
    """
    # Look for 6-digit number in message
    match = re.search(r'\b(\d{6})\b', message)
    if match:
        return match.group(1)
    return None

def handle_query(message: str, classification: dict) -> dict:
    """
    Main entry point. Extracts ticket number and returns status.
    """
    # ── Step 1: Extract ticket number ────────────────────
    ticket_id = extract_ticket_number(message)

    if not ticket_id:
        # Ask Claude to extract the ticket number if regex didn't find it
        prompt = (
            f'Extract the ticket number from this message: "{message}"\n\n'
            f'Return ONLY the ticket number as a plain number with no extra text. '
            f'If there is no ticket number, return "none".'
        )
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}]
        )
        extracted = response.content[0].text.strip().lower()
        if extracted != "none" and extracted.isdigit():
            ticket_id = extracted

    # ── Step 2: Handle no ticket number found ────────────
    if not ticket_id:
        response_text = "I'd be happy to check on your ticket status. Could you please provide your ticket number so I can look that up for you?"
        return {
            "agent": "QueryHandlerAgent",
            "response": response_text,
            "ticket_id": None,
            "ticket_status": None,
            "prompt_sent": message,
            "response_returned": response_text
        }

    # ── Step 3: Look up ticket in database ───────────────
    status = get_ticket_status(ticket_id)

    # ── Step 4: Handle ticket not found ──────────────────
    if not status:
        response_text = f"I wasn't able to find a ticket with number #{ticket_id} in our system. Please double-check the ticket number and try again."
        return {
            "agent": "QueryHandlerAgent",
            "response": response_text,
            "ticket_id": ticket_id,
            "ticket_status": None,
            "prompt_sent": message,
            "response_returned": response_text
        }

    # ── Step 5: Return status in PDF format ──────────────
    response_text = f"Your ticket #{ticket_id} is currently marked as: {status}."

    return {
        "agent": "QueryHandlerAgent",
        "response": response_text,
        "ticket_id": ticket_id,
        "ticket_status": status,
        "prompt_sent": message,
        "response_returned": response_text
    }


if __name__ == "__main__":
    # Test with PDF example
    print("\n" + "="*50)
    print("TEST: Query with valid ticket number")
    result = handle_query(
        "Could you check the status of ticket 650932?",
        {"sentiment": "Query", "intent": "Ticket Inquiry", "department": "Support Team"}
    )
    print(f"Response: {result['response']}")
    print(f"Ticket ID: {result['ticket_id']}")
    print(f"Status: {result['ticket_status']}")

    # Test with no ticket number
    print("\n" + "="*50)
    print("TEST: Query with no ticket number")
    result = handle_query(
        "Can you check on my support request?",
        {"sentiment": "Query", "intent": "Ticket Inquiry", "department": "Support Team"}
    )
    print(f"Response: {result['response']}")

    # Test with invalid ticket number
    print("\n" + "="*50)
    print("TEST: Query with invalid ticket number")
    result = handle_query(
        "What is the status of ticket 999999?",
        {"sentiment": "Query", "intent": "Ticket Inquiry", "department": "Support Team"}
    )
    print(f"Response: {result['response']}")