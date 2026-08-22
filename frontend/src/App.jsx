import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Landing } from './pages/Landing';
import { Chat } from './pages/Chat';
import { Scale } from 'lucide-react';

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAF8F3] flex flex-col items-center justify-center text-ink font-serif-display">
        <div className="p-3 bg-ink text-paper rounded-xl shadow-md mb-3 animate-bounce">
          <Scale className="w-8 h-8 text-seal-amber" />
        </div>
        <h2 className="text-xl font-bold">Nyaya Legal Assistant</h2>
        <p className="text-xs font-code-mono text-slate-custom mt-1">Initializing authenticated session...</p>
      </div>
    );
  }

  return user ? <Chat /> : <Landing />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
