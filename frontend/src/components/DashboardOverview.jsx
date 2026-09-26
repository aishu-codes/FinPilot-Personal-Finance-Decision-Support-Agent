import React from 'react';
import { 
  TrendingUp, TrendingDown, DollarSign, Wallet, AlertTriangle, 
  RefreshCw, PieChart as PieIcon, ArrowUpRight, ArrowDownRight, ShieldAlert 
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import SMSAgentWidget from './SMSAgentWidget';

const COLORS = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EC4899', '#06B6D4', '#64748B'];

export default function DashboardOverview({ overviewData, onViewSMS }) {
  if (!overviewData) {
    return (
      <div className="flex items-center justify-center p-12 text-slate-400">
        <RefreshCw className="h-6 w-6 animate-spin mr-2 text-emerald-400" /> Loading Financial Dashboard...
      </div>
    );
  }

  const {
    total_income,
    total_expenses,
    net_savings,
    savings_rate,
    committed_obligations,
    active_subscriptions_count,
    anomalies_count,
    suspicious_sms_count,
    online_spending,
    cash_spending,
    cashflow,
    top_categories,
    anomalies
  } = overviewData;

  return (
    <div className="space-y-6">
      {/* Smart SMS Agent Widget */}
      <SMSAgentWidget onViewSMS={onViewSMS} />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2 font-medium">
            <span>Total Income</span>
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <ArrowDownRight className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">${total_income.toLocaleString()}</div>
          <div className="text-xs text-emerald-400 font-medium mt-1">Monthly Inflow</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2 font-medium">
            <span>Total Expenses</span>
            <div className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
              <ArrowUpRight className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">${total_expenses.toLocaleString()}</div>
          <div className="text-xs text-slate-400 font-medium mt-1">
            Online: <span className="text-emerald-400">${online_spending.toLocaleString()}</span> | Cash: <span className="text-amber-400">${cash_spending.toLocaleString()}</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2 font-medium">
            <span>Net Savings</span>
            <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
              <Wallet className="h-4 w-4" />
            </div>
          </div>
          <div className={`text-2xl font-bold ${net_savings >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            ${net_savings.toLocaleString()}
          </div>
          <div className="text-xs text-slate-400 font-medium mt-1">
            Savings Rate: <span className="text-emerald-400 font-bold">{savings_rate}%</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2 font-medium">
            <span>Committed Recurring</span>
            <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
              <RefreshCw className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">${committed_obligations.toLocaleString()}</div>
          <div className="text-xs text-purple-300 font-medium mt-1">
            {active_subscriptions_count} Active Obligations
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2 font-medium">
            <span>Spending Alerts</span>
            <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
              <ShieldAlert className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-amber-400">{anomalies_count}</div>
          <div className="text-xs text-amber-300/80 font-medium mt-1">
            Spikes & Suspicious SMS ({suspicious_sms_count})
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cash Flow Area Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-100 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-emerald-400" />
                Monthly Cash Flow Trend
              </h3>
              <p className="text-xs text-slate-400">Income vs Expenses across recent months</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={cashflow} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                  formatter={(val) => `$${val.toLocaleString()}`}
                />
                <Area type="monotone" dataKey="income" stroke="#10B981" fillOpacity={1} fill="url(#colorIncome)" name="Income" />
                <Area type="monotone" dataKey="expenses" stroke="#EF4444" fillOpacity={1} fill="url(#colorExpenses)" name="Expenses" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Spending Pie Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="mb-4">
            <h3 className="font-bold text-slate-100 flex items-center gap-2">
              <PieIcon className="h-5 w-5 text-accent" />
              Expenses by Category
            </h3>
            <p className="text-xs text-slate-400">Distribution of current month spending</p>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={top_categories.slice(0, 5)}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="amount"
                  nameKey="category"
                >
                  {top_categories.slice(0, 5).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                  formatter={(val) => `$${val.toLocaleString()}`}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-2 space-y-1">
            {top_categories.slice(0, 4).map((c, i) => (
              <div key={c.category} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }}></span>
                  <span className="text-slate-300">{c.category}</span>
                </div>
                <span className="font-semibold text-slate-100">${c.amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Anomalies & Spending Alerts Feed */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-slate-100 flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-amber-400" />
              Detected Anomalies & Suspicious SMS Feed
            </h3>
            <p className="text-xs text-slate-400">Automated AI detection of category surges, price increases, and suspicious SMS links</p>
          </div>
        </div>

        {anomalies.length === 0 ? (
          <div className="p-6 text-center text-slate-400 text-sm bg-slate-950/50 rounded-xl border border-slate-800">
            No unusual spending anomalies detected for this period.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {anomalies.map((alt) => (
              <div 
                key={alt.id}
                className={`p-4 rounded-xl border transition ${
                  alt.severity === 'high' 
                    ? 'bg-rose-950/20 border-rose-500/40 text-rose-200' 
                    : 'bg-amber-950/20 border-amber-500/40 text-amber-200'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="inline-block px-2 py-0.5 text-[10px] uppercase tracking-wider font-bold rounded mb-1 bg-slate-800 text-slate-300">
                      {alt.type.replace('_', ' ')}
                    </span>
                    <h4 className="font-bold text-sm text-white">{alt.title}</h4>
                  </div>
                  <span className="font-bold text-sm bg-slate-900 px-2 py-1 rounded border border-slate-700">
                    ${alt.amount.toLocaleString()}
                  </span>
                </div>
                <p className="text-xs mt-2 text-slate-300 leading-relaxed">{alt.description}</p>
                {alt.action_suggested && (
                  <div className="mt-3 text-xs bg-slate-900/80 p-2 rounded-lg border border-slate-800 font-medium text-amber-300 flex items-center gap-1.5">
                    <span>💡 Action:</span>
                    <span>{alt.action_suggested}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
