import React, { useState, useEffect } from 'react';
import { Smartphone, ShieldAlert, ArrowRight, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function SMSAgentWidget({ onViewSMS }) {
  const [smsSummary, setSmsSummary] = useState(null);

  useEffect(() => {
    fetch('/api/sms/transactions')
      .then(res => res.json())
      .then(data => setSmsSummary(data.summary))
      .catch(console.error);
  }, []);

  if (!smsSummary) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Smartphone className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-sm">Smart SMS Agent</h3>
            <p className="text-xs text-slate-400">Real-time mobile SMS transaction & fraud monitor</p>
          </div>
        </div>

        <button
          onClick={onViewSMS}
          className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold bg-emerald-500/10 hover:bg-emerald-500/20 px-3 py-1.5 rounded-lg border border-emerald-500/20 transition"
        >
          <span>View SMS Transactions</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs">
        <div>
          <span className="text-slate-400 block text-[11px]">Total SMS Received</span>
          <span className="font-bold text-white text-base">{smsSummary.total_sms}</span>
        </div>

        <div>
          <span className="text-slate-400 block text-[11px]">Expenses Detected</span>
          <span className="font-bold text-rose-400 text-base">${smsSummary.expenses_detected.toLocaleString()}</span>
        </div>

        <div>
          <span className="text-slate-400 block text-[11px]">Income Detected</span>
          <span className="font-bold text-emerald-400 text-base">${smsSummary.income_detected.toLocaleString()}</span>
        </div>

        <div>
          <span className="text-slate-400 block text-[11px]">Suspicious Alerts</span>
          <span className="font-bold text-amber-400 text-base">{smsSummary.suspicious_count}</span>
        </div>
      </div>
    </div>
  );
}
