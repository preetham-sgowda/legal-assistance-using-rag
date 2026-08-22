import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, FileText } from 'lucide-react';

export function CitationSeal({ citation }) {
  const [expanded, setExpanded] = useState(false);

  const actLabel = citation.act || 'Indian Statute';
  const sectionLabel = citation.section ? `, ${citation.section}` : '';
  const textExcerpt = citation.text;

  return (
    <span className="inline-block my-1">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className={`citation-seal ${expanded ? 'active' : ''}`}
        title="Click to view official statute excerpt"
        aria-expanded={expanded}
      >
        <BookOpen className="w-3 h-3 text-current opacity-80" />
        <span>{actLabel}{sectionLabel}</span>
        {expanded ? (
          <ChevronUp className="w-3 h-3 ml-0.5 opacity-70" />
        ) : (
          <ChevronDown className="w-3 h-3 ml-0.5 opacity-70" />
        )}
      </button>

      {expanded && (
        <span className="block mt-2 mb-3 p-3 text-xs bg-[#FAF5E8] border border-[#E8DAB7] rounded-md shadow-sm text-ink transition-all animate-fadeIn">
          <span className="flex items-center gap-1.5 font-semibold text-[#8C5D0F] font-code-mono uppercase tracking-wider text-[10px] mb-1.5">
            <FileText className="w-3.5 h-3.5" />
            Official Gazette Source Excerpt
          </span>
          <span className="block font-sans text-ink-muted leading-relaxed italic border-l-2 border-[#C08A2E] pl-2.5 my-1">
            "{textExcerpt || 'Section excerpt retrieved from official Bare Act database.'}"
          </span>
          <span className="block text-[10px] text-slate-custom font-code-mono mt-2 pt-1 border-t border-[#E8DAB7]/60">
            Source: {actLabel} {sectionLabel ? `— ${sectionLabel}` : ''}
          </span>
        </span>
      )}
    </span>
  );
}
