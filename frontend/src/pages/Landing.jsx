import React from 'react';
import { Scale, BookOpen, FileCheck, Shield, ChevronRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export function Landing() {
  const { signInWithGoogle } = useAuth();

  return (
    <div className="min-h-screen bg-[#FAF8F3] text-ink flex flex-col justify-between selection:bg-[#FAF0D4] selection:text-[#8C5D0F]">
      {/* Header */}
      <header className="border-b border-[#E2DBCE] bg-[#FAF8F3]/90 backdrop-blur-xs sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-ink text-paper rounded-lg shadow-sm">
              <Scale className="w-5 h-5 text-seal-amber" />
            </div>
            <div>
              <span className="font-serif-display font-bold text-xl text-ink">Nyaya</span>
              <span className="ml-2 text-xs font-code-mono text-slate-custom hidden sm:inline">
                Legal Assistant for Indian Citizens
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={signInWithGoogle}
            className="flex items-center gap-2 px-5 py-2.5 bg-ink text-paper rounded-xl font-medium text-sm hover:bg-ink-muted transition-colors shadow-xs"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Sign in with Google</span>
          </button>
        </div>
      </header>

      {/* Main Hero Section */}
      <main className="max-w-6xl mx-auto px-6 py-12 md:py-20 grid md:grid-cols-12 gap-12 items-center">
        {/* Left Thesis Column */}
        <div className="md:col-span-6 space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FAF0D4] border border-[#E2D2A4] text-[#8C5D0F] text-xs font-code-mono font-semibold">
            <BookOpen className="w-3.5 h-3.5" />
            <span>Citation-Backed Legal RAG</span>
          </div>

          <h1 className="font-serif-display font-bold text-3xl sm:text-4xl lg:text-5xl text-ink leading-tight">
            Indian Law, made legible to everyone.
          </h1>

          <p className="text-base sm:text-lg text-slate-custom leading-relaxed">
            Ask questions about central acts, government notifications, or upload your own rental agreement or contract for instant plain-language answers grounded strictly in law.
          </p>

          <div className="pt-2 flex flex-col sm:flex-row gap-4">
            <button
              type="button"
              onClick={signInWithGoogle}
              className="flex items-center justify-center gap-3 px-6 py-3.5 bg-[#C08A2E] text-white rounded-xl font-semibold text-base hover:bg-[#A37424] transition-all shadow-md hover:shadow-lg"
            >
              <span>Get Started Free with Google</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="pt-6 border-t border-[#E2DBCE] grid grid-cols-2 gap-4 text-xs font-code-mono text-slate-custom">
            <div className="flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-[#10504A]" />
              <span>100% Citation Grounded</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#C08A2E]" />
              <span>Session Scoped Docs</span>
            </div>
          </div>
        </div>

        {/* Right Column: Live Product Example Card */}
        <div className="md:col-span-6 bg-[#FFFFFF] border border-[#D6CBB8] rounded-2xl p-6 shadow-md relative overflow-hidden">
          <div className="flex items-center justify-between pb-4 border-b border-[#E2DBCE] mb-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#C08A2E]"></div>
              <span className="text-xs font-code-mono font-bold text-ink">Live Citation Demo</span>
            </div>
            <span className="text-[10px] font-code-mono bg-[#FAF0D4] text-[#8C5D0F] px-2 py-0.5 rounded border border-[#E2D2A4]">
              General Law Mode
            </span>
          </div>

          <div className="space-y-4 text-sm">
            {/* User Question */}
            <div className="bg-[#F2ECE1] text-ink p-3 rounded-xl rounded-tr-xs ml-auto max-w-[85%] text-xs">
              <p className="font-semibold text-[10px] text-slate-custom mb-1">Citizen question:</p>
              "What is the company's liability if my personal financial data is leaked due to their negligence?"
            </div>

            {/* AI Citation Response Mock */}
            <div className="space-y-2 text-ink">
              <div className="flex items-center gap-1.5 text-xs font-serif-display font-semibold text-ink">
                <Scale className="w-3.5 h-3.5 text-[#C08A2E]" />
                <span>Nyaya Assistant Answer:</span>
              </div>
              <p className="text-xs leading-relaxed text-slate-custom">
                Under Indian cyber law, a company that handles sensitive personal data is obligated to maintain reasonable security practices. If they are negligent causing wrongful loss to you:
              </p>
              <div className="p-3 bg-[#FAF8F3] border border-[#E2D2A4] rounded-lg text-xs">
                <p className="text-ink">
                  They are liable to pay compensation to the affected individual for damages.
                </p>
                <div className="mt-2 inline-flex items-center gap-1 bg-[#FDF6E3] border border-[#E2D2A4] text-[#8C5D0F] font-code-mono text-[11px] px-2 py-0.5 rounded-full shadow-xs">
                  <span>Section 43A, IT Act 2000</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer Disclaimer */}
      <footer className="border-t border-[#E2DBCE] bg-[#F4EFE6]/60 py-6 text-center text-xs text-slate-custom font-code-mono">
        <div className="max-w-4xl mx-auto px-4 space-y-1">
          <p className="font-semibold text-ink">Disclaimer &amp; Informational Notice</p>
          <p>
            Nyaya provides legal information grounded in statutory texts for educational purposes only. It does not constitute legal advice or formal representation.
          </p>
        </div>
      </footer>
    </div>
  );
}
