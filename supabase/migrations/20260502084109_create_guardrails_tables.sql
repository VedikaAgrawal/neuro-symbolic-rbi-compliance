/*
  # Hybrid Neuro-Symbolic Guardrails - Database Schema

  1. New Tables
    - `query_logs` - Stores all user queries and their verification results
      - `id` (uuid, primary key)
      - `user_query` (text) - Original user question
      - `extracted_facts` (jsonb) - LLM-extracted entities/facts
      - `verdict` (text) - SAT or UNSAT
      - `rules_triggered` (jsonb) - Which RBI rules were evaluated
      - `required_documents` (jsonb) - Documents user needs to fulfill
      - `required_criteria` (jsonb) - Criteria user needs to meet
      - `explanation` (text) - Natural language explanation
      - `counterfactual` (text) - What would make it SAT
      - `created_at` (timestamptz)

    - `rbi_rules` - Stores the RBI regulatory rules
      - `id` (uuid, primary key)
      - `rule_id` (text, unique) - Short identifier
      - `category` (text) - KYC, Digital Lending, Loans, etc.
      - `title` (text)
      - `description` (text)
      - `source_document` (text)
      - `constraint_type` (text) - hard_limit, conditional, document_required
      - `parameters` (jsonb) - Numeric thresholds etc.
      - `created_at` (timestamptz)

  2. Security
    - Enable RLS on all tables
    - Allow public read for rbi_rules (reference data)
    - Allow public insert/select for query_logs (no auth required for demo)
*/

CREATE TABLE IF NOT EXISTS rbi_rules (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_id text UNIQUE NOT NULL,
  category text NOT NULL DEFAULT '',
  title text NOT NULL DEFAULT '',
  description text NOT NULL DEFAULT '',
  source_document text NOT NULL DEFAULT '',
  constraint_type text NOT NULL DEFAULT 'hard_limit',
  parameters jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE rbi_rules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read rbi rules"
  ON rbi_rules FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE TABLE IF NOT EXISTS query_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_query text NOT NULL DEFAULT '',
  extracted_facts jsonb DEFAULT '{}',
  verdict text NOT NULL DEFAULT 'UNKNOWN',
  rules_triggered jsonb DEFAULT '[]',
  required_documents jsonb DEFAULT '[]',
  required_criteria jsonb DEFAULT '[]',
  explanation text DEFAULT '',
  counterfactual text DEFAULT '',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can insert query logs"
  ON query_logs FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Anyone can read query logs"
  ON query_logs FOR SELECT
  TO anon, authenticated
  USING (true);
