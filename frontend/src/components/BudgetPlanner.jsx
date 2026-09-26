import React, { useState } from 'react';
import { Target, AlertTriangle, CheckCircle2, Plus, Edit2 } from 'lucide-react';

export default function BudgetPlanner({ budgets, onReload }) {
  const [editingCategory, setEditingCategory] = useState(null);
  const [newAllocated, setNewAllocated] = useState('');

  if (!budgets || budgets.length === 0) {
    return <div className="p-8 text-center text-slate-400">Loading budget data...</div>;
  }

  const handleUpdateBudget = (e) => {
    e.preventDefault();
    if (!editingCategory || !newAllocated) return;

    const formData = new FormData();
    formData.append('category', editingCategory);
    formData.append('allocated_amount', newAllocated);

    fetch('/api/budgets', {
      method: 'POST',
      body: formData
    })
      .then(res => res.json())
      .then(() => {
        setEditingCategory(null);
        setNewAllocated('');
        onReload();
      });
  };

  const totalAllocated = budgets.reduce((sum, b) => sum + b.allocated_amount, 0);
  const totalSpent = budgets.reduce((sum, b) => sum + b.spent_amount, 0);
  const totalCommitted = budgets.reduce((sum, b) => sum + b.committed_amount, 0);
  const overallPct = totalAllocated > 0 ? Math.round((totalSpent / totalAllocated) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Overall Budget Overview Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="font-bold text-slate-100 flex items-center gap-2 text-base">
              <Target className="h-5 w-5 text-emerald-400" />
              Monthly Budget Compliance
            </h3>
            <p className="text-xs text-slate-400">Compare actual spending against category limits</p>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 font-medium">Total Budget: </span>
            <span className="text-xl font-bold text-white">${totalAllocated.toLocaleString()}</span>
          </div>
        </div>

        {/* Overall Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-300 font-medium">
            <span>Spent: <strong className="text-white">${totalSpent.toLocaleString()}</strong> (${totalCommitted.toLocaleString()} committed)</span>
            <span>{overallPct}% of budget used</span>
          </div>
          <div className="h-3 w-full bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                overallPct > 100 ? 'bg-rose-500' : overallPct >= 80 ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, overallPct)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Edit Modal / Inline Form */}
      {editingCategory && (
        <form onSubmit={handleUpdateBudget} className="bg-slate-900 border border-emerald-500/50 rounded-xl p-4 flex items-center gap-3">
          <span className="text-xs text-slate-200 font-bold">Update Budget for {editingCategory}:</span>
          <input
            type="number"
            step="10"
            placeholder="New Amount ($)"
            value={newAllocated}
            onChange={(e) => setNewAllocated(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded px-3 py-1 text-xs text-white"
            required
          />
          <button type="submit" className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold text-xs px-3 py-1 rounded">
            Save
          </button>
          <button type="button" onClick={() => setEditingCategory(null)} className="text-slate-400 hover:text-slate-200 text-xs">
            Cancel
          </button>
        </form>
      )}

      {/* Category Budget Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {budgets.map(b => (
          <div key={b.category} className="bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-bold text-white text-sm">{b.category}</h4>
                <div className="text-xs text-slate-400 mt-0.5">
                  Spent: <span className="font-semibold text-slate-200">${b.spent_amount.toFixed(2)}</span> / ${b.allocated_amount.toFixed(2)}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase ${
                  b.status === 'exceeded' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                  b.status === 'warning' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                  'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                }`}>
                  {b.status.replace('_', ' ')}
                </span>
                <button
                  onClick={() => { setEditingCategory(b.category); setNewAllocated(b.allocated_amount); }}
                  className="p-1 text-slate-500 hover:text-slate-300"
                  title="Edit Budget"
                >
                  <Edit2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>

            {/* Progress bar */}
            <div className="space-y-1">
              <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    b.status === 'exceeded' ? 'bg-rose-500' : b.status === 'warning' ? 'bg-amber-500' : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.min(100, b.percentage_used)}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>Committed: ${b.committed_amount.toFixed(2)}</span>
                <span>{b.percentage_used}% used ({b.remaining_amount >= 0 ? `$${b.remaining_amount.toFixed(2)} left` : `$${Math.abs(b.remaining_amount).toFixed(2)} over`})</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
