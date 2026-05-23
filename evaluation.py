# Copyright (c) 2026 Stephanie Wong. All rights reserved. This source code is submitted for academic evaluation purposes only. No license is granted for any other use, reproduction, modification, or distribution without explicit written permission from the copyright holder.
# evaluation.py
# LLMOps Evaluation — QA scoring and logging
# Agentic AI Banking Customer Support
# Agentic AI Banking Capstone Project 2026: Engineered and Designed by Stephanie Wong 

import os
import json
from datetime import datetime

LOG_FILE = "logs/agent_log.json"

def score_response(sentiment: str, response: str) -> dict:
    """
    Simple QA scoring for agent responses.
    Evaluates empathy, clarity and routing accuracy.
    """
    scores = {}

    # ── Empathy score ─────────────────────────────────────
    empathy_keywords = [
        "understand", "sorry", "apologize", "frustrating",
        "concern", "help", "support", "glad", "happy", "welcome"
    ]
    empathy_count = sum(1 for word in empathy_keywords if word in response.lower())
    scores["empathy"] = min(round((empathy_count / 3) * 100), 100)

    # ── Clarity score ─────────────────────────────────────
    word_count = len(response.split())
    if 10 <= word_count <= 80:
        scores["clarity"] = 100
    elif word_count < 10:
        scores["clarity"] = 50
    else:
        scores["clarity"] = 75

    # ── Routing accuracy ──────────────────────────────────
    routing_correct = sentiment in [
        "Positive Feedback",
        "Negative Feedback",
        "Query",
        "Escalation Request"
    ]
    scores["routing_accuracy"] = 100 if routing_correct else 0

    # ── Overall score ─────────────────────────────────────
    scores["overall"] = round(
        (scores["empathy"] + scores["clarity"] + scores["routing_accuracy"]) / 3
    )

    return scores

def log_interaction(message: str, result: dict) -> None:
    """
    Logs each interaction to logs/agent_log.json
    """
    # Load existing logs
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    # Score the response
    scores = score_response(
        result.get("sentiment", ""),
        result.get("response", "")
    )

    # Build log entry
    entry = {
        "type": "interaction",
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "sentiment": result.get("sentiment"),
        "intent": result.get("intent"),
        "department": result.get("department"),
        "agent": result.get("agent"),
        "ticket_created": result.get("ticket_created"),
        "escalation_type": result.get("escalation_type"),
        "response": result.get("response"),
        "scores": scores
    }

    logs.append(entry)

    # Write back to file
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def get_evaluation_summary() -> dict:
    """
    Returns summary stats from all logged interactions.
    Excludes satisfaction rating entries.
    """
    if not os.path.exists(LOG_FILE):
        return {
            "total_interactions": 0,
            "avg_empathy": 0,
            "avg_clarity": 0,
            "avg_routing_accuracy": 0,
            "avg_overall": 0,
            "routing_success_rate": "0/0"
        }

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    # Filter to interaction logs only — exclude satisfaction ratings
    interaction_logs = [l for l in logs if l.get("type") == "interaction"]
    total = len(interaction_logs)

    if total == 0:
        return {
            "total_interactions": 0,
            "avg_empathy": 0,
            "avg_clarity": 0,
            "avg_routing_accuracy": 0,
            "avg_overall": 0,
            "routing_success_rate": "0/0"
        }

    avg_empathy = round(sum(l["scores"]["empathy"] for l in interaction_logs) / total)
    avg_clarity = round(sum(l["scores"]["clarity"] for l in interaction_logs) / total)
    avg_routing = round(sum(l["scores"]["routing_accuracy"] for l in interaction_logs) / total)
    avg_overall = round(sum(l["scores"]["overall"] for l in interaction_logs) / total)
    correct_routes = sum(1 for l in interaction_logs if l["scores"]["routing_accuracy"] == 100)

    return {
        "total_interactions": total,
        "avg_empathy": avg_empathy,
        "avg_clarity": avg_clarity,
        "avg_routing_accuracy": avg_routing,
        "avg_overall": avg_overall,
        "routing_success_rate": f"{correct_routes}/{total}"
    }