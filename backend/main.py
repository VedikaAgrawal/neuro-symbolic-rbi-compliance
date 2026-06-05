"""
FastAPI Backend – Hybrid Neuro-Symbolic Guardrails
Entry point for the compliance verification API.
Securely manages the Neuro-Symbolic flow, invokes Gemini and Z3, and writes logs to Supabase.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import os
from dotenv import load_dotenv

# Import our neural and symbolic components
from backend.extractor import extract_facts_from_query, generate_explanation
from backend.solver import verify
from backend.rules import ALL_RULES

# Load environment variables
load_dotenv()

# Initialize FastAPI App
app = FastAPI(
    title="Hybrid Neuro-Symbolic Guardrails API",
    description="Deterministic verification of financial queries against RBI regulations using Gemini LLM and Z3 SMT Solver.",
    version="1.0.0",
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development and demos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase Python Client (Secure Server-Side Logging)
supabase = None
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if supabase_url and supabase_key:
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        print("INFO: Supabase client securely initialized in the backend.")
    except Exception as e:
        print(f"WARNING: Failed to initialize Supabase client: {e}")
else:
    print("WARNING: Supabase URL or Key missing in backend/.env. Logging disabled.")


# ─────────────────────────────────────────────────────────────────────────────
# API Data Models
# ─────────────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    context: dict[str, Any] = {}


class VerificationResponse(BaseModel):
    verdict: str
    explanation: str
    extracted_facts: dict[str, Any]
    violations: list[str]
    required_documents: list[str]
    required_criteria: list[str]
    triggered_rules: list[dict[str, Any]]
    counterfactual: str


# ─────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "rules_loaded": len(ALL_RULES),
        "supabase_connected": supabase is not None,
        "gemini_active": os.getenv("GEMINI_API_KEY") is not None
    }


@app.get("/rules")
def list_rules():
    """List all loaded RBI regulations."""
    return [
        {
            "rule_id": r.rule_id,
            "category": r.category,
            "title": r.title,
            "description": r.description,
            "source_document": r.source_document,
            "constraint_type": r.constraint_type,
        }
        for r in ALL_RULES
    ]


@app.post("/verify", response_model=VerificationResponse)
def verify_query(request: QueryRequest):
    """
    Main verification endpoint.
    Orchestrates the entire Neuro-Symbolic compliance pipeline:
    1. Neural Perception (Gemini LLM fact extraction)
    2. Symbolic Verification (Z3 SMT Solver constraint checking)
    3. Counterfactual guidance generation
    4. Secure database query logging to Supabase
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Phase 1: Neural Perception – extract structured facts from query
    facts = extract_facts_from_query(request.query)

    # Merge any frontend-provided context overrides (e.g. mock overrides for debugging)
    if request.context:
        facts.update(request.context)

    # Phase 2: Symbolic Verification – run mathematical constraints in Z3
    result = verify(facts)

    verdict = result["verdict"]
    violations = result["violations"]
    required_docs = result["required_documents"]
    required_criteria = result["required_criteria"]
    triggered_rules = result["triggered_rules"]

    # Phase 3: Max-SMT Counterfactual Guidance
    counterfactual = ""
    if verdict == "UNSAT":
        amount = facts.get("amount", 0)
        action = facts.get("action", "request")
        
        if action in ("loan", "loan_apply", "personal_loan"):
            if amount >= 1_00_00_000:
                counterfactual = (
                    "To satisfy compliance: Complete Full KYC, submit ITR for the last 3 financial years, "
                    "maintain a CIBIL score ≥ 750, and provide legally cleared collateral worth at least 125% of the loan amount."
                )
            elif amount >= 25_00_000:
                counterfactual = (
                    "To satisfy compliance: Submit ITR for the last 2 financial years, ensure a CIBIL score ≥ 700, "
                    "and complete Full KYC. Alternatively, reducing the loan amount below ₹25,00,000 relaxes these criteria."
                )
            else:
                counterfactual = (
                    "Ensure Full KYC is completed and standard identification papers (PAN + Aadhaar) are submitted."
                )
        elif action == "transfer" and facts.get("account_type") in ("small", "otp_only"):
            counterfactual = (
                "To transfer amounts above ₹10,000: Upgrade your limited KYC account to Full KYC (via V-CIP video process "
                "or physical branch visit). Otherwise, keep individual transfers capped strictly below ₹10,000."
            )
        elif action == "credit_card_apply":
            counterfactual = (
                "To satisfy compliance: Ensure your net annual income is at least ₹3,00,000 and submit income proof (salary slips / ITR)."
            )
        elif action == "digital_loan":
            counterfactual = (
                "To satisfy compliance: Fully review and acknowledge the Key Fact Statement (KFS) before proceeding, "
                "ensure disbursal is set to a verified bank account (not a prepaid wallet), and DLG is capped under 5%."
            )

    # Phase 4: Explanation Generation
    explanation = generate_explanation(
        verdict, violations, facts, required_docs, required_criteria, triggered_rules
    )

    # Phase 5: Secure Server-Side Database Logging
    if supabase:
        try:
            # We execute insert in a non-blocking way to keep API response times fast
            supabase.table("query_logs").insert({
                "user_query": request.query,
                "extracted_facts": facts,
                "verdict": verdict,
                "rules_triggered": triggered_rules,
                "required_documents": required_docs,
                "required_criteria": required_criteria,
                "explanation": explanation,
                "counterfactual": counterfactual
            }).execute()
        except Exception as e:
            print(f"WARNING: Supabase Logging failed: {e}")

    # Return response payload
    return VerificationResponse(
        verdict=verdict,
        explanation=explanation,
        extracted_facts=facts,
        violations=violations,
        required_documents=required_docs,
        required_criteria=required_criteria,
        triggered_rules=triggered_rules,
        counterfactual=counterfactual,
    )


@app.post("/extract")
def extract_only(request: QueryRequest):
    """Extract facts from query without running verification (for debugging)."""
    facts = extract_facts_from_query(request.query)
    if request.context:
        facts.update(request.context)
    return {"extracted_facts": facts}


if __name__ == "__main__":
    import uvicorn
    # Start ASGI server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
