import React, { useState } from 'react';
import { MessageSquare, Send, Sparkles, User, Bot, HelpCircle } from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  "Where did I spend the most this month?",
  "Which subscriptions am I paying for?",
  "What expenses increased compared with last month?",
  "How much of my budget is already committed?"
];

export default function FinPilotChat() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "Hello! I'm **FinPilot**, your AI financial decision-support agent. Ask me any question about your spending, recurring bills, budget, or financial goals!",
      suggestedFollowups: SUGGESTED_QUESTIONS
    }
  ]);

  const handleSend = (questionText) => {
    const query = questionText || input;
    if (!query.trim()) return;

    // Add user message
    const newMsgs = [...messages, { sender: 'user', text: query }];
    setMessages(newMsgs);
    if (!questionText) setInput('');
    setLoading(true);

    fetch('/api/qa/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: query })
    })
      .then(res => res.json())
      .then(data => {
        setMessages([...newMsgs, {
          sender: 'bot',
          text: data.answer,
          suggestedFollowups: data.suggested_followups
        }]);
      })
      .catch(err => {
        setMessages([...newMsgs, {
          sender: 'bot',
          text: 'Sorry, I encountered an error answering your query: ' + err.message
        }]);
      })
      .finally(() => setLoading(false));
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col h-[650px]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div>
          <h3 className="font-bold text-slate-100 flex items-center gap-2 text-base">
            <Sparkles className="h-5 w-5 text-emerald-400" />
            FinPilot Natural Language Assistant
          </h3>
          <p className="text-xs text-slate-400">Ask natural-language questions about your financial statements</p>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.sender === 'bot' && (
              <div className="h-8 w-8 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4" />
              </div>
            )}

            <div className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed space-y-3 ${
              msg.sender === 'user' 
                ? 'bg-emerald-500 text-slate-950 font-medium rounded-tr-none' 
                : 'bg-slate-950 text-slate-200 border border-slate-800 rounded-tl-none'
            }`}>
              <div 
                className="whitespace-pre-line"
                dangerouslySetInnerHTML={{ __html: formatMarkdownText(msg.text) }}
              />

              {/* Followup suggested chips */}
              {msg.suggestedFollowups && msg.suggestedFollowups.length > 0 && (
                <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                  <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1">
                    <HelpCircle className="h-3 w-3 text-emerald-400" /> Suggested Questions:
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.suggestedFollowups.map((q, i) => (
                      <button
                        key={i}
                        onClick={() => handleSend(q)}
                        className="text-[11px] bg-slate-900 hover:bg-slate-800 text-emerald-400 border border-emerald-500/30 px-2.5 py-1 rounded-full transition text-left"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="h-8 w-8 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center flex-shrink-0">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 items-center text-xs text-slate-400 p-2">
            <div className="h-6 w-6 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <Bot className="h-3.5 w-3.5 animate-pulse" />
            </div>
            <span>FinPilot is analyzing your financial records...</span>
          </div>
        )}
      </div>

      {/* Input box */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="mt-4 flex gap-2 pt-3 border-t border-slate-800">
        <input
          type="text"
          placeholder="Ask e.g. 'Where did I spend the most this month?' or 'Which subscriptions am I paying for?'"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-emerald-500"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-5 py-3 rounded-xl text-xs flex items-center gap-1.5 transition disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
          Ask
        </button>
      </form>
    </div>
  );
}

// Simple markdown formatter helper for chat
function formatMarkdownText(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-white">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="italic text-slate-300">$1</em>');
}
