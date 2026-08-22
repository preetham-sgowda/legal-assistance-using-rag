import React, { useState, useRef, useEffect } from 'react';
import { Menu, Scale, ShieldAlert, Sparkles, BookMarked, FileText } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { ModeTabs } from '../components/ModeTabs';
import { ChatMessage } from '../components/ChatMessage';
import { ChatComposer } from '../components/ChatComposer';
import { DocumentUpload } from '../components/DocumentUpload';
import { useChat } from '../hooks/useChat';

export function Chat() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showUploadZone, setShowUploadZone] = useState(false);
  const messagesEndRef = useRef(null);

  const {
    currentSessionId,
    messages,
    loading,
    activeDocument,
    sessionsList,
    activeTab,
    setActiveTab,
    startNewChat,
    loadSession,
    sendMessage,
    uploadDocument,
    removeDocument,
    deleteSession,
  } = useChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleFileUpload = async (file) => {
    setShowUploadZone(false);
    await uploadDocument(file);
  };

  return (
    <div className="flex h-screen bg-[#FAF8F3] text-ink overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        sessionsList={sessionsList}
        currentSessionId={currentSessionId}
        onSelectSession={loadSession}
        onNewChat={startNewChat}
        onDeleteSession={deleteSession}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Navbar */}
        <header className="h-14 border-b border-[#E2DBCE] bg-[#FAF8F3] px-4 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 text-slate-custom hover:text-ink md:hidden rounded-lg hover:bg-[#F2ECE1]"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-[#C08A2E]" />
              <h2 className="font-serif-display font-semibold text-sm sm:text-base text-ink">
                Nyaya Assistant
              </h2>
            </div>
          </div>

          <div className="text-xs font-code-mono text-slate-custom flex items-center gap-2">
            <span className="hidden sm:inline">Persisted Citation Database</span>
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          </div>
        </header>

        {/* Mode Tabs (Signature Physical Book Divider Tabs) */}
        <ModeTabs
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          activeDocument={activeDocument}
          onRemoveDocument={removeDocument}
        />

        {/* Persistent Legal Disclaimer Banner */}
        <div className="bg-[#FAF0D4]/80 border-b border-[#E2D2A4] px-4 py-1.5 text-[11px] text-[#8C5D0F] font-code-mono text-center shrink-0">
          ⚖️ Informational legal assistant only. Citation-backed responses do not constitute legal advice.
        </div>

        {/* Chat Message Thread */}
        <div className="flex-1 overflow-y-auto px-2 sm:px-4 py-4 space-y-4">
          {/* Document Upload Zone toggleable */}
          {showUploadZone && !activeDocument && (
            <DocumentUpload onFileUpload={handleFileUpload} isUploading={loading} />
          )}

          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 max-w-xl mx-auto my-auto">
              <div className="p-4 bg-[#FAF0D4] text-[#8C5D0F] rounded-2xl mb-4 border border-[#E2D2A4]">
                <Scale className="w-8 h-8" />
              </div>
              <h3 className="font-serif-display font-bold text-xl sm:text-2xl text-ink mb-2">
                Ask a Legal Question or Attach a Document
              </h3>
              <p className="text-sm text-slate-custom leading-relaxed mb-6">
                Nyaya answers questions on Indian law with verifiable section citations, or analyzes personal legal documents in strict confidence.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left w-full max-w-md">
                <button
                  type="button"
                  onClick={() => sendMessage('What are the penalties for data breach under the IT Act 2000?')}
                  className="p-3 bg-white border border-[#D6CBB8] rounded-xl text-xs text-ink hover:border-[#C08A2E] hover:bg-[#FAF8F3] transition-all"
                >
                  <span className="font-semibold block mb-1 font-code-mono text-[#8C5D0F]">IT Act Sample:</span>
                  "What are the penalties for data breach under IT Act?"
                </button>
                <button
                  type="button"
                  onClick={() => sendMessage('What rights does a consumer have against defective products under Consumer Protection Act 2019?')}
                  className="p-3 bg-white border border-[#D6CBB8] rounded-xl text-xs text-ink hover:border-[#C08A2E] hover:bg-[#FAF8F3] transition-all"
                >
                  <span className="font-semibold block mb-1 font-code-mono text-[#8C5D0F]">Consumer Law:</span>
                  "Rights against defective products under 2019 Act?"
                </button>
              </div>
            </div>
          ) : (
            messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
          )}

          {loading && (
            <div className="flex items-center gap-3 my-4 px-8 max-w-[800px] mx-auto text-xs font-code-mono text-slate-custom animate-pulse">
              <div className="w-2 h-2 rounded-full bg-[#C08A2E]"></div>
              <span>Searching statutes &amp; generating citation-backed response...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Composer */}
        <div className="border-t border-[#E2DBCE] bg-[#FAF8F3] shrink-0">
          <ChatComposer
            onSend={sendMessage}
            onAttachClick={() => setShowUploadZone(!showUploadZone)}
            loading={loading}
            activeTab={activeTab}
            hasDocument={!!activeDocument}
          />
        </div>
      </div>
    </div>
  );
}
