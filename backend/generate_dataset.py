"""
Synthetic Compliance Query Generator
Generates 100 distinct queries across all five RBI regulatory domains,
uses Z3 to compute expected verdicts, and saves the dataset to dataset/evaluation_dataset.json.
"""

import os
import json
import sys
import random

# Ensure parent directory is in sys.path for backend imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.solver import verify

def generate_100_queries():
    random.seed(42)  # For deterministic output
    queries = []
    
    # 1. Templates for Transfers & KYC Cap Rules (KYC_001, KYC_002, KYC_003, KYC_004)
    transfer_templates = [
        # (Template text, parameters)
        ("I want to transfer ₹{amount} using my {account_type} account.", {"action": "transfer", "amount": 0.0, "account_type": ""}),
        ("Please send ₹{amount} from my {account_type} account.", {"action": "transfer", "amount": 0.0, "account_type": ""}),
        ("Initiate a fund transfer of ₹{amount} from an {account_type} account.", {"action": "transfer", "amount": 0.0, "account_type": ""}),
        ("I need to pay a vendor ₹{amount} from my {account_type} balance.", {"action": "transfer", "amount": 0.0, "account_type": ""}),
        ("Can I transfer ₹{amount} with a {kyc_status} KYC level?", {"action": "transfer", "amount": 0.0, "kyc_status": ""}),
    ]

    # Generate 25 Transfer queries
    amounts = [5000, 9500, 12000, 25000, 48000, 55000, 120000]
    acc_types = ["small", "otp_only", "full_kyc"]
    kyc_statuses = ["limited", "none", "full"]
    
    for i in range(25):
        tmpl = random.choice(transfer_templates)
        amount = random.choice(amounts)
        acc_type = random.choice(acc_types)
        kyc_status = "full" if acc_type == "full_kyc" else ("limited" if acc_type == "otp_only" else "none")
        
        # Populate text
        q_text = tmpl[0].format(amount=f"{amount:,}", account_type=acc_type.replace('_', '/'), kyc_status=kyc_status)
        
        # Populate facts
        facts = {
            "action": "transfer",
            "amount": float(amount),
            "kyc_status": kyc_status,
            "account_type": acc_type,
            "annual_credit": float(random.choice([0, 15000, 80000, 95000])),
            "current_balance": float(random.choice([500, 10000, 45000, 49000]))
        }
        queries.append((q_text, facts))

    # 2. Templates for Standard Loans & Advances (LOAN_001, LOAN_002, LOAN_003)
    loan_templates = [
        ("I want to apply for a {loan_type} loan of ₹{amount}.", {"action": "loan", "loan_type": "", "amount": 0.0}),
        ("I need a {loan_type} loan of ₹{amount}. I have {kyc} KYC, a CIBIL of {cibil}, and {collateral}.", {"action": "loan", "loan_type": "", "amount": 0.0}),
        ("Requesting a {loan_type} loan of ₹{amount}. Collateral: {collateral}. ITR status: {itr} years.", {"action": "loan", "loan_type": "", "amount": 0.0}),
        ("Applying for a ₹{amount} {loan_type} loan. I have {collateral} and CIBIL of {cibil}.", {"action": "loan", "loan_type": "", "amount": 0.0}),
    ]

    # Generate 35 Loan queries
    loan_types = ["personal", "home", "business", "vehicle", "education"]
    loan_amounts = [500000, 800000, 1200000, 2400000, 3500000, 4500000, 12000000, 15000000]
    cibil_scores = [0, 600, 680, 720, 760]
    itr_options = [(False, 0), (True, 2), (True, 3)]
    collateral_options = [True, False]
    
    for i in range(35):
        tmpl = random.choice(loan_templates)
        l_type = random.choice(loan_types)
        amount = random.choice(loan_amounts)
        cibil = random.choice(cibil_scores)
        has_itr, itr_years = random.choice(itr_options)
        has_col = random.choice(collateral_options)
        kyc = random.choice(["full", "limited", "none"])
        
        col_text = "with property collateral" if has_col else "without collateral"
        itr_text = f"ITR filed for {itr_years} years" if has_itr else "no ITR records"
        
        q_text = tmpl[0].format(
            loan_type=l_type,
            amount=f"{amount:,}",
            kyc=kyc,
            cibil=cibil if cibil > 0 else "unknown",
            collateral=col_text,
            itr=itr_text
        )
        
        facts = {
            "action": "loan",
            "amount": float(amount),
            "kyc_status": kyc,
            "loan_type": l_type,
            "has_itr": has_itr,
            "itr_years": itr_years,
            "has_collateral": has_col,
            "cibil_score": cibil,
            "annual_income": float(amount * 0.3)
        }
        queries.append((q_text, facts))

    # 3. Templates for Digital Lending (DL_001, DL_003, DL_004)
    dl_templates = [
        ("I want a digital loan of ₹{amount} from a fintech app. I acknowledge {kfs} and disburse to {disburse}.", {"action": "digital_loan", "amount": 0.0}),
        ("Applying for an online app loan of ₹{amount}. Geolocation captured, KFS: {kfs}. Disbursal target: {disburse}.", {"action": "digital_loan", "amount": 0.0}),
        ("Initiate a digital credit of ₹{amount}. Disbursal: {disburse}. DLG rate: {dlg}%.", {"action": "digital_loan", "amount": 0.0}),
        ("Can I get an online personal loan of ₹{amount} to my {disburse}?", {"action": "digital_loan", "amount": 0.0}),
    ]

    # Generate 20 Digital Lending queries
    dl_amounts = [15000, 45000, 75000, 150000]
    disburse_targets = ["bank_account", "wallet", "third_party_account"]
    dlgs = [0.0, 4.0, 5.0, 7.5]
    
    for i in range(20):
        tmpl = random.choice(dl_templates)
        amount = random.choice(dl_amounts)
        disburse = random.choice(disburse_targets)
        dlg = random.choice(dlgs)
        has_kfs = random.choice([True, False])
        
        kfs_text = "Key Fact Statement" if has_kfs else "no document disclosures"
        
        q_text = tmpl[0].format(
            amount=f"{amount:,}",
            kfs=kfs_text,
            disburse=disburse.replace('_', ' '),
            dlg=dlg
        )
        
        facts = {
            "action": "digital_loan",
            "amount": float(amount),
            "kyc_status": "full",
            "has_kfs": has_kfs,
            "disburse_to": disburse,
            "dlg_percentage": dlg
        }
        queries.append((q_text, facts))

    # 4. Templates for Credit Cards (CC_001, CC_002, CC_003, CC_004)
    cc_templates = [
        ("Apply for a credit card. My net annual income is ₹{income}.", {"action": "credit_card_apply"}),
        ("I want to apply for credit card. Income: ₹{income}. No defaults.", {"action": "credit_card_apply"}),
        ("Disputing an unauthorized charge of ₹{amount} on my credit card reported {days} days after the incident.", {"action": "dispute_unauthorized"}),
        ("Report fraudulent transaction on my credit card that happened {days} days ago.", {"action": "dispute_unauthorized"}),
    ]

    # Generate 20 Credit Card queries
    incomes = [180000, 280000, 320000, 500000]
    dispute_amounts = [2000, 8500, 15000]
    days_elapsed = [2, 5, 8, 12]
    
    for i in range(20):
        tmpl = random.choice(cc_templates)
        income = random.choice(incomes)
        amount = random.choice(dispute_amounts)
        days = random.choice(days_elapsed)
        
        if "apply" in tmpl[0].lower():
            q_text = tmpl[0].format(income=f"{income:,}")
            facts = {
                "action": "credit_card_apply",
                "amount": 0.0,
                "annual_income": float(income)
            }
        else:
            q_text = tmpl[0].format(amount=f"{amount:,}", days=days)
            facts = {
                "action": "dispute_unauthorized",
                "amount": float(amount),
                "reporting_days": days
            }
        queries.append((q_text, facts))

    # Shuffle to mix rule categories
    random.shuffle(queries)

    # 5. Format results and run Z3 solver to generate expected verdicts
    final_dataset = []
    for idx, (q_text, facts) in enumerate(queries[:100]):
        # Call verify to get true expected verdict and violations
        res = verify(facts)
        
        final_dataset.append({
            "id": idx + 1,
            "query": q_text,
            "ground_truth": facts,
            "expected_verdict": res["verdict"],
            "expected_violations": res["violations"]
        })

    # Save to JSON file
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "dataset", "evaluation_dataset.json"
    )
    with open(output_path, "w") as f:
        json.dump(final_dataset, f, indent=2)
        
    print(f"🎉 SUCCESS: Generated 100 queries and saved to {output_path}!")

if __name__ == "__main__":
    generate_100_queries()
