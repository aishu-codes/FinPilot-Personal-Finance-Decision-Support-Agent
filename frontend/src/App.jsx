import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DashboardOverview from './components/DashboardOverview';
import StatementManager from './components/StatementManager';
import SubscriptionsView from './components/SubscriptionsView';
import BudgetPlanner from './components/BudgetPlanner';
import GoalsTracker from './components/GoalsTracker';
import FinPilotChat from './components/FinPilotChat';
import MonthlyReportView from './components/MonthlyReportView';
import SMSTransactionsView from './components/SMSTransactionsView';

import { 
  LayoutDashboard, FileText, RefreshCw, Target, 
  Sparkles, Layers, Award, Smartphone 
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [activeDataset, setActiveDataset] = useState('tech_pro');
  
  // State data fetched from backend
  const [overviewData, setOverviewData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [subscriptionsData, setSubscriptionsData] = useState(null);
  const [budgets, setBudgets] = useState([]);
  const [goals, setGoals] = useState([]);

  const loadAllData = () => {
    fetch('/api/overview').then(res => res.json()).then(data => setOverviewData(data)).catch(console.error);
    fetch('/api/transactions').then(res => res.json()).then(data => setTransactions(data)).catch(console.error);
    fetch('/api/subscriptions').then(res => res.json()).then(data => setSubscriptionsData(data)).catch(console.error);
    fetch('/api/budgets').then(res => res.json()).then(data => setBudgets(data)).catch(console.error);
    fetch('/api/goals').then(res => res.json()).then(data => setGoals(data)).catch(console.error);
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const navItems = [
    { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'sms', label: '📱 SMS Transactions', icon: Smartphone, badge: 'Smart Agent' },
    { id: 'transactions', label: 'Statements & Transactions', icon: FileText },
    { id: 'subscriptions', label: 'Subscriptions & Bills', icon: RefreshCw },
    { id: 'budgets', label: 'Budgets', icon: Layers },
    { id: 'goals', label: 'Goals & Impact', icon: Target },
    { id: 'chat', label: 'FinPilot AI Assistant', icon: Sparkles, badge: 'Q&A' },
    { id: 'report', label: 'Monthly Report', icon: Award },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Header */}
      <Header
        activeDataset={activeDataset}
        onDatasetChange={(key) => setActiveDataset(key)}
        onReload={loadAllData}
      />

      {/* Main Container */}
      <div className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6">
        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 overflow-x-auto bg-slate-900 p-1.5 rounded-2xl border border-slate-800 scrollbar-none">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20 font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? 'stroke-[2.5]' : ''}`} />
                <span>{item.label}</span>
                {item.badge && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-extrabold uppercase ${
                    isActive ? 'bg-slate-950 text-emerald-400' : 'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Tab Content Rendering */}
        <main className="transition-all">
          {activeTab === 'overview' && (
            <DashboardOverview 
              overviewData={overviewData}
              onViewSMS={() => setActiveTab('sms')}
            />
          )}

          {activeTab === 'sms' && (
            <SMSTransactionsView onReloadMain={loadAllData} />
          )}

          {activeTab === 'transactions' && (
            <StatementManager
              transactions={transactions}
              onUploadSuccess={loadAllData}
              onReload={loadAllData}
            />
          )}

          {activeTab === 'subscriptions' && (
            <SubscriptionsView subscriptionsData={subscriptionsData} />
          )}

          {activeTab === 'budgets' && (
            <BudgetPlanner budgets={budgets} onReload={loadAllData} />
          )}

          {activeTab === 'goals' && (
            <GoalsTracker goals={goals} />
          )}

          {activeTab === 'chat' && (
            <FinPilotChat />
          )}

          {activeTab === 'report' && (
            <MonthlyReportView />
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 text-center py-4 text-xs text-slate-500">
        FinPilot Personal Finance Decision Support Agent • Smart SMS Agent Enabled
      </footer>
    </div>
  );
}
