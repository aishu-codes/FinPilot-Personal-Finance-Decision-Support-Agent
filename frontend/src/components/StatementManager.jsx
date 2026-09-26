import React, { useState } from 'react';
import { Upload, FileText, Plus, Search, Filter, CheckCircle2, ArrowDownLeft, ArrowUpRight } from 'lucide-react';

export default function StatementManager({ transactions, onUploadSuccess, onReload }) {
  const [activeTab, setActiveTab] = useState('upload'); // upload | text | manual
  const [file, setFile] = useState(null);
  const [billText, setBillText] = useState('');
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');

  // Manual transaction form
  const [manualForm, setManualForm] = useState({
    merchant: '',
    amount: '',
    category: 'Shopping',
    date: '2026-09-25',
    type: 'expense'
  });

  const handleFileUpload = (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setUploadMsg('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('account_name', 'Uploaded Statement');

    fetch('/api/upload/statement', {
      method: 'POST',
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        setUploadMsg(`Successfully ingested ${data.ingested_count} transactions!`);
        setFile(null);
        onReload();
      })
      .catch(err => setUploadMsg('Upload failed: ' + err.message))
      .finally(() => setUploading(false));
  };

  const handleTextUpload = (e) => {
    e.preventDefault();
    if (!billText.trim()) return;
    setUploading(true);
    setUploadMsg('');

    const formData = new FormData();
    formData.append('text_content', billText);
    formData.append('account_name', 'Bill Parse');

    fetch('/api/upload/statement', {
      method: 'POST',
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        setUploadMsg('Parsed and saved bill transaction!');
        setBillText('');
        onReload();
      })
      .catch(err => setUploadMsg('Parsing failed: ' + err.message))
      .finally(() => setUploading(false));
  };

  const handleManualAdd = (e) => {
    e.preventDefault();
    if (!manualForm.merchant || !manualForm.amount) return;
    
    const amt = parseFloat(manualForm.amount);
    const tx = {
      id: `tx_man_${Date.now()}`,
      merchant: manualForm.merchant,
      amount: manualForm.type === 'income' ? -abs(amt) : Math.abs(amt),
      category: manualForm.category,
      date: manualForm.date,
      type: manualForm.type,
      source: 'manual'
    };

    fetch('/api/transaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tx)
    })
      .then(res => res.json())
      .then(() => {
        setUploadMsg('Added transaction successfully!');
        setManualForm({ merchant: '', amount: '', category: 'Shopping', date: '2026-09-25', type: 'expense' });
        onReload();
      });
  };

  const categories = ['All', 'Income', 'Housing & Utilities', 'Groceries', 'Food & Dining', 'Subscriptions', 'Shopping', 'Transportation', 'Health & Fitness', 'Entertainment', 'Childcare & Education', 'Software & Tools', 'Travel'];

  const filteredTx = transactions.filter(t => {
    const matchCat = selectedCategory === 'All' || t.category === selectedCategory;
    const matchSearch = !search || t.merchant.toLowerCase().includes(search.toLowerCase()) || t.date.includes(search);
    return matchCat && matchSearch;
  });

  return (
    <div className="space-y-6">
      {/* Upload & Ingestion Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h3 className="font-bold text-slate-100 flex items-center gap-2 mb-1">
          <Upload className="h-5 w-5 text-emerald-400" />
          Statement & Bill Ingestion
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Upload bank/credit card CSV statements, JSON export files, or paste raw text bills for automated parsing & categorization.
        </p>

        {/* Ingestion Mode Tabs */}
        <div className="flex border-b border-slate-800 mb-4 gap-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('upload')}
            className={`pb-2 border-b-2 transition ${activeTab === 'upload' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          >
            Upload CSV / JSON File
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`pb-2 border-b-2 transition ${activeTab === 'text' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          >
            Parse Raw Bill Text
          </button>
          <button
            onClick={() => setActiveTab('manual')}
            className={`pb-2 border-b-2 transition ${activeTab === 'manual' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          >
            Add Single Transaction
          </button>
        </div>

        {uploadMsg && (
          <div className="mb-4 p-3 bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs rounded-lg flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
            <span>{uploadMsg}</span>
          </div>
        )}

        {/* Tab 1: CSV / JSON Dropzone */}
        {activeTab === 'upload' && (
          <form onSubmit={handleFileUpload} className="space-y-4">
            <div className="border-2 border-dashed border-slate-800 hover:border-slate-700 bg-slate-950/40 rounded-xl p-6 text-center cursor-pointer transition">
              <input
                type="file"
                accept=".csv,.json"
                onChange={(e) => setFile(e.target.files[0])}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer block">
                <Upload className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                <span className="text-sm font-semibold text-slate-200 block">
                  {file ? file.name : 'Click or drag statement file to upload'}
                </span>
                <span className="text-xs text-slate-500 block mt-1">Supports CSV, JSON statement exports</span>
              </label>
            </div>
            {file && (
              <button
                type="submit"
                disabled={uploading}
                className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 px-4 py-2 rounded-lg text-xs font-bold transition"
              >
                {uploading ? 'Processing File...' : 'Ingest File Data'}
              </button>
            )}
          </form>
        )}

        {/* Tab 2: Text Bill Parser */}
        {activeTab === 'text' && (
          <form onSubmit={handleTextUpload} className="space-y-3">
            <textarea
              rows={4}
              value={billText}
              onChange={(e) => setBillText(e.target.value)}
              placeholder="Paste raw bill text or receipt text here, e.g.:&#10;City Water & Light Bill&#10;Date: 2026-09-20&#10;Total Amount Due: $145.80"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            />
            <button
              type="submit"
              disabled={uploading || !billText.trim()}
              className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 px-4 py-2 rounded-lg text-xs font-bold transition disabled:opacity-50"
            >
              Parse Bill & Add
            </button>
          </form>
        )}

        {/* Tab 3: Manual Entry */}
        {activeTab === 'manual' && (
          <form onSubmit={handleManualAdd} className="grid grid-cols-1 md:grid-cols-5 gap-3">
            <input
              type="text"
              placeholder="Merchant / Description"
              value={manualForm.merchant}
              onChange={(e) => setManualForm({ ...manualForm, merchant: e.target.value })}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
              required
            />
            <input
              type="number"
              step="0.01"
              placeholder="Amount ($)"
              value={manualForm.amount}
              onChange={(e) => setManualForm({ ...manualForm, amount: e.target.value })}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
              required
            />
            <select
              value={manualForm.category}
              onChange={(e) => setManualForm({ ...manualForm, category: e.target.value })}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
            >
              {categories.filter(c => c !== 'All').map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            <input
              type="date"
              value={manualForm.date}
              onChange={(e) => setManualForm({ ...manualForm, date: e.target.value })}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
            />
            <button
              type="submit"
              className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-4 py-2 rounded-lg text-xs"
            >
              Add Record
            </button>
          </form>
        )}
      </div>

      {/* Transactions Data Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="font-bold text-slate-100 text-base">Transactions Record</h3>
            <p className="text-xs text-slate-400">Total {filteredTx.length} transactions listed</p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Search Input */}
            <div className="relative">
              <Search className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search merchant, date..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 w-48"
              />
            </div>

            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-emerald-400 font-semibold focus:outline-none"
            >
              {categories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Merchant / Payee</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4 text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredTx.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500">
                    No transactions match the selected filters.
                  </td>
                </tr>
              ) : (
                filteredTx.map(tx => (
                  <tr key={tx.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 text-slate-400 font-mono">{tx.date}</td>
                    <td className="py-3 px-4 font-semibold text-white">
                      {tx.merchant}
                      {tx.is_recurring && (
                        <span className="ml-2 px-1.5 py-0.5 text-[10px] rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                          Recurring
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-medium">
                        {tx.category}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {tx.type === 'income' ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                          <ArrowDownLeft className="h-3 w-3" /> Income
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-slate-400 font-medium">
                          <ArrowUpRight className="h-3 w-3 text-slate-500" /> Expense
                        </span>
                      )}
                    </td>
                    <td className={`py-3 px-4 text-right font-bold text-sm ${tx.type === 'income' ? 'text-emerald-400' : 'text-slate-100'}`}>
                      {tx.type === 'income' ? `+$${Math.abs(tx.amount).toFixed(2)}` : `-$${Math.abs(tx.amount).toFixed(2)}`}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
