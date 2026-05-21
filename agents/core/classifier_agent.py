# agents/core/classifier_agent.py
# Classifier Agent — routes all incoming customer messages
# Agentic AI Banking Capstone Project 2026: Engineered and Designed by Stephanie Wong

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

# ── Tier definitions ──────────────────────────────────────
TIER_1_INTENTS = [
    "Fraud Claim",
    "Account Compromised",
    "Legal or Regulatory Threat",
]

TIER_2_INTENTS = [
    "Card Not Arrived",
    "Unresolved Transfer Issue",
    "Unresolved Account Access Issue",
    "Disputed Charge",
    "Loan or Mortgage Issue",
    "Persistent Service Failure",
]

TIER_3_INTENTS = [
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

def get_tier(intent: str) -> int:
    if intent in TIER_1_INTENTS:
        return 1
    elif intent in TIER_2_INTENTS:
        return 2
    elif intent in TIER_3_INTENTS:
        return 3
    else:
        return 3

def check_explicit_escalation(message: str) -> bool:
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
        f'Classify using this banking intent taxonomy:\n\n'
        f'TIER 1 — Always escalate to human (fraud, security, legal):\n'
        f'- Fraud Claim: unauthorized transaction, someone used account without permission\n'
        f'- Account Compromised: suspicious login, someone changed account info, hacked\n'
        f'- Legal or Regulatory Threat: mentions lawyer, CFPB, BBB, lawsuit, legal action\n\n'
        f'TIER 2 — Create support ticket, needs follow up:\n'
        f'- Card Not Arrived: card ordered but not received after expected delivery window\n'
        f'- Unresolved Transfer Issue: transfer pending more than 3 business days\n'
        f'- Unresolved Account Access Issue: cannot access account after trying self-service steps\n'
        f'- Disputed Charge: specific charge customer wants to formally dispute\n'
        f'- Loan or Mortgage Issue: payment not applied, rate concern, loan dispute\n'
        f'- Persistent Service Failure: issue that has already been reported and not resolved\n\n'
        f'TIER 3 — Self-service, answer directly, no ticket needed:\n'
        f'- Payment or Card Declined: payment or card was declined — explain common reasons and steps\n'
        f'- Login or Password Help: forgot password, locked out — provide reset instructions\n'
        f'- Balance or Transaction Inquiry: balance check, recent transactions, statement\n'
        f'- Ticket Status Inquiry: check status of existing support ticket\n'
        f'- Card Activation: how to activate new card\n'
        f'- Account Information Update: change address, phone, email\n'
        f'- Transfer Processing Time: transfer not showing yet — explain processing times\n'
        f'- Fee or Interest Rate Question: explain fee structure or rates\n'
        f'- How to Set Up Direct Deposit: step by step instructions\n'
        f'- How to Dispute a Charge: explain the dispute process and steps\n'
        f'- App or Website Troubleshooting: app not working, website error — troubleshooting steps\n'
        f'- Product Question: how does X work, account types, features\n'
        f'- General Feedback: positive experience, compliment, suggestion\n\n'
        f'Department mapping:\n'
        f'- Fraud Claim → Fraud Investigation Team\n'
        f'- Account Compromised → Security Team\n'
        f'- Legal or Regulatory Threat → Legal and Compliance\n'
        f'- Card Not Arrived, Unresolved Transfer Issue → Operations Team\n'
        f'- Disputed Charge → Chargeback Team\n'
        f'- Loan or Mortgage Issue → Lending Team\n'
        f'- Persistent Service Failure, Unresolved Account Access Issue → Customer Relations\n'
        f'- Payment or Card Declined, App or Website Troubleshooting → Self-Service Support\n'
        f'- Login or Password Help, Card Activation, Account Information Update → Self-Service Support\n'
        f'- Balance or Transaction Inquiry, Ticket Status Inquiry, Transfer Processing Time → General Support\n'
        f'- Fee or Interest Rate Question, How to Set Up Direct Deposit, How to Dispute a Charge → General Support\n'
        f'- Product Question → Product Support\n'
        f'- General Feedback → Customer Experience Team\n\n'
        f'Important distinctions:\n'
        f'- "my payment was declined" or "card declined" = Payment or Card Declined (Tier 3) NOT a complaint\n'
        f'- "my card hasnt arrived" after reasonable time = Card Not Arrived (Tier 2)\n'
        f'- "transfer not showing" same day or next day = Transfer Processing Time (Tier 3)\n'
        f'- "transfer still pending after 3 days" = Unresolved Transfer Issue (Tier 2)\n'
        f'- "forgot password" or "locked out" = Login or Password Help (Tier 3) NOT Account Compromised\n'
        f'- Account Compromised = someone ELSE accessed the account\n\n'
        f'If message does not clearly fit, use banking knowledge to pick closest match.\n\n'
        f'Return ONLY valid JSON, no markdown, no explanation:\n'
        f'{{"intent": "exact intent name from taxonomy", "department": "department name", '
        f'"sentiment": "Positive Feedback or Negative Feedback or Query"}}\n\n'
        f'Sentiment rules:\n'
        f'- Gratitude, satisfaction → Positive Feedback\n'
        f'- Problem, complaint, issue → Negative Feedback\n'
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
        "My payment was declined.",
        "I forgot my password.",
        "There is an unauthorized charge on my account.",
        "I am going to contact my lawyer if this is not resolved.",
        "My transfer has been pending for 4 days.",
        "My transfer isn't showing yet but I just sent it.",
        "How do I set up direct deposit?",
        "The app keeps crashing.",
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