import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Brain, FileText, BarChart3, MessageSquare, Sparkles, Zap } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import DocumentUpload from './components/DocumentUpload';
import Dashboard from './components/Dashboard';
import './index.css';

function App() {
    return (
        <Router>
            <div className="min-h-screen relative overflow-hidden bg-slate-50 font-sans selection:bg-violet-200 selection:text-violet-900">
                {/* Animated Background - Colorful Orbs */}
                <div className="fixed inset-0 -z-10 overflow-hidden">
                    <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-gradient-to-r from-violet-400/30 to-fuchsia-400/30 blur-[120px] animate-float" />
                    <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-gradient-to-r from-cyan-400/30 to-blue-400/30 blur-[120px] animate-float" style={{ animationDelay: '-4s' }} />
                    <div className="absolute top-[40%] left-[40%] w-[30%] h-[60%] rounded-full bg-gradient-to-r from-amber-200/20 to-orange-200/20 blur-[100px] animate-pulse-glow" />
                </div>

                <Header />

                <main className="max-w-7xl mx-auto px-4 py-8 relative z-10">
                    <Routes>
                        <Route path="/" element={<ChatInterface />} />
                        <Route path="/documents" element={<DocumentUpload />} />
                        <Route path="/analytics" element={<Dashboard />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

function Header() {
    const location = useLocation();

    return (
        <header className="sticky top-4 z-50 mx-4 lg:mx-auto max-w-7xl">
            <div className="glass-panel px-6 py-4 flex items-center justify-between">
                {/* Logo Section */}
                <div className="flex items-center gap-4">
                    <div className="relative group">
                        <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl blur opacity-40 group-hover:opacity-100 transition duration-500" />
                        <div className="relative w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-lg border border-white/50">
                            <Brain className="w-7 h-7 text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-fuchsia-600 fill-current" />
                        </div>
                        <Sparkles className="absolute -top-2 -right-2 w-5 h-5 text-yellow-400 animate-bounce" />
                    </div>

                    <div className="hidden sm:block">
                        <h1 className="text-2xl font-black tracking-tight mb-0.5">
                            <span className="bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">Decision</span>
                            <span className="bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-fuchsia-600"> Intelligence</span>
                        </h1>
                        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
                            <Zap className="w-3 h-3 text-amber-500" />
                            <span>Enterprise AI Platform</span>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex items-center gap-2 bg-gray-100/50 p-1.5 rounded-2xl border border-white/50 backdrop-blur-sm">
                    <NavLink to="/" icon={<MessageSquare />} label="Chat" active={location.pathname === '/'} />
                    <NavLink to="/documents" icon={<FileText />} label="Docs" active={location.pathname === '/documents'} />
                    <NavLink to="/analytics" icon={<BarChart3 />} label="Analytics" active={location.pathname === '/analytics'} />
                </nav>
            </div>
        </header>
    );
}

function NavLink({ to, icon, label, active }: { to: string; icon: React.ReactNode; label: string; active: boolean }) {
    return (
        <Link
            to={to}
            className={`
        relative px-4 py-2.5 rounded-xl flex items-center gap-2.5 transition-all duration-300 font-bold text-sm
        ${active
                    ? 'text-white shadow-lg scale-105'
                    : 'text-gray-500 hover:text-gray-900 hover:bg-white/50'
                }
      `}
        >
            {active && (
                <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl -z-10 animate-gradient-x" />
            )}
            {React.cloneElement(icon as React.ReactElement, {
                className: `w-4 h-4 ${active ? 'text-white' : 'text-current'}`,
                strokeWidth: 2.5
            })}
            <span>{label}</span>
        </Link>
    );
}

export default App;
