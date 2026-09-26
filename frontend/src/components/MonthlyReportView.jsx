import React, { useState, useEffect } from 'react';
import { FileText, Copy, Printer, Check, ArrowDownLeft, ArrowUpRight, ShieldAlert } from 'lucide-react';

export default function MonthlyReportView() {
  const [report, setReport] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch('/api/report/monthly')
      .then(res => res.json())
      .then(data => setReport(data))
      .catch(err => console.error("Error fetching report:", err));
  }, []);

  if (!report) {
    return <div className="p-8 text-center text-slate-400">Synthesizing Monthly Financial Summary Report...</div>;
  }

  const handleCopyMarkdown = () => {
    const markdown = `# FinPilot Executive Financial Summary - ${report.period}

## Financial Snapshot
- Total Income: $${report.total_income.toLocaleString()}
- Total Expenses: $${report.total_expenses.toLocaleString()}
- Net Savings: $${report.net_savings.toLocaleString()} (Savings Rate: ${report.savings_rate}%)
- Recurring Subscriptions Total: $${report.total_recurring_monthly.toLocaleString()}/month

## Executive Commentary
${report.executive_summary}

## Key Action Items
${report.action_items.join('\n')}
`;
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <div>
          <h3 className="font-bold text-slate-100 flex items-center gap-2 text-base">
            <FileText className="h-5 w-5 text-emerald-400" />
            Monthly Financial Summary Report
          </h3>
          <p className="text-xs text-slate-400">Generated report for {report.period}</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyMarkdown}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-lg text-xs font-semibold border border-slate-700 transition"
          >
            {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
            {copied ? 'Copied Markdown' : 'Copy Report'}
          </button>
        </div>
      </div>

      {/* Main Report Document Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 space-y-6">
        {/* Report Header */}
        <div className="border-b border-slate-800 pb-6 flex items-start justify-between">
          <div>
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">FinPilot Intelligence Report</div>
            <h1 className="text-2xl font-bold text-white mt-1">Monthly Financial Executive Summary</h1>
            <div className="text-xs text-slate-400 mt-1">Period: {report.period}</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-emerald-400">${report.net_savings.toLocaleString()}</div>
            <div className="text-xs text-slate-400 font-medium">Net Savings ({report.savings_rate}% Rate)</div>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="space-y-2">
          <h4 className="font-bold text-slate-200 text-sm">Executive Overview</h4>
          <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800">
            {report.executive_summary}
          </p>
        </div>

        {/* Key Metrics Breakdown Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="text-slate-400 text-xs">Total Income</div>
            <div className="text-xl font-bold text-white mt-1">${report.total_income.toLocaleString()}</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="text-slate-400 text-xs">Total Expenses</div>
            <div className="text-xl font-bold text-rose-400 mt-1">${report.total_expenses.toLocaleString()}</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="text-slate-400 text-xs">Active Subscriptions</div>
            <div className="text-xl font-bold text-purple-400 mt-1">{report.active_subscriptions_count} (${report.total_recurring_monthly.toFixed(2)}/mo)</div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="text-slate-400 text-xs">Budget Compliance</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">
              {report.budget_health.within_limit_count} / {report.budget_health.within_limit_count + report.budget_health.exceeded_count + report.budget_health.warning_count} Passed
            </div>
          </div>
        </div>

        {/* Top Spending Categories Table */}
        <div className="space-y-3">
          <h4 className="font-bold text-slate-200 text-sm">Category Spending Breakdown</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4">Category</th>
                  <th className="py-2.5 px-4">Tx Count</th>
                  <th className="py-2.5 px-4">% of Expenses</th>
                  <th className="py-2.5 px-4 text-right">Total Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {report.top_categories.map(c => (
                  <tr key={c.category} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-4 font-semibold text-white">{c.category}</td>
                    <td className="py-2.5 px-4 text-slate-400">{c.transaction_count}</td>
                    <td className="py-2.5 px-4 text-slate-400">{c.percentage}%</td>
                    <td className="py-2.5 px-4 text-right font-bold text-white">${c.total_amount.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Action Items List */}
        <div className="space-y-3 pt-4 border-t border-slate-800">
          <h4 className="font-bold text-slate-200 text-sm flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-amber-400" />
            Recommended Action Items & Observations
          </h4>
          <div className="space-y-2">
            {report.action_items.map((item, idx) => (
              <div key={idx} className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-200 font-medium leading-relaxed">
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
