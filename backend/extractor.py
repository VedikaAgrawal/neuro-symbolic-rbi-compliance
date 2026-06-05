"""
Neural Perception Layer – Entity and Intent Extraction
Uses Google Gemini 1.5 Flash (with forced structured schema) to parse 
natural language financial queries into structured JSON facts. 
Includes a robust regex fallback when the Gemini API key is not configured.
"""

import os
import re
import json
from typing import Any, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Google Generative AI if key is present
GEMINI_ACTIVE = False
client = None
try:
    from google import genai
    from google.genai import types
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip():
        client = genai.Client(api_key=api_key)
        GEMINI_ACTIVE = True
    else:
        print("WARNING: GEMINI_API_KEY is empty. Running with Regex Fallback.")
except ImportError:
    print("WARNING: google-genai package not installed. Running with Regex Fallback.")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Pydantic Extraction Schema (For Gemini Structured Output)
# ─────────────────────────────────────────────────────────────────────────────

class ExtractedFactsSchema(BaseModel):
    action: Literal["loan", "transfer", "digital_loan", "credit_card_apply", "dispute_unauthorized"] = Field(
        description="The high-level financial request category: 'loan' (standard, home, vehicle, education or business loans), 'transfer' (fund transfers via UPI/NEFT/IMPS), 'digital_loan' (fintech/app loans or Buy Now Pay Later), 'credit_card_apply' (applying for credit cards), or 'dispute_unauthorized' (disputing fraudulent transactions)."
    )
    amount: float = Field(
        description="The numeric amount involved in Rupees (INR). Parse words like '1 crore' as 10000000, '50 lakh' as 5000000, '25L' as 2500000, '10k' as 10000."
    )
    kyc_status: Literal["full", "limited", "none", "unknown"] = Field(
        description="KYC status. 'full' if user explicitly says they have Aadhaar, PAN, complete KYC, or video KYC. 'limited' if OTP account, small account, or limited KYC. 'none' if no KYC."
    )
    loan_type: Literal["personal", "home", "business", "vehicle", "education"] = Field(
        description="The sub-type of loan. Mapped from terms like 'home', 'business', 'corporate', 'msme', 'car', 'study', etc."
    )
    has_itr: bool = Field(
        description="True if the query mentions Income Tax Returns (ITR) or tax filings."
    )
    itr_years: int = Field(
        description="The number of years of ITR mentioned (e.g. 'ITR for 2 years' -> 2)."
    )
    has_collateral: bool = Field(
        description="True if user mentions security, collateral, mortgage, property papers, or assets to pledge."
    )
    has_audited_financials: bool = Field(
        description="True if the user has audited statements, Chartered Accountant (CA) certificates, or balance sheets."
    )
    cibil_score: int = Field(
        description="The CIBIL or credit score mentioned (e.g. 'cibil of 750' -> 750)."
    )
    annual_income: float = Field(
        description="Annual income or salary mentioned in INR (e.g., 'income of 6 lakh per year' -> 600000)."
    )
    annual_credit: float = Field(
        description="Total annual credit received in small/limited accounts in INR."
    )
    current_balance: float = Field(
        description="Current account balance in INR."
    )
    has_kfs: bool = Field(
        description="True if Key Fact Statement (KFS) is mentioned, acknowledged, or provided."
    )
    dlg_percentage: float = Field(
        description="Default Loss Guarantee (DLG) percentage mentioned (0 to 100)."
    )
    disburse_to: Literal["bank_account", "wallet", "third_party_account"] = Field(
        description="The target account for loan disbursement. Set to 'wallet' if wallet/prepaid is mentioned, 'third_party_account' if sent to someone else's account."
    )
    reporting_days: int = Field(
        description="Number of days elapsed before reporting an unauthorized transaction dispute."
    )
    account_type: Literal["full_kyc", "small", "otp_only"] = Field(
        description="Type of bank account. 'small' or 'otp_only' if limited KYC or small account mentioned."
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Regex Fallback Engine (Robust Procedural Extraction)
# ─────────────────────────────────────────────────────────────────────────────

def _parse_amount_from_text(text: str) -> float:
    text_lower = text.lower()
    patterns = [
        (r"₹\s*([\d,]+(?:\.\d+)?)\s*crore", lambda m: float(m.group(1).replace(",", "")) * 1_00_00_000),
        (r"₹\s*([\d,]+(?:\.\d+)?)\s*cr\b", lambda m: float(m.group(1).replace(",", "")) * 1_00_00_000),
        (r"([\d,]+(?:\.\d+)?)\s*crore", lambda m: float(m.group(1).replace(",", "")) * 1_00_00_000),
        (r"₹\s*([\d,]+(?:\.\d+)?)\s*lakh", lambda m: float(m.group(1).replace(",", "")) * 1_00_000),
        (r"₹\s*([\d,]+(?:\.\d+)?)\s*lac\b", lambda m: float(m.group(1).replace(",", "")) * 1_00_000),
        (r"([\d,]+(?:\.\d+)?)\s*lakh", lambda m: float(m.group(1).replace(",", "")) * 1_00_000),
        (r"₹\s*([\d,]+(?:\.\d+)?)\s*thousand", lambda m: float(m.group(1).replace(",", "")) * 1_000),
        (r"([\d,]+(?:\.\d+)?)\s*k\b", lambda m: float(m.group(1).replace(",", "")) * 1_000),
        (r"₹\s*([\d,]+(?:\.\d+)?)", lambda m: float(m.group(1).replace(",", ""))),
        (r"rs\.?\s*([\d,]+(?:\.\d+)?)", lambda m: float(m.group(1).replace(",", ""))),
        (r"inr\s*([\d,]+(?:\.\d+)?)", lambda m: float(m.group(1).replace(",", ""))),
    ]
    for pattern, converter in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return converter(match)

    word_map = {
        "one crore": 1_00_00_000, "1 crore": 1_00_00_000,
        "two crore": 2_00_00_000, "five crore": 5_00_00_000,
        "ten crore": 10_00_00_000, "fifty lakh": 50_00_000,
        "one lakh": 1_00_000, "fifty thousand": 50_000,
        "sixty thousand": 60_000, "ten thousand": 10_000,
    }
    for phrase, value in word_map.items():
        if phrase in text_lower:
            return float(value)
    return 0.0


def _detect_action(text: str) -> str:
    text_lower = text.lower()
    digital_lending_keywords = ["digital loan", "bnpl", "buy now pay later", "fintech", "app loan", "online loan"]
    credit_card_keywords = ["credit card", "debit card", "card apply", "card limit", "unauthorized transaction", "fraud charge"]
    loan_keywords = ["loan", "borrow", "lending", "credit", "mortgage", "emi", "finance", "fund"]
    transfer_keywords = ["transfer", "send", "remit", "neft", "rtgs", "imps", "upi", "pay"]

    for kw in digital_lending_keywords:
        if kw in text_lower:
            return "digital_loan"
    for kw in credit_card_keywords:
        if kw in text_lower:
            if "unauthorized" in text_lower or "fraud" in text_lower or "charge" in text_lower:
                return "dispute_unauthorized"
            return "credit_card_apply"
    for kw in loan_keywords:
        if kw in text_lower:
            return "loan"
    for kw in transfer_keywords:
        if kw in text_lower:
            return "transfer"
    return "loan"


def _detect_kyc_status(text: str) -> str:
    text_lower = text.lower()
    if "full kyc" in text_lower or "complete kyc" in text_lower or "v-cip" in text_lower:
        return "full"
    if "otp" in text_lower and ("account" in text_lower or "kyc" in text_lower):
        return "limited"
    if "small account" in text_lower or "limited kyc" in text_lower:
        return "limited"
    if "no kyc" in text_lower or "without kyc" in text_lower:
        return "none"
    return "unknown"


def _detect_loan_type(text: str) -> str:
    text_lower = text.lower()
    if "home" in text_lower or "house" in text_lower or "property" in text_lower:
        return "home"
    if "business" in text_lower or "corporate" in text_lower or "msme" in text_lower:
        return "business"
    if "car" in text_lower or "vehicle" in text_lower or "auto" in text_lower:
        return "vehicle"
    if "education" in text_lower or "study" in text_lower:
        return "education"
    return "personal"


def fallback_extract_facts_from_query(query: str) -> dict[str, Any]:
    text_lower = query.lower()
    facts = {
        "action": _detect_action(query),
        "amount": _parse_amount_from_text(query),
        "kyc_status": _detect_kyc_status(query),
        "loan_type": _detect_loan_type(query),
        "has_itr": bool(re.search(r"\bitr\b|income tax return|tax return", text_lower)),
        "itr_years": 0,
        "has_collateral": bool(re.search(r"collateral|security|mortgage|pledge|property", text_lower)),
        "has_audited_financials": bool(re.search(r"audited|ca certificate|chartered accountant|balance sheet", text_lower)),
        "cibil_score": 0,
        "annual_income": 0.0,
        "annual_credit": 0.0,
        "current_balance": 0.0,
        "has_kfs": bool(re.search(r"kfs|key fact|fact statement", text_lower)),
        "dlg_percentage": 0.0,
        "disburse_to": "bank_account",
        "reporting_days": 0,
        "account_type": "full_kyc",
    }

    # ITR years
    itr_match = re.search(r"(\d+)\s*year[s]?\s*itr|itr\s*(?:for\s*)?(\d+)\s*year", text_lower)
    if itr_match:
        facts["itr_years"] = int(itr_match.group(1) or itr_match.group(2))
    elif facts["has_itr"]:
        facts["itr_years"] = 1

    # CIBIL score
    cibil_match = re.search(r"cibil[:\s]+(\d{3})|credit score[:\s]+(\d{3})|score\s+of\s+(\d{3})", text_lower)
    if cibil_match:
        facts["cibil_score"] = int(next(g for g in cibil_match.groups() if g))

    # Annual Income
    if "income" in text_lower or "salary" in text_lower:
        income_match = re.search(
            r"(?:income|salary)\s*(?:of|is|:)?\s*₹?\s*([\d,]+(?:\.\d+)?)\s*(lakh|crore|thousand|k)?",
            text_lower
        )
        if income_match:
            val = float(income_match.group(1).replace(",", ""))
            multiplier_map = {"lakh": 1_00_000, "crore": 1_00_00_000, "thousand": 1_000, "k": 1_000}
            unit = income_match.group(2)
            facts["annual_income"] = float(val * multiplier_map.get(unit or "", 1))

    if facts["kyc_status"] in ("limited", "none"):
        facts["account_type"] = "small"
    elif "otp" in text_lower:
        facts["account_type"] = "otp_only"

    if "wallet" in text_lower:
        facts["disburse_to"] = "wallet"
    elif "third party" in text_lower:
        facts["disburse_to"] = "third_party_account"

    days_match = re.search(r"(\d+)\s*day[s]?\s*(?:ago|back|later|after)", text_lower)
    if days_match:
        facts["reporting_days"] = int(days_match.group(1))

    return facts


# ─────────────────────────────────────────────────────────────────────────────
# 3. Default Facts Fallback (Resolves Undefined Fields)
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_FACTS: dict[str, Any] = {
    "action": "loan",
    "amount": 0.0,
    "kyc_status": "unknown",
    "loan_type": "personal",
    "has_itr": False,
    "itr_years": 0,
    "has_collateral": False,
    "has_audited_financials": False,
    "cibil_score": 0,
    "annual_income": 0.0,
    "annual_credit": 0.0,
    "current_balance": 0.0,
    "has_kfs": False,
    "dlg_percentage": 0.0,
    "disburse_to": "bank_account",
    "reporting_days": 0,
    "account_type": "full_kyc"
}


# ─────────────────────────────────────────────────────────────────────────────
# 4. Main Entrypoint: Neural Layer Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def extract_facts_from_query(query: str) -> dict[str, Any]:
    """
    Extract structured facts from a natural language query using Google Gemini.
    Falls back gracefully to procedural regex rules if Gemini is inactive or fails.
    """
    if not GEMINI_ACTIVE or client is None:
        return fallback_extract_facts_from_query(query)

    try:
        prompt = f"Extract compliance entities from the following user query:\n\n\"{query}\""
        
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an expert NLP parser designed to extract compliance-relevant facts from financial queries. "
                    "You must strictly parse inputs into the provided JSON schema. Ensure currency words are converted "
                    "into raw floating-point numbers in Rupees (INR) (e.g., '1 crore' -> 10000000.0, '50 lakh' -> 5000000.0). "
                    "Infer properties logically. For example, if a user mentions 'applying via fintech app' or 'BNPL', action is 'digital_loan'. "
                    "If they complain about a card charge or fraud, action is 'dispute_unauthorized'."
                ),
                response_mime_type="application/json",
                response_schema=ExtractedFactsSchema,
                temperature=0.1
            )
        )
        
        extracted_data = json.loads(response.text)
        # Merge with defaults to ensure all required fields are populated
        return {**DEFAULT_FACTS, **extracted_data}
        
    except Exception as e:
        print(f"WARNING: Gemini SFI Extraction failed. Falling back to Regex. Error: {e}")
        return fallback_extract_facts_from_query(query)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Natural Language Explanation Generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_explanation(verdict: str, violations: list[str], facts: dict[str, Any],
                          required_docs: list[str], required_criteria: list[str],
                          rules_triggered: list[dict]) -> str:
    """
    Generate a clear natural-language explanation summary of the compliance check.
    """
    action = facts.get("action", "request")
    amount = facts.get("amount", 0)
    amount_str = f"₹{int(amount):,}" if amount > 0 else "the requested amount"
    action_clean = action.replace('_', ' ').capitalize()

    if verdict == "SAT":
        explanation = f"Your {action_clean} request of {amount_str} satisfies all applicable RBI regulations under our symbolic SMT solver checks.\n\n"
        if required_docs or required_criteria:
            explanation += "Please verify that you fulfill the remaining documents and criteria listed below before finalizing the transaction."
        else:
            explanation += "No compliance violations or document requirements have been triggered."
    else:
        num_violations = len(violations)
        explanation = f"Your {action_clean} request of {amount_str} is NOT compliant with current RBI regulations. We detected {num_violations} compliance violation(s).\n\n"
        explanation += "Please address the direct violations and submit all mandatory documents listed in the sections below to satisfy the SMT logic constraints."

    return explanation
