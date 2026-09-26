import React, { useState } from 'react';
import { Target, Calendar, TrendingUp, Sliders, CheckCircle2, AlertCircle } from 'lucide-react';

export default function GoalsTracker({ goals }) {
  const [selectedGoalId, setSelectedGoalId] = useState(goals?.[0]?.id || 'g1');
  const [extraSpend, setExtraSpend] = useState(100);
  const [simulationResult, setSimulationResult] = useState(null);

  if (!goals || goals.length === 0) {
    return <div className="p-8 text-center text-slate-400">Loading financial goals...</div>;
  }

  const handleSimulate = (goalId, spendVal) => {
    setSelectedGoalId(goalId);
    setExtraSpend(spendVal);

    fetch('/api/goals/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        goal_id: goalId,
        additional_monthly_spending: parseFloat(spendVal)
      })
    })
      .then(res => res.json())
      .then(data => setSimulationResult(data));
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h3 className="font-bold text-slate-100 flex items-center gap-2 text-base mb-1">
          <Target className="h-5 w-5 text-emerald-400" />
          Financial Goals & Savings Velocity
        </h3>
        <p className="text-xs text-slate-400">
          Track target dates, monthly contribution rates, and run interactive spending impact simulations.
        </p>
      </div>

      {/* Goals Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {goals.map(g => (
          <div key={g.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 px-2 py-0.5 rounded bg-slate-800">
                  {g.category}
                </span>
                <h4 className="font-bold text-white text-base mt-1">{g.name}</h4>
              </div>

              <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                g.status === 'on_track' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}>
                {g.status === 'on_track' ? 'On Track' : 'At Risk'}
              </span>
            </div>

            {/* Savings Numbers */}
            <div className="flex items-baseline justify-between text-xs">
              <span className="text-slate-400">Current: <strong className="text-emerald-400 text-sm">${g.current_savings.toLocaleString()}</strong></span>
              <span className="text-slate-400">Target: <strong className="text-white text-sm">${g.target_amount.toLocaleString()}</strong></span>
            </div>

            {/* Progress Bar */}
            <div className="space-y-1">
              <div className="h-2.5 w-full bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
                <div
                  className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, g.completion_percentage)}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>{g.completion_percentage}% saved</span>
                <span>${g.monthly_contribution}/month rate</span>
              </div>
            </div>

            {/* Dates */}
            <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-300 flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-slate-500" />
                <span>Target: <strong className="text-slate-200">{g.target_date}</strong></span>
              </div>
              <div className="text-slate-400">
                Projected: <strong className="text-emerald-300">{g.projected_date}</strong>
              </div>
            </div>

            {g.impact_notes && (
              <p className="text-[11px] text-slate-400 italic bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                {g.impact_notes}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Goal Impact Simulator */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h4 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
          <Sliders className="h-4 w-4 text-emerald-400" />
          Interactive Goal Impact Simulator
        </h4>
        <p className="text-xs text-slate-400">
          See how discretionary overspending (e.g. extra dining out or shopping) delays your savings target date.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div>
            <label className="text-xs text-slate-400 font-semibold block mb-1">Select Goal</label>
            <select
              value={selectedGoalId}
              onChange={(e) => handleSimulate(e.target.value, extraSpend)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
            >
              {goals.map(g => (
                <option key={g.id} value={g.id}>{g.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-400 font-semibold block mb-1">
              Extra Monthly Spending: <strong className="text-rose-400">${extraSpend}/mo</strong>
            </label>
            <input
              type="range"
              min="0"
              max="500"
              step="25"
              value={extraSpend}
              onChange={(e) => handleSimulate(selectedGoalId, e.target.value)}
              className="w-full accent-emerald-500 cursor-pointer"
            />
          </div>

          <div className="text-right">
            <button
              onClick={() => handleSimulate(selectedGoalId, extraSpend)}
              className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-4 py-2 rounded-lg text-xs"
            >
              Calculate Impact
            </button>
          </div>
        </div>

        {simulationResult && (
          <div className="p-4 bg-emerald-950/30 border border-emerald-500/30 rounded-xl text-xs space-y-2">
            <div className="font-bold text-emerald-300 text-sm">
              Simulation Results for {simulationResult.goal_name}:
            </div>
            <p className="text-slate-200">{simulationResult.impact_summary}</p>
            <div className="flex gap-4 text-slate-400">
              <span>Original Projected Date: <strong className="text-white">{simulationResult.original_projected_date}</strong></span>
              <span>New Projected Date: <strong className="text-rose-300">{simulationResult.new_projected_date}</strong></span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
