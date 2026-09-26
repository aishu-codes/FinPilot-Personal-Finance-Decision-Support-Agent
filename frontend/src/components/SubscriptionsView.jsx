import React from 'react';
import { RefreshCw, AlertTriangle, Calendar, CheckCircle2, TrendingUp, DollarSign } from 'lucide-react';

export default function SubscriptionsView({ subscriptionsData }) {
  if (!subscriptionsData) {
    return <div className="p-8 text-center text-slate-400">Loading recurring subscriptions...</div>;
  }

  const { subscriptions, upcoming_summary } = subscriptionsData;
  const totalMonthly = subscriptions.reduce((sum, s) => sum + s.amount, 0);
  const totalAnnual = totalMonthly * 12;

  const priceHikes = subscriptions.filter(s => s.status === 'price_hike' || (s.price_change_pct && s.price_change_pct > 0));

  return (
    <div className="space-y-6">
      {/* Summary Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="text-slate-400 text-xs font-medium mb-1">Active Subscriptions</div>
          <div className="text-3xl font-bold text-white">{subscriptions.length}</div>
          <div className="text-xs text-purple-400 mt-1">Services & Bills</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="text-slate-400 text-xs font-medium mb-1">Monthly Committed Spend</div>
          <div className="text-3xl font-bold text-emerald-400">${totalMonthly.toFixed(2)}</div>
          <div className="text-xs text-slate-400 mt-1">${totalAnnual.toFixed(2)} per year</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="text-slate-400 text-xs font-medium mb-1">Detected Price Hikes</div>
          <div className="text-3xl font-bold text-amber-400">{priceHikes.length}</div>
          <div className="text-xs text-amber-300/80 mt-1">Requires user review</div>
        </div>
      </div>

      {/* Price Hike Warning Alert */}
      {priceHikes.length > 0 && (
        <div className="bg-amber-950/30 border border-amber-500/40 rounded-2xl p-4 text-amber-200">
          <h4 className="font-bold text-sm flex items-center gap-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            Subscription Price Increases Detected
          </h4>
          <div className="space-y-2 text-xs">
            {priceHikes.map(s => (
              <div key={s.id} className="flex items-center justify-between bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <div>
                  <span className="font-bold text-white">{s.merchant}</span>
                  <span className="ml-2 text-slate-400">({s.category})</span>
                </div>
                <div className="text-right">
                  <span className="text-rose-400 font-bold mr-2">+${(s.amount - (s.previous_amount || 0)).toFixed(2)} ({s.price_change_pct}%)</span>
                  <span className="text-slate-400 line-through text-[11px]">${s.previous_amount?.toFixed(2)}</span> → <span className="font-bold text-white">${s.amount.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Subscriptions Grid */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h3 className="font-bold text-slate-100 flex items-center gap-2 mb-4">
          <RefreshCw className="h-5 w-5 text-purple-400" />
          Recurring Subscriptions & Fixed Obligations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {subscriptions.map(sub => (
            <div key={sub.id} className="bg-slate-950 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-slate-100 text-sm">{sub.merchant}</h4>
                  <span className="text-xs text-slate-400">{sub.category}</span>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-white">${sub.amount.toFixed(2)}</div>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">{sub.frequency}</span>
                </div>
              </div>

              {sub.status === 'price_hike' && (
                <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[11px] font-bold px-2 py-1 rounded">
                  ⚠️ Price increased +{sub.price_change_pct}%
                </div>
              )}

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-slate-500" />
                  Next due: <span className="text-slate-200 font-medium">{sub.next_due}</span>
                </span>
                <span className="text-slate-500 text-[11px]">Last: {sub.last_billed}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
