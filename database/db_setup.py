# database/db_setup.py
# Creates and seeds the SQLite support_tickets database
# Agentic AI Banking Customer Support
# Agentic AI Banking Capstone Project 2026: Engineered and Designed by Stephanie Wong 

import sqlite3
from datetime import datetime

DB_PATH = "database/support_tickets.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def setup_database():
    """Creates the support_tickets table and seeds with sample data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id TEXT PRIMARY KEY,
            customer_message TEXT,
            status TEXT,
            sentiment TEXT,
            intent TEXT,
            department TEXT,
            created_at TIMESTAMP,
            agent_handled TEXT
        )
    """)

    # Seed with sample tickets
    seed_tickets = [
        ("650932", "My net banking login wasn't working.", "Resolved", 
         "Negative Feedback", "Complaint", "Customer Relations", 
         datetime.now(), "FeedbackHandlerAgent"),

        ("784521", "My debit card replacement hasn't arrived.", "Unresolved", 
         "Negative Feedback", "Complaint", "Customer Relations", 
         datetime.now(), "FeedbackHandlerAgent"),

        ("392841", "Incorrect charge on my statement.", "In Progress", 
         "Negative Feedback", "Complaint", "Chargeback Team", 
         datetime.now(), "FeedbackHandlerAgent"),

        ("517293", "Unauthorized transaction on my account.", "Escalated", 
         "Negative Feedback", "Fraud Report", "Fraud Investigation Team", 
         datetime.now(), "AISimulatedHumanHandoffAgent"),
    ]

    # Only insert if tickets don't already exist
    for ticket in seed_tickets:
        cursor.execute("""
            INSERT OR IGNORE INTO support_tickets 
            (ticket_id, customer_message, status, sentiment, intent, 
             department, created_at, agent_handled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ticket)

    conn.commit()
    conn.close()
    print("✅ Database setup complete.")

def get_ticket_status(ticket_id):
    """Returns the status of a ticket by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM support_tickets WHERE ticket_id = ?", 
        (ticket_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def insert_ticket(ticket_id, customer_message, sentiment, intent, department):
    """Inserts a new ticket into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO support_tickets 
        (ticket_id, customer_message, status, sentiment, intent, 
         department, created_at, agent_handled)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        customer_message,
        "Unresolved",
        sentiment,
        intent,
        department,
        datetime.now(),
        "FeedbackHandlerAgent"
    ))
    conn.commit()
    conn.close()

def get_all_tickets():
    """Returns all tickets as a list of dicts for display."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ticket_id, customer_message, status, intent, 
               department, created_at, agent_handled 
        FROM support_tickets 
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "Ticket ID": row[0],
            "Message": row[1][:50] + "..." if len(row[1]) > 50 else row[1],
            "Status": row[2],
            "Intent": row[3],
            "Department": row[4],
            "Created": row[5],
            "Agent": row[6]
        }
        for row in rows
    ]

if __name__ == "__main__":
    setup_database()