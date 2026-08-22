import React from 'react';
import { MessageSquarePlus, History, LogOut, Scale, Trash2, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export function Sidebar({
  sessionsList,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  isOpen,
  onClose,
}) {
  const { user, signOut } = useAuth();

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-ink/40 backdrop-blur-xs z-40 md:hidden"
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-72 bg-[#FAF8F3] border-r border-[#E2DBCE] flex flex-col justify-between transition-transform duration-200 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Top Branding & New Chat */}
        <div className="p-4 border-b border-[#E2DBCE]">
          <div className="flex items-center gap-2.5 mb-4">
            <div className="p-2 bg-ink text-paper rounded-lg shadow-sm">
              <Scale className="w-5 h-5 text-seal-amber" />
            </div>
            <div>
              <h1 className="font-serif-display font-bold text-lg text-ink leading-none">Nyaya</h1>
              <p className="text-[11px] font-code-mono text-slate-custom mt-0.5">Legal Assistant for India</p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => {
              onNewChat();
              if (onClose) onClose();
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-ink text-paper rounded-xl font-medium text-sm hover:bg-ink-muted transition-colors shadow-xs"
          >
            <MessageSquarePlus className="w-4 h-4 text-seal-amber" />
            <span>New Conversation</span>
          </button>
        </div>

        {/* History Session List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <div className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-code-mono text-slate-custom uppercase tracking-wider">
            <History className="w-3.5 h-3.5" />
            <span>Chat History</span>
          </div>

          {sessionsList.length === 0 ? (
            <p className="text-xs text-slate-custom px-3 py-4 text-center italic font-serif-display">
              No past conversations yet. Ask a question to begin.
            </p>
          ) : (
            sessionsList.map((s) => {
              const isSelected = s.id === currentSessionId;
              return (
                <div
                  key={s.id}
                  className={`group relative flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-[#F2ECE1] text-ink font-semibold border-l-3 border-[#C08A2E]'
                      : 'text-slate-custom hover:bg-[#F5F0E6] hover:text-ink'
                  }`}
                  onClick={() => {
                    onSelectSession(s.id);
                    if (onClose) onClose();
                  }}
                >
                  <span className="truncate pr-4">{s.title || 'Conversation'}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(s.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-custom hover:text-rust rounded transition-opacity"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* User Profile & Sign Out Footer */}
        <div className="p-4 border-t border-[#E2DBCE] bg-[#F4EFE6]/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 overflow-hidden">
              {user?.user_metadata?.avatar_url ? (
                <img
                  src={user.user_metadata.avatar_url}
                  alt={user.email}
                  className="w-8 h-8 rounded-full border border-[#D6CBB8]"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-[#E2DBCE] text-ink flex items-center justify-center font-bold text-xs">
                  <User className="w-4 h-4 text-ink" />
                </div>
              )}
              <div className="truncate">
                <p className="text-xs font-semibold text-ink truncate">
                  {user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'Citizen'}
                </p>
                <p className="text-[10px] text-slate-custom truncate">{user?.email}</p>
              </div>
            </div>

            <button
              type="button"
              onClick={signOut}
              className="p-2 text-slate-custom hover:text-rust rounded-lg hover:bg-rust/10 transition-colors"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
