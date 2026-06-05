import { CheckCircle, XCircle, Clock } from 'lucide-react';

interface Props {
  verdict: 'SAT' | 'UNSAT' | 'PENDING';
  size?: 'sm' | 'lg';
}

export function VerdictBadge({ verdict, size = 'sm' }: Props) {
  if (verdict === 'SAT') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 ${size === 'lg' ? 'text-base px-4 py-2' : 'text-xs px-2.5 py-1'}`}>
        <CheckCircle className={size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />
        SAT — Compliant
      </span>
    );
  }
  if (verdict === 'UNSAT') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-red-50 text-red-700 border border-red-200 ${size === 'lg' ? 'text-base px-4 py-2' : 'text-xs px-2.5 py-1'}`}>
        <XCircle className={size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />
        UNSAT — Violation
      </span>
    );
  }
  return (
    <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-slate-100 text-slate-500 border border-slate-200 ${size === 'lg' ? 'text-base px-4 py-2' : 'text-xs px-2.5 py-1'}`}>
      <Clock className={size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />
      Pending
    </span>
  );
}
