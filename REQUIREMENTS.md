## Copyright

Copyright (c) 2026 Stephanie Wong. All rights reserved.
This project is submitted for academic evaluation purposes only.
No license is granted for any other use, reproduction, modification,
or distribution without explicit written permission from the copyright holder.

---

# REQUIREMENTS.md
# Voillà — Agentic AI Banking Customer Support
# Local Setup & Testing Instructions

---

## Prerequisites

- Python 3.11+
- An Anthropic API key (get one at https://console.anthropic.com)

---

## Local Setup

**1. Clone the repository:**

```bash
git clone https://github.com/[YOUR-USERNAME]/agentic-ai-banking-customer-support.git
cd agentic-ai-banking-customer-support
```

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Set your Anthropic API key:**

```bash
export ANTHROPIC_API_KEY=your_key_here
```

**4. Run the app:**

```bash
streamlit run app.py
```

**5. Open in browser:**

```
http://localhost:8501
```

---

## Testing Each Requirement Locally

### Requirement 1 — Classifier Agent

Type in chat: `Thanks for sorting out my net banking login issue.`

Open Engineering Log and expand Current Interaction Trace. Verify:
- Sentiment: Positive Feedback
- Agent Triggered: Customer Feedback Handler

---

### Requirement 2 — Feedback Handler: Positive Path

Type in chat: `Thanks for sorting out my net banking login issue.`

Verify the response begins with: `Thank you for your kind words, [name]!`

No ticket number should appear in the response.

---

### Requirement 2 — Feedback Handler: Negative Path

Type in chat: `My debit card replacement still hasn't arrived.`

Verify the response contains a 6-digit ticket number.

Verify ticket was created in the database by running in shell:

```bash
python -c "from database.db_setup import get_all_tickets; print(get_all_tickets())"
```

---

### Requirement 3 — Query Handler Agent

Type in chat: `Could you check the status of ticket 650932?`

Verify the response returns the ticket status from the database.

Open Engineering Log and verify:
- Sentiment: Query
- Intent: Ticket Status Inquiry
- Agent Triggered: Ticket Query Specialist

---

### Requirement 4 — Sample Use Case Flow

Open Engineering Log and expand Test Scenarios. Click each of the 4 test buttons:

- Test Positive Feedback
- Test Negative Feedback
- Test Ticket Query
- Test AI-Simulated Human Handoff

Scroll to Routing Success Log and verify Routing Success Rate shows 100%.

---

### Requirement 7 — Model Evaluation

Send 3 to 4 messages of different types. Open Engineering Log and scroll to QA Evaluation Scores.

Verify all metrics are showing: Empathy %, Clarity %, Routing %, Overall %

---

### Requirement 8 — Streamlit UI

Verify the following are all present and working:
- Chat input accepts messages and displays responses
- Engineering Log shows Test Scenarios, Current Interaction Trace, Ticket Log, Routing Success Log, QA Evaluation Scores
- Ticket Log populates after negative feedback messages
- All 4 test buttons work with agent role captions below each

---

### Requirement 9 — Logs and Debugging

After any message, open Engineering Log and expand Current Interaction Trace. Click each expander:

- View Classifier Prompt — verify full prompt text showing
- View Classifier Response — verify JSON classification output showing
- View Agent Prompt — verify full task description showing
- View Agent Response — verify raw LLM response showing

Verify Ticket Log shows all tickets with ID, Status, Intent, Department, Created timestamp, and Agent.

---

### Requirement 9 — User Feedback Loop (Optional)

Click End Conversation after any exchange. Submit a rating and click Submit Rating.

Open Engineering Log and scroll to QA Evaluation Scores then Rating History.

Verify:
- Rating appears in Rating History table with Score, Status, and Comment
- 1 to 2 stars triggers red LOW alert
- 3 stars triggers yellow BELOW TARGET warning
- 4 to 5 stars shows green ACCEPTABLE
- Overall Satisfaction average updates correctly

---

## Reset Database to Clean State

To reset all tickets and logs to the original seed state:

```bash
rm database/support_tickets.db
rm logs/agent_log.json
streamlit run app.py
```

The app will automatically reseed the database with 4 clean seed tickets on startup.

---

## File Structure

```
agentic-ai-banking-customer-support/
├── agents/
│   ├── core/
│   │   ├── classifier_agent.py        — Classifies all messages
│   │   ├── feedback_agent.py          — Handles positive and negative feedback
│   │   └── query_agent.py             — Handles ticket status queries
│   └── enhanced/
│       └── ai_simulated_human_handoff_agent.py — Human escalation agent
├── assets/
│   └── voilla_logo.png
├── database/
│   └── db_setup.py                    — SQLite setup and seed data
├── logs/
│   └── agent_log.json                 — Interaction and rating logs
├── app.py                             — Streamlit UI
├── crew.py                            — CrewAI orchestration
├── evaluation.py                      — QA scoring and logging
├── requirements.txt
├── README.md
└── REQUIREMENTS.md
```

---

## Alternative Live Website

[agentic-ai-banking-customer-support.replit.app](https://agentic-ai-banking-customer-support.replit.app) — No setup required. Click and interact immediately.

**Custom Domain (SSL propagating):** [voilla.ai](https://voilla.ai)

## Author

**Stephanie Wong** — AI UX Design Engineer

Agentic AI Banking Capstone Project 2026
Submitted to: Purdue University (Online) via Simplilearn — Applied Generative AI Specialization
