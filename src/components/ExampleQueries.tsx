interface Props {
  onSelect: (query: string) => void;
}

const EXAMPLES = [
  {
    label: 'Crore Loan',
    query: 'I want a loan of 1 crore.',
    category: 'Loans',
  },
  {
    label: 'OTP Transfer',
    query: 'I want to transfer ₹60,000 using my OTP-verified account.',
    category: 'KYC',
  },
  {
    label: 'Digital Loan',
    query: 'I want to apply for a ₹2 lakh loan through a fintech app without KFS.',
    category: 'Digital Lending',
  },
  {
    label: 'Credit Card',
    query: 'I want to apply for a credit card with an annual income of ₹1,80,000.',
    category: 'Credit Cards',
  },
  {
    label: 'Business Loan',
    query: 'I need a business loan of ₹50 lakh for my MSME.',
    category: 'Loans',
  },
  {
    label: 'Home Loan',
    query: 'I want a home loan of ₹75 lakh with collateral and ITR for 2 years.',
    category: 'Loans',
  },
];

const categoryColors: Record<string, string> = {
  Loans: 'bg-blue-950/40 text-blue-300 border border-blue-800/30',
  KYC: 'bg-teal-950/40 text-teal-300 border border-teal-800/30',
  'Digital Lending': 'bg-amber-950/40 text-amber-300 border border-amber-800/30',
  'Credit Cards': 'bg-rose-950/40 text-rose-300 border border-rose-800/30',
};

export function ExampleQueries({ onSelect }: Props) {
  return (
    <div>
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3 px-1">Try an Example</p>
      <div className="grid grid-cols-2 gap-2">
        {EXAMPLES.map(ex => (
          <button
            key={ex.label}
            onClick={() => onSelect(ex.query)}
            className="text-left p-3 rounded-xl border border-white/5 bg-slate-900/40 hover:bg-slate-900/80 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-950/20 transition-all group"
          >
            <div className="flex items-center gap-1.5 mb-1.5">
              <span className={`text-xs font-medium px-1.5 py-0.5 rounded-full border ${categoryColors[ex.category]}`}>
                {ex.category}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-snug group-hover:text-slate-200 transition-colors line-clamp-2">
              {ex.query}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
