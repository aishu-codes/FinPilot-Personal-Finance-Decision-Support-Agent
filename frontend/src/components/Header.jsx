import React, { useState, useEffect } from 'react';
import { Compass, RefreshCw, Layers, Sparkles } from 'lucide-react';

export default function Header({ activeDataset, onDatasetChange, onReload }) {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/datasets')
      .then(res => res.json())
      .then(data => setDatasets(data))
      .catch(err => console.error("Error fetching datasets:", err));
  }, []);

  const handleSelect = (e) => {
    const key = e.target.value;
    setLoading(true);
    fetch(`/api/dataset/load/${key}`, { method: 'POST' })
      .then(res => res.json())
      .then(() => {
        onDatasetChange(key);
        onReload();
      })
      .finally(() => setLoading(false));
  };

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-slate-950 shadow-lg shadow-emerald-500/20">
          <Compass className="h-6 w-6 stroke-[2.5]" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
              FinPilot
            </h1>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              AI Support Agent
            </span>
          </div>
          <p className="text-xs text-slate-400">Personal Finance Decision Support System</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/80 text-xs text-slate-300">
          <Layers className="h-4 w-4 text-emerald-400" />
          <span className="font-medium">Active Profile:</span>
          <select 
            value={activeDataset}
            onChange={handleSelect}
            disabled={loading}
            className="bg-slate-900 text-emerald-400 font-semibold border border-slate-700 rounded px-2 py-1 focus:outline-none focus:border-emerald-500 cursor-pointer"
          >
            {datasets.map(d => (
              <option key={d.key} value={d.key}>{d.name}</option>
            ))}
          </select>
        </div>

        <button
          onClick={onReload}
          disabled={loading}
          className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-lg text-xs font-medium border border-slate-700 transition"
          title="Refresh Data"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
          Refresh
        </button>
      </div>
    </header>
  );
}
