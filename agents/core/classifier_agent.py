# agents/core/classifier_agent.py
# Classifier Agent — routes all incoming customer messages
# Uses banking intent taxonomy with tier-based routing
# Agentic AI Banking Customer Support
# Purdue University (Online) via Simplilearn

import os
import json
import anthropic

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── Explicit escalation phrases ───────────────────────────
ESCALATION_PHRASES = [
    "speak to a human",
    "talk to a human",
    "real person",
    "human agent",
    "speak to someone",
    "talk to someone",
    "connect me to",
    "transfer me",
    "escalate",
    "manager",
    "supervisor",
    "representative",
]

# ── Tier definitions for routing ──────────────────────────
TIER_1_INTENTS = [
    "Fraud Claim",
    "Account Compromised",
    "Legal or Regulatory Threat",
]

TIER_2_INTENTS = [
    "Card Dispute",
    "Card Issue",
    "Transfer Issue",
    "Loan or Mortgage Issue",
    "Fee Complaint",
    "Service Complaint",
]

TIER_3_INTENTS = [
    "Login or Password Help",
    "Balance or Transaction Inquiry",
    "Ticket Status Inquiry",
    "Card Activation",
    "Account Information Update",
    "Product Question",
    "General Feedback",
]

def get_tier(intent: str) -> int:
    """Returns the tier number for a given intent."""
    if intent in TIER_1_INTENTS:
        return 1
    elif intent in TIER_2_INTENTS:
        return 2
    elif intent in TIER_3_INTENTS:
        return 3
    else:
        return 3  # Default to Tier 3 for unknown intents

def check_explicit_escalation(message: str) -> bool:
    """Check if customer is explicitly requesting a human."""
    message_lower = message.lower()
    return any(phrase in message_lower for phrase in ESCALATION_PHRASES)

def classify_message(message: str) -> dict:
    """
    Classifies a customer message using banking intent taxonomy.
    Returns: sentiment, intent, department, tier, escalation info
    """

    # ── Step 1: Check for explicit escalation first ───────
    if check_explicit_escalation(message):
        return {
            "sentiment": "Escalation Request",
            "intent": "Human Agent Request",
            "department": "Customer Relations",
            "tier": 1,
            "escalation_type": "Customer Requested",
            "escalation_trigger": "Customer explicitly requested human agent",
            "prompt_sent": f"Escalation phrase detected in: '{message}'",
            "response_returned": "Routing to AI-Simulated Human Handoff Agent"
        }

    # ── Step 2: Use Claude to classify ───────────────────
    prompt = (
        f'You are an expert banking customer support classifier at a major US bank.\n\n'
        f'Analyze this customer message: "{message}"\n\n'
        f'Classify it using this exact banking intent taxonomy:\n\n'
        f'TIER 1 — Always escalate to human (fraud, security, legal):\n'
        f'- Fraud Claim: unauthorized transaction, someone used my card/account without permission\n'
        f'- Account Compromised: suspicious login, someone changed account info, hacked\n'
        f'- Legal or Regulatory Threat: mentions lawyer, CFPB, BBB, lawsuit, legal action\n\n'
        f'TIER 2 — AI handles, creates support ticket:\n'
        f'- Card Dispute: charge I want to dispute, incorrect charge, want money back\n'
        f'- Card Issue: card not arrived, card declined, card blocked, card damaged\n'
        f'- Transfer Issue: pending transfer, failed transfer, wrong amount sent, wire issue\n'
        f'- Loan or Mortgage Issue: payment not applied, rate concern, loan question\n'
        f'- Fee Complaint: overdraft fee, unexpected charge, fee waiver request\n'
        f'- Service Complaint: app not working, website error, general dissatisfaction\n\n'
        f'TIER 3 — AI handles directly, no ticket needed:\n'
        f'- Login or Password Help: forgot password, locked out, cant access account\n'
        f'- Balance or Transaction Inquiry: balance check, recent transactions, statement\n'
        f'- Ticket Status Inquiry: check status of existing support ticket\n'
        f'- Card Activation: activate new card, new card setup\n'
        f'- Account Information Update: change address, phone, email, preferences\n'
        f'- Product Question: how does X work, rates, fees, account types, features\n'
        f'- General Feedback: positive experience, compliment, suggestion\n\n'
        f'Department mapping:\n'
        f'- Tier 1 Fraud Claim → Fraud Investigation Team\n'
        f'- Tier 1 Account Compromised → Security Team\n'
        f'- Tier 1 Legal or Regulatory Threat → Legal and Compliance\n'
        f'- Card Dispute → Chargeback Team\n'
        f'- Card Issue, Transfer Issue → Operations Team\n'
        f'- Loan or Mortgage Issue → Lending Team\n'
        f'- Fee Complaint, Service Complaint → Customer Relations\n'
        f'- Login or Password Help, Card Activation, Account Information Update → Self-Service Support\n'
        f'- Balance or Transaction Inquiry, Ticket Status Inquiry → General Support\n'
        f'- Product Question → Product Support\n'
        f'- General Feedback → Customer Experience Team\n\n'
        f'If the message does not clearly fit any category, use your general banking customer '
        f'service knowledge to pick the closest match and classify accordingly.\n\n'
        f'Return ONLY a valid JSON object with no markdown, no explanation:\n'
        f'{{"intent": "exact intent name from taxonomy", "department": "department name", "sentiment": "Positive Feedback or Negative Feedback or Query"}}\n\n'
        f'Sentiment rules:\n'
        f'- Gratitude, satisfaction, compliment → Positive Feedback\n'
        f'- Problem, complaint, issue, frustration → Negative Feedback\n'
        f'- Question, inquiry, status check → Query'
    )

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.content[0].text.strip()

    # ── Step 3: Parse response ────────────────────────────
    try:
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
    except json.JSONDecodeError:
        # Fallback — let Claude handle it as general banking query
        result = {
            "sentiment": "Query",
            "intent": "Product Question",
            "department": "General Support"
        }

    # ── Step 4: Determine tier ────────────────────────────
    intent = result.get("intent", "Product Question")
    tier = get_tier(intent)
    result["tier"] = tier

    # ── Step 5: Check for Tier 1 auto-escalation ─────────
    if tier == 1:
        result["sentiment"] = "Escalation Request"
        result["escalation_type"] = "Auto-Detected"
        result["escalation_trigger"] = f"Auto-escalation triggered: {intent} detected"
    else:
        result["escalation_type"] = None
        result["escalation_trigger"] = None

    # ── Step 6: Add trace info ────────────────────────────
    result["prompt_sent"] = prompt
    result["response_returned"] = response_text

    return result


if __name__ == "__main__":
    test_messages = [
        "Thanks for sorting out my net banking login issue.",
        "My debit card replacement still hasn't arrived.",
        "Could you check the status of ticket 650932?",
        "I need to speak to a real person about my account.",
        "Hi I forgot my password.",
        "There is an unauthorized charge on my account.",
        "I am going to contact my lawyer if this is not resolved.",
        "How do I activate my new debit card?",
        "What are your current savings account interest rates?",
    ]

    for msg in test_messages:
        print(f"\n{'='*50}")
        print(f"Input: {msg}")
        result = classify_message(msg)
        print(f"Sentiment: {result['sentiment']}")
        print(f"Intent: {result['intent']}")
        print(f"Department: {result['department']}")
        print(f"Tier: {result['tier']}")
        if result.get('escalation_type'):
            print(f"Escalation: {result['escalation_type']}")