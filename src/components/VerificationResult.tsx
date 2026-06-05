import { AlertCircle, BookOpen, CheckSquare, FileText, Scale, Lightbulb, ShieldAlert, ShieldCheck, CheckCircle2, ChevronRight } from 'lucide-react';
import type { VerificationResult } from '../lib/verifier';
import { VerdictBadge } from './VerdictBadge';

interface Props {
  result: VerificationResult;
}

export function VerificationResultCard({ result }: Props) {
  const { verdict, violations, required_documents, required_criteria, triggered_rules, counterfactual, explanation } = result;
  const isSat = verdict === 'SAT';

  return (
    <div className={`rounded-2xl border backdrop-blur-md shadow-2xl overflow-hidden transition-all ${isSat ? 'border-emerald-500/30 bg-slate-900/70' : 'border-rose-500/30 bg-slate-900/70'}`}>
      
      {/* 1. Header Banner */}
      <div className={`px-6 py-5 flex items-center justify-between ${isSat ? 'bg-gradient-to-r from-emerald-600/80 to-teal-600/80 border-b border-emerald-500/20' : 'bg-gradient-to-r from-rose-600/80 to-red-600/80 border-b border-rose-500/20'}`}>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-white/10 backdrop-blur-md">
            {isSat ? (
              <ShieldCheck className="w-6 h-6 text-emerald-200" />
            ) : (
              <ShieldAlert className="w-6 h-6 text-rose-200" />
            )}
          </div>
          <div>
            <p className="text-white/60 text-[9px] font-bold uppercase tracking-widest leading-none">Formal Verification Engine</p>
            <h3 className="text-white font-bold text-base leading-tight mt-1">
              {isSat ? 'RBI Compliance Satisfied' : 'Compliance Violations Detected'}
            </h3>
          </div>
        </div>
        <VerdictBadge verdict={verdict} size="lg" />
      </div>

      {/* 2. Main Explanation (Premium Text spacing) */}
      <div className="px-6 py-5 border-b border-white/5 bg-slate-950/30">
        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line font-medium">
          {explanation}
        </p>
      </div>

      {/* 3. Sleek Glowing Metric Cards (Highly Highlighted & Clean) */}
      <div className="px-6 py-4 bg-slate-950/20 border-b border-white/5 grid grid-cols-1 sm:grid-cols-3 gap-3">
        
        {/* Violations Card */}
        <div className={`p-3.5 rounded-xl border flex items-center justify-between transition-all ${violations.length > 0 ? 'bg-rose-950/30 border-rose-500/30 shadow-md shadow-rose-950/20' : 'bg-emerald-950/30 border-emerald-500/20'}`}>
          <div className="flex items-center gap-2.5">
            <AlertCircle className={`w-5 h-5 ${violations.length > 0 ? 'text-rose-400' : 'text-emerald-400'}`} />
            <div>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider leading-none">Violations</p>
              <p className="text-xs text-slate-300 font-medium mt-1">Direct Issues</p>
            </div>
          </div>
          <span className={`text-xl font-black ${violations.length > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {violations.length}
          </span>
        </div>

        {/* Documents Card */}
        <div className="p-3.5 rounded-xl border bg-blue-950/30 border-blue-500/20 shadow-md shadow-blue-950/20 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <FileText className="w-5 h-5 text-blue-400" />
            <div>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider leading-none">Required Docs</p>
              <p className="text-xs text-slate-300 font-medium mt-1">Paperwork</p>
            </div>
          </div>
          <span className="text-xl font-black text-blue-400">
            {required_documents.length}
          </span>
        </div>

        {/* Criteria Card */}
        <div className="p-3.5 rounded-xl border bg-amber-950/30 border-amber-500/20 shadow-md shadow-amber-950/20 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Scale className="w-5 h-5 text-amber-400" />
            <div>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider leading-none">Limits & Criteria</p>
              <p className="text-xs text-slate-300 font-medium mt-1">Thresholds</p>
            </div>
          </div>
          <span className="text-xl font-black text-amber-400">
            {required_criteria.length}
          </span>
        </div>

      </div>

      {/* 4. Unified, Systematic Single-Column Execution Body */}
      <div className="p-6 space-y-6">
        
        {/* Compliance Resolution Path (Teal Highlight Box) */}
        {counterfactual && (
          <div className="rounded-xl border border-teal-500/20 bg-teal-950/20 p-4 space-y-2 shadow-lg">
            <div className="flex items-center gap-2 text-teal-300 font-bold text-xs uppercase tracking-wider">
              <Lightbulb className="w-4 h-4 text-teal-400 animate-pulse" />
              Compliance Resolution Roadmap
            </div>
            <p className="text-xs text-teal-200 leading-relaxed font-semibold pl-6">
              {counterfactual}
            </p>
          </div>
        )}

        {/* Satisfied State Notification */}
        {isSat && (
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/20 p-4 space-y-2">
            <div className="flex items-center gap-2 text-emerald-300 font-bold text-xs uppercase tracking-wider">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              SMT Solver Satisfied
            </div>
            <p className="text-xs text-emerald-200 leading-relaxed font-medium pl-6">
              Z3 SMT Solver has mathematically proven your parameter states as fully compliant. No compliance violations have been triggered in the logic network.
            </p>
          </div>
        )}

        {/* Unified Compliance Action Checklist (Highly Systematic) */}
        {(violations.length > 0 || required_documents.length > 0 || required_criteria.length > 0) && (
          <div className="rounded-xl border border-white/5 bg-slate-950/30 overflow-hidden shadow-lg">
            
            {/* Checklist Section Title */}
            <div className="px-4 py-3 bg-slate-950/40 border-b border-white/5 flex items-center justify-between">
              <span className="text-xs font-bold text-white/80 uppercase tracking-wide">Fulfillment Action Checklist</span>
              <span className="text-[10px] text-slate-400 font-medium">Step-by-step resolution</span>
            </div>

            {/* Checklist Content */}
            <div className="p-4 space-y-4">
              
              {/* Step 1: Violations */}
              {violations.length > 0 && (
                <div className="space-y-2">
                  <div className="text-[10px] text-rose-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
                    Step 1: Resolve Direct Violations
                  </div>
                  <ul className="space-y-2 pl-3">
                    {violations.map((v, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-xs text-slate-200 leading-relaxed font-semibold">
                        <AlertCircle className="w-3.5 h-3.5 text-rose-500 mt-0.5 shrink-0" />
                        <span>{v}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Step 2: Documents */}
              {required_documents.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-white/5">
                  <div className="text-[10px] text-blue-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                    Step 2: Gather Mandated Documentation
                  </div>
                  <ul className="space-y-2 pl-3">
                    {required_documents.map((doc, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-xs text-slate-200 leading-relaxed font-medium">
                        <ChevronRight className="w-3.5 h-3.5 text-blue-500 mt-0.5 shrink-0" />
                        <span>{doc}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Step 3: Criteria */}
              {required_criteria.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-white/5">
                  <div className="text-[10px] text-amber-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                    Step 3: Verify Regulatory Thresholds & Criteria
                  </div>
                  <ul className="space-y-2 pl-3">
                    {required_criteria.map((crit, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-xs text-slate-200 leading-relaxed font-medium">
                        <CheckSquare className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
                        <span>{crit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            </div>
          </div>
        )}

        {/* 5. Triggered regulations metadata (Cards grid at bottom) */}
        {triggered_rules.length > 0 && (
          <div className="rounded-xl border border-white/5 bg-slate-950/20 p-4 space-y-3 shadow-inner">
            <div className="flex items-center gap-2 text-slate-400 font-bold text-xs uppercase tracking-wider">
              <BookOpen className="w-4 h-4 text-slate-500" />
              Referenced RBI Legal Clauses
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {triggered_rules.map((rule, i) => (
                <div key={i} className="p-3 bg-slate-900/40 rounded-lg border border-white/5 shadow-sm flex flex-col justify-between hover:bg-slate-900/60 transition-all">
                  <div>
                    <span className="text-[9px] bg-slate-950/80 text-slate-400 font-bold px-1.5 py-0.5 rounded-full uppercase border border-white/5">
                      {rule.category}
                    </span>
                    <h4 className="font-bold text-white/80 text-xs mt-2.5 leading-snug">
                      [{rule.rule_id}] {rule.title}
                    </h4>
                  </div>
                  <p className="text-[9px] text-slate-500 mt-2.5 italic leading-tight">
                    Source: {rule.source}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
