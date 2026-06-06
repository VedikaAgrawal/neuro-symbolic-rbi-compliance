/**
 * Client-side verification module.
 * Makes asynchronous API calls to the FastAPI backend to perform
 * real-time neuro-symbolic compliance checks.
 */

export interface ExtractedFacts {
  action: string;
  amount: number;
  kyc_status: string;
  loan_type: string;
  has_itr: boolean;
  itr_years: number;
  has_collateral: boolean;
  has_audited_financials: boolean;
  cibil_score: number;
  annual_income: number;
  account_type: string;
  has_kfs: boolean;
  dlg_percentage: number;
  disburse_to: string;
  reporting_days: number;
}

export interface TriggeredRule {
  rule_id: string;
  title: string;
  source: string;
  category: string;
}

export interface VerificationResult {
  verdict: 'SAT' | 'UNSAT' | 'PENDING';
  explanation: string;
  extracted_facts: ExtractedFacts;
  violations: string[];
  required_documents: string[];
  required_criteria: string[];
  triggered_rules: TriggeredRule[];
  counterfactual: string;
}

/**
 * Calls the FastAPI backend verification endpoint.
 */
export async function verifyQuery(queryText: string): Promise<VerificationResult> {
  const apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const response = await fetch(`${apiBaseUrl}/verify`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: queryText }),
  });

  if (!response.ok) {
    throw new Error("Unable to reach the compliance verification server. Please ensure the backend is running.");
  }

  return response.json();
}
