import { Cpu } from 'lucide-react';
import type { ExtractedFacts } from '../lib/verifier';

interface Props {
  facts: ExtractedFacts;
}

function Fact({ label, value }: { label: string; value: string | number | boolean }) {
  const display = typeof value === 'boolean' ? (
    value ? (
      <span className="text-emerald-400 font-semibold">Yes</span>
    ) : (
      <span className="text-slate-500">No</span>
    )
  ) : typeof value === 'number' && label === 'Amount' ? (
    <span className="font-mono text-white/95">₹{value.toLocaleString('en-IN')}</span>
  ) : (
    <span className="font-mono text-white/95">{String(value) || '—'}</span>
  );

  return (
    <div className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-xs">{display}</span>
    </div>
  );
}

export function FactsPanel({ facts }: Props) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-900/60 backdrop-blur-md overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 bg-slate-950/40 border-b border-white/5">
        <Cpu className="w-4 h-4 text-slate-400 animate-pulse" />
        <span className="text-xs font-semibold text-white/80 uppercase tracking-wide">Extracted Facts (Neural Layer)</span>
      </div>
      <div className="px-4 py-2">
        <Fact label="Action" value={facts.action} />
        <Fact label="Amount" value={facts.amount} />
        <Fact label="KYC Status" value={facts.kyc_status} />
        <Fact label="Loan Type" value={facts.loan_type} />
        <Fact label="Account Type" value={facts.account_type} />
        <Fact label="Has ITR" value={facts.has_itr} />
        <Fact label="ITR Years" value={facts.itr_years} />
        <Fact label="Has Collateral" value={facts.has_collateral} />
        <Fact label="CIBIL Score" value={facts.cibil_score || '—'} />
        <Fact label="Annual Income" value={facts.annual_income ? `₹${facts.annual_income.toLocaleString('en-IN')}` : '—'} />
      </div>
    </div>
  );
}
