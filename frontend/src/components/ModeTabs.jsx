import React from 'react';
import { BookMarked, FileText, X } from 'lucide-react';

export function ModeTabs({ activeTab, setActiveTab, activeDocument, onRemoveDocument }) {
  return (
    <div className="border-b border-[#E2DBCE] bg-[#FAF8F3] px-4 pt-3 flex items-center justify-between shadow-xs select-none">
      <div className="flex items-end space-x-1 sm:space-x-2 overflow-x-auto no-scrollbar">
        {/* Mode 1: General Law Tab */}
        <button
          type="button"
          onClick={() => setActiveTab('general')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-medium rounded-t-lg transition-all duration-200 border-t border-x ${
            activeTab === 'general'
              ? 'bg-[#FFFFFF] border-[#D6CBB8] text-ink border-b-2 border-b-[#C08A2E] shadow-xs font-semibold'
              : 'bg-[#F2ECE1] border-transparent text-slate-custom hover:bg-[#EAE2D3] hover:text-ink'
          }`}
        >
          <BookMarked className={`w-4 h-4 ${activeTab === 'general' ? 'text-[#C08A2E]' : 'text-slate-custom'}`} />
          <span>General Law Q&amp;A</span>
          <span className="text-[10px] font-code-mono px-1.5 py-0.5 rounded bg-[#F2ECE1] text-[#8C5D0F] border border-[#E2D2A4]">
            Bare Acts
          </span>
        </button>

        {/* Mode 2: Uploaded Document Tab */}
        {activeDocument && (
          <div
            className={`flex items-center gap-2 px-3 py-2.5 text-xs sm:text-sm font-medium rounded-t-lg transition-all duration-200 border-t border-x animate-slideIn ${
              activeTab === 'document'
                ? 'bg-[#FFFFFF] border-[#10504A]/30 text-[#10504A] border-b-2 border-b-[#10504A] shadow-xs font-semibold'
                : 'bg-[#E6F2F0] border-transparent text-[#10504A]/80 hover:bg-[#D4E8E5]'
            }`}
          >
            <button
              type="button"
              onClick={() => setActiveTab('document')}
              className="flex items-center gap-2 text-left truncate max-w-[180px] sm:max-w-[260px]"
              title={activeDocument.filename}
            >
              <FileText className="w-4 h-4 text-[#10504A] shrink-0" />
              <span className="truncate">{activeDocument.filename}</span>
            </button>

            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onRemoveDocument();
              }}
              className="p-1 text-[#10504A]/60 hover:text-rust hover:bg-rust/10 rounded-full transition-colors ml-1"
              title="Remove document & return to General Law mode"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      <div className="hidden md:flex items-center gap-2 text-[11px] font-code-mono text-slate-custom pb-2">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span>{activeTab === 'document' ? 'Scope: Uploaded Document' : 'Scope: Central & State Acts'}</span>
      </div>
    </div>
  );
}
