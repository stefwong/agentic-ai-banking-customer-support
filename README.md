# Voillà — Agentic AI Banking Customer Support

**Designed and Engineered by Stephanie Wong**
Agentic AI Banking Capstone Project 2026
Purdue University (Online) via Simplilearn — Applied Generative AI Specialization

---

## Live Demo

[voilla.ai](https://voilla.ai) — No setup required. Click and interact immediately.

**GitHub Repository:** [to be updated after repo is created]

---

## What This Is

Voillà is a multi-agent AI system built for banking customer support workflows. It classifies incoming customer messages, routes them to the appropriate AI agent, generates contextually aware responses, tracks support tickets, and simulates human escalation when needed.

---

## Before You Begin

Open [voilla.ai](https://voilla.ai) in a desktop browser.
When prompted, enter your first name and click **Start Chat**.
The system greets you by name and the chat opens.
Click **Engineering Log & Testing Panel** at the bottom to expand it before running tests.

---

## How to Test

Follow the numbered tests in order. After each test open the Engineering Log to verify the correct agent was triggered.

**Test 1 — Classifier Agent**
Type: `Thanks for sorting out my net banking login issue.`
Verify: Sentiment = Positive Feedback, Agent Triggered = Customer Feedback Handler

**Test 2 — Feedback Handler: Positive Path**
Same message. Verify response begins with: Thank you for your kind words, [your name]!

**Test 3 — Feedback Handler: Negative Path**
Type: `My debit card replacement still hasn't arrived.`
Verify: 6-digit ticket number in response, new row in Ticket Log with Status: Unresolved

**Test 4 — Query Handler Agent**
Type: `Could you check the status of ticket 650932?`
Verify: Response returns ticket status from database

**Test 5 — Sample Use Case Flow**
Open Engineering Log → Test Scenarios → click all 4 test buttons.
Verify: Routing Success Rate shows 100%

**Test 6 — Model Evaluation**
Send 3 to 4 messages. Open Engineering Log → QA Evaluation Scores.
Verify: Empathy %, Clarity %, Routing %, Overall % all showing

**Test 7 — Streamlit UI**
Verify chat input, Engineering Log sections, Ticket Log, and test buttons all working.

**Test 8 — Logs and Debugging**
Expand all 4 prompt trace expanders in Current Interaction Trace after any message.

**Test 9 — User Feedback Loop (Optional)**
Click End Conversation → submit a rating → verify Rating History updates in Engineering Log.

---

## Tech Stack

| Tool | Role |
|---|---|
| Python | Backend language |
| CrewAI | Multi-agent orchestration |
| LangChain | LLM utility layer |
| Claude (Anthropic) | LLM powering all agent responses |
| SQLite | Support ticket database |
| Streamlit | UI framework |
| Replit | Development and deployment environment |

---

## Local Setup

See [REQUIREMENTS.md](REQUIREMENTS.md) for full local setup and shell testing instructions.

---

## Author

**Stephanie Wong** — AI UX Design Engineer
Agentic AI Banking Capstone Project 2026
Purdue University (Online) via Simplilearn — Applied Generative AI Specialization