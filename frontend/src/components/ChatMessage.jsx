import React from 'react';
import { CitationSeal } from './CitationSeal';
import { Scale, User } from 'lucide-react';

export function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const isDocMode = message.mode === 'document';

  if (isUser) {
    return (
      <div className="flex justify-end my-4 px-4 sm:px-6">
        <div className="max-w-[85%] sm:max-w-[70%] bg-[#F2ECE1] text-ink border border-[#E2DBCE] rounded-2xl rounded-tr-xs px-4 py-3 shadow-xs">
          <div className="text-xs font-code-mono text-slate-custom mb-1 flex items-center justify-end gap-1">
            <span>You</span>
            <User className="w-3 h-3 text-slate-custom" />
          </div>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message formatting
  return (
    <div className="my-6 px-4 sm:px-8 max-w-[800px] mx-auto">
      <div className="flex items-center gap-2 mb-2 pb-1 border-b border-[#E8E2D5]/60">
        <div className={`p-1.5 rounded-md ${isDocMode ? 'bg-[#E6F2F0] text-[#10504A]' : 'bg-[#FAF0D4] text-[#8C5D0F]'}`}>
          <Scale className="w-4 h-4" />
        </div>
        <span className="font-serif-display font-semibold text-sm text-ink">
          Nyaya Assistant
        </span>
        {isDocMode ? (
          <span className="text-[10px] font-code-mono px-2 py-0.5 rounded bg-[#E6F2F0] text-[#10504A] border border-[#10504A]/20">
            Document Scope
          </span>
        ) : (
          <span className="text-[10px] font-code-mono px-2 py-0.5 rounded bg-[#FAF0D4] text-[#8C5D0F] border border-[#E2D2A4]">
            Statute Citation Mode
          </span>
        )}
      </div>

      {/* Book-typeset paragraph layout (~65-75ch) */}
      <div className="prose prose-slate max-w-none text-ink text-sm sm:text-base leading-relaxed tracking-normal">
        <div className="whitespace-pre-wrap font-sans text-ink space-y-3">
          {message.content}
        </div>

        {/* Render Citation Seals if available */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 pt-3 border-t border-[#E8E2D5] bg-[#FAF8F3]/50 p-3 rounded-lg">
            <span className="block text-[11px] font-code-mono uppercase tracking-wider text-slate-custom mb-2">
              Verified Legal Sources ({message.citations.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {message.citations.map((citation, idx) => (
                <CitationSeal key={idx} citation={citation} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
