import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Loader2 } from 'lucide-react';

export function ChatComposer({ onSend, onAttachClick, loading, activeTab, hasDocument }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [text]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || loading) return;
    onSend(text);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto p-3 sm:p-4 bg-paper">
      <div className="relative flex items-end gap-2 bg-[#FFFFFF] border border-[#D6CBB8] rounded-2xl p-2 shadow-sm focus-within:border-[#C08A2E] focus-within:ring-1 focus-within:ring-[#C08A2E] transition-all">
        <button
          type="button"
          onClick={onAttachClick}
          className={`p-2 rounded-xl text-slate-custom hover:text-ink hover:bg-[#FAF8F3] transition-colors ${
            hasDocument ? 'text-[#10504A] bg-[#E6F2F0]' : ''
          }`}
          title={hasDocument ? 'Document attached (Click to re-upload)' : 'Attach personal legal document (Mode 2)'}
        >
          <Paperclip className="w-5 h-5" />
        </button>

        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            activeTab === 'document'
              ? 'Ask a question about your uploaded document...'
              : 'Ask a question on Indian Law (e.g. data protection rules, consumer rights)...'
          }
          rows={1}
          className="flex-1 bg-transparent border-0 focus:ring-0 focus:outline-none resize-none py-1.5 px-2 text-sm text-ink placeholder:text-slate-custom/70 min-h-[40px] max-h-[160px]"
        />

        <button
          type="submit"
          disabled={!text.trim() || loading}
          className={`p-2.5 rounded-xl transition-all ${
            !text.trim() || loading
              ? 'bg-[#E5DFD3] text-slate-custom/50 cursor-not-allowed'
              : activeTab === 'document'
              ? 'bg-[#10504A] text-white hover:bg-[#0C3D38]'
              : 'bg-[#C08A2E] text-white hover:bg-[#A37424]'
          }`}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>

      <div className="flex items-center justify-between mt-2 px-2 text-[11px] font-code-mono text-slate-custom">
        <span>Press Enter to send, Shift+Enter for newline</span>
        <span className="hidden sm:inline">Nyaya Legal Assistant v1.0</span>
      </div>
    </form>
  );
}
