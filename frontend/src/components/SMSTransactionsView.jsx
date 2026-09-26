import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, ShieldAlert, CheckCircle2, AlertTriangle, 
  HelpCircle, ArrowDownLeft, ArrowUpRight, Search, Filter, 
  Eye, Check, X, RefreshCw, Send, Smartphone, Lock
} from 'lucide-react';

const DEMO_SMS_PRESETS = [
  { label: "🛒 Amazon UPI Debit", text: "Rs.850 debited from A/c XX1234 for AMAZON via UPI. Ref 987654321." },
  { label: "💰 Salary Credit", text: "Rs. 5000.00 credited to A/c XX4321 from CLIENT PAYOUT on 2026-09-20. Ref TXN112233." },
  { label: "🏦 ATM Cash Withdrawal", text: "Rs.2000 cash withdrawn at HDFC ATM using Debit Card XX5678 on 2026-09-21." },
  { label: "🚨 Fake KYC Scam", text: "Your HDFC account will be blocked today! Click http://bit.ly/fake-kyc to verify PAN immediately." },
  { label: "🔐 Private OTP Code", text: "Your OTP for login is 987654. Do not share your OTP with anyone." }
];

export default function SMSTransactionsView({ onReloadMain }) {
  const [smsData, setSmsData] = useState(null);
  const [inputSms, setInputSms] = useState('');
  const [sender, setSender] = useState('BANK-SMS');
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState('All');
  const [search, setSearch] = useState('');
  const [selectedSMS, setSelectedSMS] = useState(null); // Detail Modal
  const [actionMsg, setActionMsg] = useState('');

  const fetchSMSLogs = () => {
    fetch('/api/sms/transactions')
      .then(res => res.json())
      .then(data => setSmsData(data))
      .catch(err => console.error("Error fetching SMS logs:", err));
  };

  useEffect(() => {
    fetchSMSLogs();
  }, []);

  const handleProcessSMS = (e) => {
    if (e) e.preventDefault();
    if (!inputSms.trim()) return;
    setLoading(true);
    setActionMsg('');

    fetch('/api/sms/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sms_text: inputSms, sender: sender || 'BANK-SMS' })
    })
      .then(res => res.json())
      .then(data => {
        setActionMsg(`Result: ${data.status} - ${data.message}`);
        setInputSms('');
        fetchSMSLogs();
        if (onReloadMain) onReloadMain();
      })
      .catch(err => setActionMsg('Error processing SMS: ' + err.message))
      .finally(() => setLoading(false));
  };

  const handleConfirmSMS = (smsId, action) => {
    fetch('/api/sms/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sms_id: smsId, action })
    })
      .then(res => res.json())
      .then(() => {
        setSelectedSMS(null);
        fetchSMSLogs();
        if (onReloadMain) onReloadMain();
      });
  };

  if (!smsData) {
    return <div className="p-8 text-center text-slate-400">Loading Smart SMS Transaction Agent...</div>;
  }

  const { summary, sms_logs } = smsData;

  const filteredLogs = sms_logs.filter(log => {
    const matchStatus = filterStatus === 'All' || log.status === filterStatus || log.payment_mode === filterStatus || log.type === filterStatus.toLowerCase();
    const matchSearch = !search || log.sms_text.toLowerCase().includes(search.toLowerCase()) || log.merchant.toLowerCase().includes(search.toLowerCase()) || log.sender.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="font-bold text-slate-100 flex items-center gap-2 text-base">
              <Smartphone className="h-5 w-5 text-emerald-400" />
              Smart SMS Transaction Agent & Scam Detection
            </h3>
            <p className="text-xs text-slate-400">
              Automatic SMS transaction parsing, privacy redaction of OTPs/PINs, and multi-signal scam detection.
            </p>
          </div>
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
            <Lock className="h-3.5 w-3.5" /> Privacy Protected
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <div className="text-slate-400 text-[11px] font-medium">Total SMS</div>
          <div className="text-2xl font-bold text-white">{summary.total_sms}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <div className="text-slate-400 text-[11px] font-medium">Verified Txns</div>
          <div className="text-2xl font-bold text-emerald-400">{summary.verified_count}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <div className="text-slate-400 text-[11px] font-medium">Suspicious SMS</div>
          <div className="text-2xl font-bold text-rose-400">{summary.suspicious_count}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <div className="text-slate-400 text-[11px] font-medium">Expenses Detected</div>
          <div className="text-2xl font-bold text-white">${summary.expenses_detected.toLocaleString()}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <div className="text-slate-400 text-[11px] font-medium">Online Spend (UPI/Card)</div>
          <div className="text-2xl font-bold text-accent">${summary.online_spending.toLocaleString()}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <div className="text-slate-400 text-[11px] font-medium">Cash Spend (ATM/CDM)</div>
          <div className="text-2xl font-bold text-amber-400">${summary.cash_spending.toLocaleString()}</div>
        </div>
      </div>

      {/* Live "Paste SMS" Development & Demo Input Box */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
            <MessageSquare className="h-4 w-4 text-emerald-400" />
            Live "Paste SMS" Tester & Mobile Receiver
          </h4>
          <span className="text-[11px] text-slate-400">Simulate incoming bank SMS in real-time</span>
        </div>

        {/* Quick Preset Buttons */}
        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-slate-400 font-semibold self-center">Try Preset:</span>
          {DEMO_SMS_PRESETS.map((p, i) => (
            <button
              key={i}
              type="button"
              onClick={() => { setInputSms(p.text); setSender('HDFCBK-SMS'); }}
              className="text-[11px] bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 px-2.5 py-1 rounded-lg transition"
            >
              {p.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleProcessSMS} className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              type="text"
              placeholder="Sender (e.g., HDFCBK, AXISBK)"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
            />
            <input
              type="text"
              placeholder="Paste raw SMS text received on phone..."
              value={inputSms}
              onChange={(e) => setInputSms(e.target.value)}
              className="md:col-span-3 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            <span className="text-xs text-slate-400">
              * Sensitive OTPs and PINs are automatically redacted before storage.
            </span>
            <button
              type="submit"
              disabled={loading || !inputSms.trim()}
              className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 transition disabled:opacity-50"
            >
              <Send className="h-3.5 w-3.5" />
              Process Incoming SMS
            </button>
          </div>
        </form>

        {actionMsg && (
          <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs font-semibold text-emerald-400">
            {actionMsg}
          </div>
        )}
      </div>

      {/* SMS Logs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="font-bold text-slate-100 text-base">Processed SMS Stream</h3>
            <p className="text-xs text-slate-400">Showing {filteredLogs.length} logs</p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search SMS..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 w-44"
              />
            </div>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-emerald-400 font-semibold focus:outline-none"
            >
              <option value="All">All Logs</option>
              <option value="VERIFIED_TRANSACTION">Verified Txns</option>
              <option value="SUSPICIOUS">Suspicious Scams</option>
              <option value="UNKNOWN">Requires Review</option>
              <option value="UPI">UPI</option>
              <option value="CARD">Card</option>
              <option value="ATM">ATM / Cash</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Date / Time</th>
                <th className="py-3 px-4">Merchant / Payee</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Payment Mode</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Classification</th>
                <th className="py-3 px-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No SMS logs found matching filters. Try processing a test SMS above!
                  </td>
                </tr>
              ) : (
                filteredLogs.map(log => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">{log.date_processed}</td>
                    <td className="py-3 px-4 font-semibold text-white">
                      {log.merchant}
                      {log.reference_id && <span className="ml-1 text-[10px] text-slate-500 font-normal">(Ref: {log.reference_id})</span>}
                    </td>
                    <td className={`py-3 px-4 font-bold text-sm ${log.type === 'income' ? 'text-emerald-400' : 'text-slate-100'}`}>
                      {log.amount > 0 ? (log.type === 'income' ? `+$${log.amount.toFixed(2)}` : `-$${log.amount.toFixed(2)}`) : '$0.00'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px] uppercase font-bold">
                        {log.payment_mode}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800 text-[11px]">
                        {log.category}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {log.status === 'VERIFIED_TRANSACTION' && (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 text-[11px]">
                          <CheckCircle2 className="h-3 w-3" /> Verified
                        </span>
                      )}
                      {log.status === 'SUSPICIOUS' && (
                        <span className="inline-flex items-center gap-1 text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20 text-[11px]">
                          <AlertTriangle className="h-3 w-3" /> Suspicious
                        </span>
                      )}
                      {log.status === 'UNKNOWN' && (
                        <span className="inline-flex items-center gap-1 text-amber-400 font-semibold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 text-[11px]">
                          <HelpCircle className="h-3 w-3" /> Review Required
                        </span>
                      )}
                      {log.status === 'NON_TRANSACTION' && (
                        <span className="text-slate-500 text-[11px]">Non-Financial</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => setSelectedSMS(log)}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] font-semibold flex items-center gap-1 mx-auto transition"
                      >
                        <Eye className="h-3 w-3" /> Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedSMS && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl relative">
            <button
              onClick={() => setSelectedSMS(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>

            <h3 className="font-bold text-lg text-white flex items-center gap-2">
              <Smartphone className="h-5 w-5 text-emerald-400" />
              SMS Transaction Details
            </h3>

            {/* Original & Sanitized SMS */}
            <div className="space-y-2">
              <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Sanitized Original SMS Text</label>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-200 leading-relaxed font-mono">
                {selectedSMS.sanitized_text}
              </div>
            </div>

            {/* Extracted Data Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Extracted Amount</span>
                <span className="font-bold text-sm text-white">${selectedSMS.amount.toFixed(2)}</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Merchant / Payee</span>
                <span className="font-bold text-sm text-white">{selectedSMS.merchant}</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Payment Mode</span>
                <span className="font-semibold text-emerald-400">{selectedSMS.payment_mode}</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Confidence Score</span>
                <span className="font-semibold text-white">{(selectedSMS.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>

            {/* Suspicious Reasons list if any */}
            {selectedSMS.suspicious_reasons && selectedSMS.suspicious_reasons.length > 0 && (
              <div className="p-3 bg-rose-950/40 border border-rose-500/30 text-rose-200 text-xs rounded-xl space-y-1">
                <div className="font-bold flex items-center gap-1.5 text-rose-400">
                  <AlertTriangle className="h-4 w-4" /> Fraud Risk Signals Identified:
                </div>
                {selectedSMS.suspicious_reasons.map((r, i) => (
                  <div key={i}>• {r}</div>
                ))}
              </div>
            )}

            {/* Confirmation Actions */}
            {(selectedSMS.status === 'SUSPICIOUS' || selectedSMS.status === 'UNKNOWN') && (
              <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3">
                <button
                  onClick={() => handleConfirmSMS(selectedSMS.id, 'reject')}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg"
                >
                  Dismiss / Reject
                </button>
                <button
                  onClick={() => handleConfirmSMS(selectedSMS.id, 'approve')}
                  className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 text-xs font-bold rounded-lg"
                >
                  Approve as Financial Record
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
