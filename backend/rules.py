"""
RBI Regulatory Rules - Knowledge Base (Law Layer)
Encodes hard constraints and conditional dependencies from RBI Master Directions.
"""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class RBIRule:
    rule_id: str
    category: str
    title: str
    description: str
    source_document: str
    constraint_type: str  # hard_limit | conditional | document_required
    parameters: dict[str, Any] = field(default_factory=dict)

# ─────────────────────────────────────────────────────────────────────────────
# KYC Rules – Master Direction KYC 2016 (Updated Aug 2025)
# ─────────────────────────────────────────────────────────────────────────────

KYC_RULES: list[RBIRule] = [
    RBIRule(
        rule_id="KYC_001",
        category="KYC",
        title="Small Account Transfer Limit",
        description="Accounts with OTP/limited KYC (Small Accounts) have a maximum single transaction transfer limit of ₹10,000.",
        source_document="Master Direction - KYC Direction, 2016 (Updated Aug 2025)",
        constraint_type="hard_limit",
        parameters={
            "max_transaction": 10_000,
            "account_types": ["small", "otp_only", "limited_kyc"],
            "metric": "amount",
        },
    ),
    RBIRule(
        rule_id="KYC_002",
        category="KYC",
        title="Small Account Annual Credit Limit",
        description="Small Accounts (limited KYC) cannot receive more than ₹1,00,000 total credit in a year.",
        source_document="Master Direction - KYC Direction, 2016 (Updated Aug 2025)",
        constraint_type="hard_limit",
        parameters={
            "max_annual_credit": 1_00_000,
            "account_types": ["small", "otp_only", "limited_kyc"],
            "metric": "annual_credit",
        },
    ),
    RBIRule(
        rule_id="KYC_003",
        category="KYC",
        title="Small Account Balance Limit",
        description="Small Accounts (limited KYC) cannot maintain a balance exceeding ₹50,000 at any point.",
        source_document="Master Direction - KYC Direction, 2016 (Updated Aug 2025)",
        constraint_type="hard_limit",
        parameters={
            "max_balance": 50_000,
            "account_types": ["small", "otp_only", "limited_kyc"],
            "metric": "balance",
        },
    ),
    RBIRule(
        rule_id="KYC_004",
        category="KYC",
        title="Full KYC Required for High-Value Transactions",
        description="Transactions above ₹50,000 or loans above ₹5,00,000 require Full KYC (Aadhaar + PAN + address proof).",
        source_document="Master Direction - KYC Direction, 2016 (Updated Aug 2025)",
        constraint_type="conditional",
        parameters={
            "threshold_transaction": 50_000,
            "threshold_loan": 5_00_000,
            "required_kyc": "full",
            "required_docs": [
                "Aadhaar Card / Passport / Voter ID (OVD)",
                "PAN Card",
                "Address Proof (utility bill / bank statement < 2 months old)",
                "Recent passport-size photograph",
            ],
        },
    ),
    RBIRule(
        rule_id="KYC_005",
        category="KYC",
        title="Re-KYC Requirement",
        description="Customers must complete periodic Re-KYC: High-risk every 2 years, Medium-risk every 8 years, Low-risk every 10 years.",
        source_document="Master Direction - KYC Direction, 2016 (Updated Aug 2025)",
        constraint_type="conditional",
        parameters={
            "high_risk_years": 2,
            "medium_risk_years": 8,
            "low_risk_years": 10,
            "required_docs": [
                "Updated address proof",
                "Updated identity document",
                "Self-declaration if no change",
            ],
        },
    ),
    RBIRule(
        rule_id="KYC_006",
        category="KYC",
        title="Non-Face-to-Face KYC (Video KYC / V-CIP)",
        description="For digital/online account opening, Video-based Customer Identification Process (V-CIP) is required for Full KYC.",
        source_document="Master Direction - KYC Direction, 2016 (Updated Aug 2025) – Amendment 2024-25",
        constraint_type="document_required",
        parameters={
            "required_docs": [
                "Original OVD (Aadhaar / Passport / Voter ID) for video display",
                "PAN Card",
                "Live geolocation capture during V-CIP",
                "Live photo capture during V-CIP",
            ],
            "applicability": "digital_onboarding",
        },
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# Loan / Advances Rules – Master Circular Loans & Advances
# ─────────────────────────────────────────────────────────────────────────────

LOAN_RULES: list[RBIRule] = [
    RBIRule(
        rule_id="LOAN_001",
        category="Loans",
        title="Personal Loan Cap (Unsecured)",
        description="Unsecured personal loans without collateral are typically capped at ₹10,00,000 for individual borrowers without income proof.",
        source_document="Master Circular – Loans and Advances – Statutory and Other Restrictions",
        constraint_type="hard_limit",
        parameters={
            "max_amount": 10_00_000,
            "loan_type": "personal_unsecured",
            "metric": "loan_amount",
        },
    ),
    RBIRule(
        rule_id="LOAN_002",
        category="Loans",
        title="High-Value Loan Documentation Requirements",
        description="Loans above ₹25,00,000 require income proof (ITR for 2 years), bank statements, credit report, and collateral documents.",
        source_document="Master Circular – Loans and Advances – Statutory and Other Restrictions",
        constraint_type="conditional",
        parameters={
            "threshold": 25_00_000,
            "required_docs": [
                "Income Tax Returns (ITR) for last 2 financial years",
                "Form 16 / Salary Slips (last 3 months)",
                "Bank statements (last 6 months)",
                "CIBIL / Credit score report",
                "Collateral documents (if secured loan)",
                "Property papers / valuation report (for property loans)",
            ],
            "required_criteria": [
                "Minimum CIBIL score of 700",
                "Debt-to-Income (DTI) ratio below 50%",
                "Minimum 2 years of employment / business continuity",
            ],
        },
    ),
    RBIRule(
        rule_id="LOAN_003",
        category="Loans",
        title="Crore-Level Loan (1 Crore+) Requirements",
        description="Loans of ₹1 Crore or above require Full KYC, ITR for 3 years, audited financials, collateral with legal clearance, and credit committee approval.",
        source_document="Master Circular – Loans and Advances – Statutory and Other Restrictions",
        constraint_type="conditional",
        parameters={
            "threshold": 1_00_00_000,
            "required_kyc": "full",
            "required_docs": [
                "Full KYC documents (Aadhaar, PAN, Address Proof, Photograph)",
                "Income Tax Returns (ITR) for last 3 financial years",
                "Audited Financial Statements (for business/corporate loans)",
                "CA-certified Balance Sheet",
                "Bank statements (last 12 months)",
                "CIBIL / Credit Bureau Report",
                "Collateral documents with legal due diligence report",
                "Property valuation report from empanelled valuer",
                "Insurance documents for collateral",
                "No-Objection Certificate (NOC) from existing lenders (if any)",
                "Business plan / Project report (for business loans)",
                "Co-applicant / Guarantor documents (if applicable)",
            ],
            "required_criteria": [
                "Full KYC compliance (Aadhaar + PAN + Address verified)",
                "Minimum CIBIL score of 750",
                "Debt-to-Income ratio below 40%",
                "Minimum 3 years of stable income history",
                "Collateral value >= 125% of loan amount (for secured loans)",
                "No ongoing defaults or NPA history",
                "Credit committee / senior management approval",
                "Legal clearance on collateral property",
            ],
        },
    ),
    RBIRule(
        rule_id="LOAN_004",
        category="Loans",
        title="Prohibition on Loans to Directors / Related Parties",
        description="Banks cannot sanction loans to their own directors or their relatives without Board approval and RBI disclosure norms.",
        source_document="Master Circular – Loans and Advances – Statutory and Other Restrictions",
        constraint_type="hard_limit",
        parameters={
            "prohibited_entities": ["bank_director", "director_relative", "related_party"],
            "exception": "board_approval_required",
        },
    ),
    RBIRule(
        rule_id="LOAN_005",
        category="Loans",
        title="Priority Sector Lending Classification",
        description="Loans to agriculture (up to ₹1,60,000 crop loan), MSMEs (manufacturing up to ₹25 Crore, services up to ₹10 Crore), and weaker sections qualify for priority sector.",
        source_document="Master Direction – Priority Sector Lending – Targets and Classification (Dec 2019)",
        constraint_type="conditional",
        parameters={
            "agriculture_crop_limit": 1_60_000,
            "msme_manufacturing_limit": 25_00_00_000,
            "msme_services_limit": 10_00_00_000,
            "required_docs": [
                "Land ownership / tenancy documents (for agriculture)",
                "Kisan Credit Card (if applicable)",
                "Udyam Registration Certificate (for MSME)",
                "GST registration (if applicable)",
                "Business vintage proof (min 1 year for MSME loans)",
            ],
        },
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# Digital Lending Rules – RBI Digital Lending Directions, 2025
# ─────────────────────────────────────────────────────────────────────────────

DIGITAL_LENDING_RULES: list[RBIRule] = [
    RBIRule(
        rule_id="DL_001",
        category="Digital Lending",
        title="Key Fact Statement (KFS) Mandatory",
        description="All digital lenders must provide a Key Fact Statement before loan disbursal. No loan can be disbursed without KFS acknowledgment.",
        source_document="RBI Digital Lending Directions, 2025",
        constraint_type="document_required",
        parameters={
            "required_docs": [
                "Key Fact Statement (KFS) – must be acknowledged by borrower",
                "Loan agreement signed digitally",
                "Sanction letter with all charges disclosed",
            ],
            "required_criteria": [
                "Annual Percentage Rate (APR) must be disclosed upfront",
                "All fees, penalties, and charges must be listed in KFS",
                "No hidden charges allowed",
            ],
        },
    ),
    RBIRule(
        rule_id="DL_002",
        category="Digital Lending",
        title="Cooling-Off Period for Digital Loans",
        description="Borrowers must be given a minimum cooling-off period of 3 days for loans up to ₹50,000 and 7 days for loans above ₹50,000 to exit without penalty.",
        source_document="RBI Digital Lending Directions, 2025",
        constraint_type="hard_limit",
        parameters={
            "cooling_off_small": 3,
            "cooling_off_large": 7,
            "threshold": 50_000,
            "metric": "cooling_off_days",
        },
    ),
    RBIRule(
        rule_id="DL_003",
        category="Digital Lending",
        title="Direct Disbursal to Borrower Account",
        description="Loan funds must be disbursed directly to the borrower's verified bank account. Disbursement to third-party accounts or wallets is prohibited.",
        source_document="RBI Digital Lending Directions, 2025",
        constraint_type="hard_limit",
        parameters={
            "prohibited": ["third_party_account", "wallet", "prepaid_instrument"],
            "required": "verified_bank_account_only",
        },
    ),
    RBIRule(
        rule_id="DL_004",
        category="Digital Lending",
        title="Default Loss Guarantee Cap",
        description="Default Loss Guarantee (DLG) in digital lending is capped at 5% of the outstanding loan portfolio. Exceeding this requires RBI approval.",
        source_document="Guidelines on Default Loss Guarantee in Digital Lending",
        constraint_type="hard_limit",
        parameters={
            "max_dlg_percentage": 5.0,
            "metric": "dlg_percentage",
        },
    ),
    RBIRule(
        rule_id="DL_005",
        category="Digital Lending",
        title="Lending Service Provider Registration",
        description="All Lending Service Providers (LSPs) must be registered with RBI and listed in the RE's (Regulated Entity's) approved LSP registry.",
        source_document="RBI Digital Lending Directions, 2025",
        constraint_type="document_required",
        parameters={
            "required_docs": [
                "RBI registration certificate for LSP",
                "LSP agreement with Regulated Entity (RE)",
                "Data privacy agreement",
            ],
        },
    ),
    RBIRule(
        rule_id="DL_006",
        category="Digital Lending",
        title="Data Collection Consent",
        description="Digital lenders cannot collect sensitive personal data (biometrics, contacts, location) without explicit one-time consent from borrower.",
        source_document="RBI Digital Lending Directions, 2025",
        constraint_type="document_required",
        parameters={
            "required_docs": [
                "Explicit data consent form (one-time, not bundled)",
                "Privacy policy acknowledgment",
            ],
            "prohibited": ["one_time_mandate_override", "auto_debit_without_consent"],
        },
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# Credit Card Rules – Master Direction Credit & Debit Cards, 2022 (Mar 2024)
# ─────────────────────────────────────────────────────────────────────────────

CREDIT_CARD_RULES: list[RBIRule] = [
    RBIRule(
        rule_id="CC_001",
        category="Credit Cards",
        title="Credit Card Interest Rate Disclosure",
        description="All credit card issuers must disclose the Annual Percentage Rate (APR) and all fees in the Key Fact Statement before issuance.",
        source_document="Master Direction – Credit Card and Debit Card – Issuance and Conduct Directions, 2022 (Updated Mar 2024)",
        constraint_type="document_required",
        parameters={
            "required_docs": [
                "Key Fact Statement with APR disclosure",
                "Most Important Terms and Conditions (MITC) document",
                "Schedule of charges",
            ],
        },
    ),
    RBIRule(
        rule_id="CC_002",
        category="Credit Cards",
        title="Credit Card Application Income Criteria",
        description="Credit cards can only be issued to individuals with a minimum net annual income of ₹3,00,000 or as per bank policy (minimum floor).",
        source_document="Master Direction – Credit Card and Debit Card – Issuance and Conduct Directions, 2022 (Updated Mar 2024)",
        constraint_type="conditional",
        parameters={
            "min_annual_income": 3_00_000,
            "required_docs": [
                "Income proof (ITR / Form 16 / Salary slips for 3 months)",
                "Employment proof (appointment letter / employment certificate)",
                "Bank statements (last 3 months)",
                "KYC documents (Aadhaar, PAN, address proof)",
                "Recent passport-size photograph",
            ],
            "required_criteria": [
                "Minimum net annual income of ₹3,00,000",
                "Good credit history (no defaults in last 12 months)",
                "Minimum age 18 years",
            ],
        },
    ),
    RBIRule(
        rule_id="CC_003",
        category="Credit Cards",
        title="Credit Limit Enhancement Restrictions",
        description="Credit limit enhancement requires fresh income proof and cannot be done more than once in 6 months.",
        source_document="Master Direction – Credit Card and Debit Card – Issuance and Conduct Directions, 2022 (Updated Mar 2024)",
        constraint_type="conditional",
        parameters={
            "min_gap_months": 6,
            "required_docs": [
                "Updated income proof (ITR / salary slips)",
                "Recent bank statements",
            ],
        },
    ),
    RBIRule(
        rule_id="CC_004",
        category="Credit Cards",
        title="Unauthorized Transaction Liability",
        description="If unauthorized transaction reported within 3 days: zero liability. Within 4-7 days: max liability ₹10,000. Beyond 7 days: full liability.",
        source_document="Master Direction – Credit Card and Debit Card – Issuance and Conduct Directions, 2022 (Updated Mar 2024)",
        constraint_type="hard_limit",
        parameters={
            "zero_liability_days": 3,
            "partial_liability_days": 7,
            "partial_liability_max": 10_000,
            "metric": "reporting_days",
        },
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# Consolidated Rule Registry
# ─────────────────────────────────────────────────────────────────────────────

ALL_RULES: list[RBIRule] = KYC_RULES + LOAN_RULES + DIGITAL_LENDING_RULES + CREDIT_CARD_RULES

RULE_REGISTRY: dict[str, RBIRule] = {r.rule_id: r for r in ALL_RULES}
