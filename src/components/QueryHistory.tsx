import { Clock } from 'lucide-react';
import type { VerificationResult } from '../lib/verifier';
import { VerdictBadge } from './VerdictBadge';

interface HistoryEntry {
  id: string;
  query: string;
  result: VerificationResult;
  timestamp: Date;
}

interface Props {
  history: HistoryEntry[];
  onSelect: (entry: HistoryEntry) => void;
  selectedId: string | null;
}

export function QueryHistory({ history, onSelect, selectedId }: Props) {
  if (!history.length) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 px-1">
        <Clock className="w-3.5 h-3.5 text-slate-400" />
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Query History</span>
      </div>
      {history.map(entry => (
        <button
          key={entry.id}
          onClick={() => onSelect(entry)}
          className={`w-full text-left rounded-xl border p-3 transition-all ${
            selectedId === entry.id
              ? 'border-blue-300 bg-blue-50 shadow-sm'
              : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm'
          }`}
        >
          <div className="flex items-start justify-between gap-2 mb-1">
            <p className="text-xs text-slate-700 line-clamp-2 flex-1">{entry.query}</p>
            <VerdictBadge verdict={entry.result.verdict} />
          </div>
          <p className="text-xs text-slate-400">{entry.timestamp.toLocaleTimeString()}</p>
        </button>
      ))}
    </div>
  );
}

export type { HistoryEntry };
