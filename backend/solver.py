"""
Z3 SMT Solver Engine – Symbolic Verification Layer
Formally models RBI rules as mathematical constraints and checks compliance
deterministically using Microsoft's Z3 SMT Solver.
"""
from z3 import Solver, Int, Real, Bool, And, Or, Not, Implies, sat, Optimize, is_true
from backend.rules import ALL_RULES, RULE_REGISTRY, RBIRule
from typing import Any

# Declare Global Z3 Symbolic Variables
amount_var = Int("amount")
kyc_status_var = Int("kyc_status")  # 0: none, 1: limited/small, 2: full
loan_type_var = Int("loan_type")    # 1: personal, 2: home, 3: business, 4: vehicle, 5: education
has_itr_var = Bool("has_itr")
itr_years_var = Int("itr_years")
has_collateral_var = Bool("has_collateral")
has_audited_financials_var = Bool("has_audited_financials")
cibil_score_var = Int("cibil_score")
annual_income_var = Int("annual_income")
annual_credit_var = Int("annual_credit")
current_balance_var = Int("current_balance")
has_kfs_var = Bool("has_kfs")
dlg_percentage_var = Real("dlg_percentage")
disburse_to_var = Int("disburse_to")  # 1: bank_account, 2: wallet, 3: third_party_account
reporting_days_var = Int("reporting_days")
account_type_var = Int("account_type") # 0: small/otp_only, 1: full_kyc
action_var = Int("action")            # 1: loan, 2: transfer, 3: digital_loan, 4: credit_card_apply, 5: dispute_unauthorized

# Enum Mapping Directories for Z3 compatibility
KYC_MAP = {"none": 0, "limited": 1, "unknown": 1, "full": 2}
LOAN_MAP = {"personal": 1, "home": 2, "business": 3, "vehicle": 4, "education": 5}
DISBURSE_MAP = {"bank_account": 1, "wallet": 2, "third_party_account": 3}
ACCOUNT_MAP = {"small": 0, "otp_only": 0, "full_kyc": 1}
ACTION_MAP = {"loan": 1, "transfer": 2, "digital_loan": 3, "credit_card_apply": 4, "dispute_unauthorized": 5}

# Global M.Tech Symbolic Rule Logic Network Templates
# Each rule contains: (Applicability_Constraint, Compliance_Constraint, Error_Message_Template)
RULES_LOGIC_TEMPLATES = {
    "KYC_001": (
        And(action_var == 2, account_type_var == 0),
        amount_var <= 10000,
        "Single transfer amount ₹{amount:,} exceeds Small Account limit of ₹10,000."
    ),
    "KYC_002": (
        And(action_var == 2, account_type_var == 0),
        annual_credit_var + amount_var <= 100000,
        "Small Account annual credits limit of ₹1,00,000 would be exceeded."
    ),
    "KYC_003": (
        And(action_var == 2, account_type_var == 0),
        current_balance_var + amount_var <= 50000,
        "Small Account maximum balance cap of ₹50,000 would be exceeded."
    ),
    "KYC_004": (
        amount_var > 50000,
        kyc_status_var == 2,
        "Full KYC (Aadhaar + PAN) is mandatory for transactions or loans exceeding ₹50,000."
    ),
    "LOAN_001": (
        And(action_var == 1, loan_type_var == 1, Not(has_collateral_var)),
        amount_var <= 1000000,
        "Unsecured personal loan amount ₹{amount:,} exceeds legal limit of ₹10,00,000 without collateral."
    ),
    "LOAN_002": (
        And(action_var == 1, amount_var >= 2500000, amount_var < 10000000),
        And(has_itr_var, itr_years_var >= 2, Or(cibil_score_var == 0, cibil_score_var >= 700)),
        "Loans above ₹25,00,000 require at least 2 years of ITR and a minimum CIBIL score of 700."
    ),
    "LOAN_003": (
        And(action_var == 1, amount_var >= 10000000),
        And(kyc_status_var == 2, has_itr_var, itr_years_var >= 3, Or(cibil_score_var == 0, cibil_score_var >= 750), has_collateral_var),
        "Loans of ₹1 Crore+ require Full KYC, ITR for 3 years, CIBIL score ≥ 750, and collateral security."
    ),
    "DL_001": (
        action_var == 3,
        has_kfs_var,
        "Key Fact Statement (KFS) must be explicitly provided and acknowledged for digital loans."
    ),
    "DL_003": (
        action_var == 3,
        disburse_to_var == 1,
        "Digital loan disbursals directly to prepaid wallets or third-party accounts are prohibited."
    ),
    "DL_004": (
        And(action_var == 3, dlg_percentage_var > 0.0),
        dlg_percentage_var <= 5.0,
        "Default Loss Guarantee (DLG) in digital lending cannot exceed the 5% regulatory portfolio cap."
    ),
    "CC_002": (
        action_var == 4,
        Or(annual_income_var == 0, annual_income_var >= 300000),
        "Credit card issuance requires a minimum annual net income of ₹3,00,000."
    ),
    "CC_004": (
        action_var == 5,
        reporting_days_var <= 7,
        "Credit card dispute reported after 7 days; full cardholder liability applies per RBI directions."
    )
}


def verify(facts: dict[str, Any]) -> dict[str, Any]:
    """
    Formally verifies extracted facts against mapped RBI symbolic constraints.
    Returns SAT/UNSAT verdict, violated rules, triggered rules, and checklists.
    """
    # 1. Resolve raw fact strings into Z3-compatible enum indices
    actual_action = facts.get("action", "loan")
    actual_amount = facts.get("amount", 0.0)
    actual_kyc = facts.get("kyc_status", "unknown")
    actual_loan_type = facts.get("loan_type", "personal")
    actual_disburse = facts.get("disburse_to", "bank_account")
    actual_account = facts.get("account_type", "full_kyc")

    # 2. Build the Solver Context and Assert Ground Truth Facts
    s = Solver()
    s.add(amount_var == int(actual_amount))
    s.add(kyc_status_var == KYC_MAP.get(actual_kyc, 1))
    s.add(loan_type_var == LOAN_MAP.get(actual_loan_type, 1))
    s.add(has_itr_var == bool(facts.get("has_itr", False)))
    s.add(itr_years_var == int(facts.get("itr_years", 0)))
    s.add(has_collateral_var == bool(facts.get("has_collateral", False)))
    s.add(has_audited_financials_var == bool(facts.get("has_audited_financials", False)))
    s.add(cibil_score_var == int(facts.get("cibil_score", 0)))
    s.add(annual_income_var == int(facts.get("annual_income", 0)))
    s.add(annual_credit_var == int(facts.get("annual_credit", 0)))
    s.add(current_balance_var == int(facts.get("current_balance", 0)))
    s.add(has_kfs_var == bool(facts.get("has_kfs", False)))
    s.add(dlg_percentage_var == float(facts.get("dlg_percentage", 0.0)))
    s.add(disburse_to_var == DISBURSE_MAP.get(actual_disburse, 1))
    s.add(reporting_days_var == int(facts.get("reporting_days", 0)))
    s.add(account_type_var == ACCOUNT_MAP.get(actual_account, 1))
    s.add(action_var == ACTION_MAP.get(actual_action, 1))

    # 3. Formulate rules logic list from templates
    rules_logic = {}
    for rule_id, (applies, complies, err_tmpl) in RULES_LOGIC_TEMPLATES.items():
        err_msg = err_tmpl.format(amount=int(actual_amount))
        rules_logic[rule_id] = (applies, complies, err_msg)

    violations = []
    triggered_ids = []
    required_docs = []
    required_criteria = []

    # 4. Perform Z3 Symbolic SMT Checking
    for rule_id, (applies, complies, error_msg) in rules_logic.items():
        # Check if the rule is applicable to current facts
        s.push()
        s.add(applies)
        is_applicable = (s.check() == sat)
        s.pop()

        if is_applicable:
            triggered_ids.append(rule_id)
            
            # Fetch rule documents & criteria metadata from rules.py
            rule_ref = RULE_REGISTRY.get(rule_id)
            if rule_ref:
                for doc in rule_ref.parameters.get("required_docs", []):
                    if doc not in required_docs:
                        required_docs.append(doc)
                for crit in rule_ref.parameters.get("required_criteria", []):
                    if crit not in required_criteria:
                        required_criteria.append(crit)

            # Test if the compliance condition is violated (i.e. Not(complies) is satisfiable under current facts)
            s.push()
            s.add(Not(complies))
            is_violated = (s.check() == sat)
            s.pop()

            if is_violated:
                violations.append(error_msg)

    # 5. Determine SAT/UNSAT Verdict
    verdict = "SAT" if not violations else "UNSAT"

    # Deduplicate checklists
    required_docs = list(dict.fromkeys(required_docs))
    required_criteria = list(dict.fromkeys(required_criteria))

    # Pull metadata for all triggered rules
    triggered_rules_metadata = []
    for r_id in triggered_ids:
        r_ref = RULE_REGISTRY.get(r_id)
        if r_ref:
            triggered_rules_metadata.append({
                "rule_id": r_ref.rule_id,
                "title": r_ref.title,
                "source": r_ref.source_document,
                "category": r_ref.category
            })

    return {
        "verdict": verdict,
        "violations": violations,
        "required_documents": required_docs,
        "required_criteria": required_criteria,
        "triggered_rules": triggered_rules_metadata
    }


def generate_counterfactual_via_z3(facts: dict[str, Any]) -> str:
    """
    Formulates a Max-SMT optimization problem using Z3 to find the closest
    compliant state, generating dynamic recommendations for rejected transactions.
    """
    actual_action = facts.get("action", "loan")
    actual_amount = facts.get("amount", 0.0)
    actual_kyc = facts.get("kyc_status", "unknown")
    actual_loan_type = facts.get("loan_type", "personal")
    actual_disburse = facts.get("disburse_to", "bank_account")
    actual_account = facts.get("account_type", "full_kyc")

    opt = Optimize()

    # 1. Assert all applicable regulatory rules as hard constraints
    for r_id, (applies, complies, _) in RULES_LOGIC_TEMPLATES.items():
        opt.add(Implies(applies, complies))

    # Domain constraints
    opt.add(amount_var >= 0)
    opt.add(kyc_status_var >= 0, kyc_status_var <= 2)
    opt.add(itr_years_var >= 0)
    opt.add(cibil_score_var >= 0)
    opt.add(disburse_to_var >= 1, disburse_to_var <= 3)
    opt.add(reporting_days_var >= 0)
    opt.add(account_type_var >= 0, account_type_var <= 1)
    
    action_idx = ACTION_MAP.get(actual_action, 1)
    opt.add(action_var == action_idx)

    # 2. Add soft constraints representing the user's current facts
    current_kyc_idx = KYC_MAP.get(actual_kyc, 1)
    current_loan_type_idx = LOAN_MAP.get(actual_loan_type, 1)
    current_disburse_idx = DISBURSE_MAP.get(actual_disburse, 1)
    current_account_idx = ACCOUNT_MAP.get(actual_account, 1)

    opt.add_soft(kyc_status_var == current_kyc_idx, 10)
    opt.add_soft(has_itr_var == bool(facts.get("has_itr", False)), 10)
    opt.add_soft(itr_years_var == int(facts.get("itr_years", 0)), 10)
    opt.add_soft(has_collateral_var == bool(facts.get("has_collateral", False)), 10)
    opt.add_soft(cibil_score_var == int(facts.get("cibil_score", 0)), 5)
    opt.add_soft(annual_income_var == int(facts.get("annual_income", 0)), 5)
    opt.add_soft(annual_credit_var == int(facts.get("annual_credit", 0)), 5)
    opt.add_soft(current_balance_var == int(facts.get("current_balance", 0)), 5)
    opt.add_soft(has_kfs_var == bool(facts.get("has_kfs", False)), 10)
    opt.add_soft(dlg_percentage_var == float(facts.get("dlg_percentage", 0.0)), 10)
    opt.add_soft(disburse_to_var == current_disburse_idx, 10)
    opt.add_soft(reporting_days_var == int(facts.get("reporting_days", 0)), 10)
    opt.add_soft(account_type_var == current_account_idx, 10)

    # 3. Handle optimization scenarios
    # Scenario A: Try hard-asserting the requested amount to see what user profile changes can enable it.
    opt.push()
    opt.add(amount_var == int(actual_amount))
    
    recommendations = []
    
    if opt.check() == sat:
        m = opt.model()
        
        # Check KYC
        opt_kyc = m[kyc_status_var].as_long() if m[kyc_status_var] is not None else current_kyc_idx
        if opt_kyc > current_kyc_idx:
            kyc_name = [k for k, v in KYC_MAP.items() if v == opt_kyc][0]
            recommendations.append(f"Complete {kyc_name.capitalize()} KYC")
        
        # Check ITR
        opt_has_itr = is_true(m[has_itr_var]) if m[has_itr_var] is not None else bool(facts.get("has_itr", False))
        opt_itr_years = m[itr_years_var].as_long() if m[itr_years_var] is not None else int(facts.get("itr_years", 0))
        if opt_has_itr and not facts.get("has_itr", False):
            recommendations.append("Submit Income Tax Returns (ITR)")
        if opt_itr_years > int(facts.get("itr_years", 0)):
            recommendations.append(f"Submit ITR for the last {opt_itr_years} financial years")
            
        # Check Collateral
        opt_has_col = is_true(m[has_collateral_var]) if m[has_collateral_var] is not None else bool(facts.get("has_collateral", False))
        if opt_has_col and not facts.get("has_collateral", False):
            recommendations.append("Provide legally cleared collateral security")
            
        # Check CIBIL
        opt_cibil = m[cibil_score_var].as_long() if m[cibil_score_var] is not None else int(facts.get("cibil_score", 0))
        if opt_cibil > int(facts.get("cibil_score", 0)) and int(facts.get("cibil_score", 0)) > 0:
            recommendations.append(f"Maintain a CIBIL score ≥ {opt_cibil}")

        # Check KFS (Digital Loan)
        opt_kfs = is_true(m[has_kfs_var]) if m[has_kfs_var] is not None else bool(facts.get("has_kfs", False))
        if opt_kfs and not facts.get("has_kfs", False):
            recommendations.append("Review and acknowledge the Key Fact Statement (KFS)")

        # Check Disbursal target (Digital Loan)
        opt_disburse = m[disburse_to_var].as_long() if m[disburse_to_var] is not None else current_disburse_idx
        if opt_disburse != current_disburse_idx:
            disburse_name = [k for k, v in DISBURSE_MAP.items() if v == opt_disburse][0]
            recommendations.append(f"Ensure disbursal is set to a {disburse_name.replace('_', ' ')}")

        # Check DLG (Digital Loan)
        opt_dlg = m[dlg_percentage_var]
        if opt_dlg is not None:
            try:
                opt_dlg_val = float(opt_dlg.numerator_as_long() / opt_dlg.denominator_as_long())
            except:
                opt_dlg_val = 0.0
            if opt_dlg_val < float(facts.get("dlg_percentage", 0.0)):
                recommendations.append(f"Cap Default Loss Guarantee (DLG) percentage under {opt_dlg_val}%")

        # Check account type (KYC transfer limits)
        opt_acc = m[account_type_var].as_long() if m[account_type_var] is not None else current_account_idx
        if opt_acc > current_account_idx:
            recommendations.append("Upgrade your account to a Full KYC Account")

        opt.pop()
    else:
        # Scenario B: Hard limit bounds exceeded (even with profile changes, amount is too high).
        # Pop requested amount and maximize it to find the threshold cap.
        opt.pop()
        opt.maximize(amount_var)
        
        if opt.check() == sat:
            m = opt.model()
            max_amount = m[amount_var].as_long() if m[amount_var] is not None else 0
            if max_amount > 0:
                recommendations.append(f"Reduce transaction/loan amount below ₹{max_amount:,}")
            
            # Check if any profile changes are required even at the reduced max amount
            opt_kyc = m[kyc_status_var].as_long() if m[kyc_status_var] is not None else current_kyc_idx
            if opt_kyc > current_kyc_idx:
                kyc_name = [k for k, v in KYC_MAP.items() if v == opt_kyc][0]
                recommendations.append(f"Complete {kyc_name.capitalize()} KYC")
                
            opt_has_col = is_true(m[has_collateral_var]) if m[has_collateral_var] is not None else bool(facts.get("has_collateral", False))
            if opt_has_col and not facts.get("has_collateral", False):
                recommendations.append("Provide legally cleared collateral security")
                
            opt_acc = m[account_type_var].as_long() if m[account_type_var] is not None else current_account_idx
            if opt_acc > current_account_idx:
                recommendations.append("Upgrade your account to a Full KYC Account")
                
            opt_days = m[reporting_days_var].as_long() if m[reporting_days_var] is not None else 0
            if opt_days < int(facts.get("reporting_days", 0)):
                recommendations.append(f"Report the unauthorized charge within {opt_days} days of occurrence")

    if not recommendations:
        return "Ensure standard identification papers (PAN + Aadhaar) are submitted."
        
    return "To satisfy compliance: " + ", ".join(recommendations) + "."
