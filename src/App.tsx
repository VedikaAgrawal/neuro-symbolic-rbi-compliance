import { useState, useRef } from 'react';
import { Scale, Send, Shield, BookOpen, Zap, ChevronRight, Activity } from 'lucide-react';
import { verifyQuery, type VerificationResult } from './lib/verifier';
import { VerificationResultCard } from './components/VerificationResult';
import { FactsPanel } from './components/FactsPanel';
import { QueryHistory, type HistoryEntry } from './components/QueryHistory';
import { ExampleQueries } from './components/ExampleQueries';

function FileIcon() {
  return (
    <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  async function handleVerify(queryText = query) {
    if (!queryText.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await verifyQuery(queryText);

      const entry: HistoryEntry = {
        id: crypto.randomUUID(),
        query: queryText,
        result: res,
        timestamp: new Date(),
      };

      setResult(res);
      setSelectedId(entry.id);
      setHistory(prev => [entry, ...prev.slice(0, 9)]);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to verify compliance. Ensure the FastAPI backend is running.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  function handleSelect(entry: HistoryEntry) {
    setSelectedId(entry.id);
    setResult(entry.result);
    setQuery(entry.query);
  }

  function handleExample(q: string) {
    setQuery(q);
    handleVerify(q);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleVerify();
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 flex flex-col">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-10 bg-slate-950/80">
        <div className="max-w-screen-xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-blue-600 shadow-lg shadow-blue-900/40">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-white font-bold text-lg leading-none">RBI Compliance Verifier</h1>
              <p className="text-slate-400 text-xs mt-0.5">AI-Powered Neuro-Symbolic Guardrails · Z3 SMT Solver</p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-4 text-xs text-slate-400">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Z3 SMT Solver Active
            </div>
            <div className="flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5" />
              RBI Regulations 2025
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-screen-xl mx-auto w-full px-4 sm:px-6 py-6 grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
        {/* Left Sidebar */}
        <aside className="flex flex-col gap-5">
          {/* Architecture */}
          <div className="rounded-2xl bg-white/5 border border-white/10 p-4 space-y-3">
            <p className="text-white/60 text-xs font-semibold uppercase tracking-wider">Pipeline Architecture</p>
            {[
              { icon: <Zap className="w-3.5 h-3.5" />, label: 'Neural Perception', desc: 'Entity & intent extraction from NL query', color: 'text-blue-400 bg-blue-500/20' },
              { icon: <ChevronRight className="w-3.5 h-3.5" />, label: 'Auto-Formalization', desc: 'JSON facts injected into Z3 context', color: 'text-teal-400 bg-teal-500/20' },
              { icon: <Activity className="w-3.5 h-3.5" />, label: 'SMT Verification', desc: 'Deterministic SAT / UNSAT verdict', color: 'text-amber-400 bg-amber-500/20' },
              { icon: <BookOpen className="w-3.5 h-3.5" />, label: 'Max-SMT Feedback', desc: 'Counterfactual + doc checklist generation', color: 'text-rose-400 bg-rose-500/20' },
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <div className={`mt-0.5 p-1.5 rounded-lg ${item.color}`}>{item.icon}</div>
                <div>
                  <p className="text-white/90 text-xs font-medium">{item.label}</p>
                  <p className="text-white/40 text-xs leading-snug">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Regulation Coverage */}
          <div className="rounded-2xl bg-white/5 border border-white/10 p-4">
            <p className="text-white/60 text-xs font-semibold uppercase tracking-wider mb-3">RBI Regulation Coverage</p>
            <div className="space-y-2">
              {[
                { label: 'KYC Direction 2016 (Aug 2025)', rules: 6, color: 'bg-teal-500' },
                { label: 'Loans & Advances Circular', rules: 5, color: 'bg-blue-500' },
                { label: 'Digital Lending Directions 2025', rules: 6, color: 'bg-amber-500' },
                { label: 'Credit & Debit Card Directions 2022', rules: 4, color: 'bg-rose-500' },
                { label: 'Priority Sector Lending 2019', rules: 1, color: 'bg-slate-400' },
              ].map((reg, i) => (
                <div key={i}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-white/50 text-xs truncate pr-2">{reg.label}</span>
                    <span className="text-white/40 text-xs font-mono shrink-0">{reg.rules}</span>
                  </div>
                  <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${reg.color}`} style={{ width: `${(reg.rules / 6) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Query History */}
          {history.length > 0 && (
            <QueryHistory history={history} onSelect={handleSelect} selectedId={selectedId} />
          )}
        </aside>

        {/* Main Panel */}
        <div className="flex flex-col gap-5 min-h-0">
          {/* Input Card */}
          <div className="rounded-2xl bg-slate-900/60 border border-white/10 backdrop-blur-md shadow-2xl overflow-hidden">
            <div className="px-5 py-4 border-b border-white/5 bg-slate-950/40">
              <h2 className="text-white font-bold text-base">Financial Compliance Query</h2>
              <p className="text-slate-400 text-xs mt-1 leading-relaxed">
                Describe your financial request in plain English. The system extracts facts and verifies against all applicable RBI rules.
              </p>
            </div>
            <div className="p-4">
              <textarea
                ref={textareaRef}
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="e.g. I want a loan of 1 crore for my business…"
                rows={3}
                className="w-full resize-none text-white placeholder-slate-500 text-sm leading-relaxed focus:outline-none bg-transparent"
              />
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/5">
                <p className="text-xs text-slate-500 hidden sm:block">Enter to verify · Shift+Enter for newline</p>
                <button
                  onClick={() => handleVerify()}
                  disabled={loading || !query.trim()}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-600/25 ml-auto"
                >
                  {loading ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Verifying…
                    </>
                  ) : (
                    <>
                      <Scale className="w-4 h-4" />
                      Verify Compliance
                      <Send className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="rounded-2xl bg-rose-50 border border-rose-200 p-5 text-sm text-rose-700 shadow-sm animate-fade-in space-y-2">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-rose-600" />
                <span className="font-bold text-rose-800">Connection Failure</span>
              </div>
              <p className="mt-1 text-xs text-rose-600 leading-relaxed">
                {error}
              </p>
              <p className="text-xs text-rose-500 pt-1 font-mono">
                Troubleshoot: Verify the FastAPI server is listening at http://localhost:8000
              </p>
            </div>
          )}

          {/* Results or Landing */}
          {!result ? (
            <div className="rounded-2xl bg-slate-900/60 border border-white/10 backdrop-blur-md shadow-2xl p-5 space-y-6">
              <ExampleQueries onSelect={handleExample} />

              <div className="pt-5 border-t border-white/5 grid grid-cols-1 sm:grid-cols-3 gap-4">
                {[
                  {
                    icon: <Scale className="w-5 h-5 text-blue-400" />,
                    title: 'SAT / UNSAT Verdict',
                    desc: 'Deterministic Z3 SMT result — mathematically provable, zero hallucination.',
                  },
                  {
                    icon: <div className="text-amber-400"><FileIcon /></div>,
                    title: 'Full Document Checklist',
                    desc: 'Every document mandated by RBI for your specific request, clearly listed.',
                  },
                  {
                    icon: <Shield className="w-5 h-5 text-teal-400" />,
                    title: 'Eligibility Criteria',
                    desc: 'CIBIL score, KYC status, income, collateral requirements — all specified.',
                  },
                ].map((item, i) => (
                  <div key={i} className="p-4 rounded-xl bg-slate-900/40 border border-white/5 shadow-inner">
                    <div className="mb-2.5">{item.icon}</div>
                    <p className="font-semibold text-white/95 text-sm">{item.title}</p>
                    <p className="text-slate-400 text-xs mt-1.5 leading-relaxed">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <VerificationResultCard result={result} />
              <FactsPanel facts={result.extracted_facts} />
            </div>
          )}
        </div>
      </main>

      <footer className="border-t border-white/10 py-4">
        <div className="max-w-screen-xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-1 text-xs text-slate-500">
          <span>Hybrid Neuro-Symbolic Guardrails · M.Tech Research Project</span>
          <span>RBI Master Directions 2025 · Z3 SMT Solver · LLM Entity Extraction</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
