"""
Seed script to populate the Supabase `rbi_rules` table.
Imports rules defined in `backend/rules.py` and upserts them to Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Import rules from rules.py
from backend.rules import ALL_RULES

# Load env variables from backend/.env
# This ensures it finds the .env inside the backend folder first
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def seed_rules():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL or SUPABASE_KEY is missing in your backend/.env file.")
        return

    # Initialize Supabase client
    print(f"Initializing Supabase client targeting: {supabase_url}")
    supabase = create_client(supabase_url, supabase_key)

    # Prepare data for upload
    records = []
    for rule in ALL_RULES:
        records.append({
            "rule_id": rule.rule_id,
            "category": rule.category,
            "title": rule.title,
            "description": rule.description,
            "source_document": rule.source_document,
            "constraint_type": rule.constraint_type,
            "parameters": rule.parameters
        })

    print(f"Prepared {len(records)} rules for upload.")

    try:
        # Perform upsert to prevent duplicates if the script is run multiple times
        print("Uploading rules to Supabase...")
        response = supabase.table("rbi_rules").upsert(records, on_conflict="rule_id").execute()
        
        # In newer supabase-py versions, data is inside response.data
        if response.data:
            print(f"Success! Successfully seeded/updated {len(response.data)} rules in the database.")
        else:
            print("Successfully executed query. Check your Supabase table dashboard.")
            
    except Exception as e:
        print(f"An error occurred while seeding rules: {e}")

if __name__ == "__main__":
    seed_rules()
