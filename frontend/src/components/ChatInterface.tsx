import React, { useState } from 'react';
import { Send, Loader2, AlertCircle, CheckCircle, Shield, Sparkles } from 'lucide-react';
import { apiService } from '@/services/api';
import type { ExecutionResponse } from '@/types';
import GraphVisualization from './GraphVisualization';
import DecisionResults from './DecisionResults';

export default function ChatInterface() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [execution, setExecution] = useState<ExecutionResponse | null>(null);
    const [sessionId] = useState(() => crypto.randomUUID());

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || loading) return;

        setLoading(true);
        setError(null);
        setExecution(null);

        try {
            const result = await apiService.executeWorkflow({
                query: query.trim(),
                session_id: sessionId,
            });
            setExecution(result);
            setQuery('');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to execute workflow');
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (approved: boolean) => {
        if (!execution) return;

        try {
            await apiService.approveDecision(execution.execution_id, approved);
            const updated = await apiService.getExecutionStatus(execution.execution_id);
            setExecution(updated);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to approve decision');
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

            {/* Welcome Hero */}
            {!execution && (
                <div className="text-center py-10 space-y-4">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-100 border border-violet-200 text-violet-700 font-bold text-xs uppercase tracking-widest shadow-sm">
                        <Sparkles className="w-3 h-3" />
                        AI Enterprise Intelligence
                    </div>
                    <h1 className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-violet-800 to-gray-900 pb-2">
                        Ask complex questions.
                        <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-fuchsia-600">
                            Get intelligent decisions.
                        </span>
                    </h1>
                    <p className="text-lg text-gray-500 max-w-2xl mx-auto font-medium">
                        Five specialized AI agents collaborate to plan, research, validate, and assess compliance risks for your business.
                    </p>
                </div>
            )}

            {/* Query Input Card */}
            <div className="glass-panel p-1 relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-r from-violet-500 via-fuchsia-500 to-blue-500 opacity-20 blur-xl group-hover:opacity-30 transition duration-500" />
                <div className="relative bg-white/80 backdrop-blur-xl rounded-[1.4rem] p-6 border border-white/50 shadow-sm">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="relative">
                            <textarea
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Analyze the compliance risks in our new vendor contract..."
                                className="modern-input min-h-[140px] text-lg text-gray-800 placeholder:text-gray-400"
                                disabled={loading}
                            />
                            <div className="absolute bottom-4 right-4 text-xs font-semibold text-gray-400 bg-white/80 px-2 py-1 rounded-md border border-gray-100">
                                Groq LLaMA 3.3 70B
                            </div>
                        </div>

                        <div className="flex items-center justify-between pt-2">
                            <div className="flex items-center gap-2 text-sm font-medium text-gray-500">
                                <Shield className="w-4 h-4 text-emerald-500" />
                                <span>Enterprise Grade Security</span>
                            </div>

                            <button
                                type="submit"
                                disabled={loading || !query.trim()}
                                className="btn-primary flex items-center gap-2 group-disabled:opacity-70"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>Processing...</span>
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-5 h-5 group-hover:animate-pulse" />
                                        <span>Run Analysis</span>
                                        <Send className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            {loading && (
                <div className="max-w-2xl mx-auto text-center py-12 space-y-4">
                    <div className="relative w-24 h-24 mx-auto">
                        <div className="absolute inset-0 border-4 border-violet-100 rounded-full" />
                        <div className="absolute inset-0 border-4 border-violet-600 rounded-full border-t-transparent animate-spin" />
                        <div className="absolute inset-0 rounded-full animate-pulse bg-violet-500/10 blur-xl" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-800">Orchestrating Agents</h3>
                    <p className="text-gray-500 animate-pulse">Planner → Researcher → Validator → Risk → Decision</p>
                </div>
            )}

            {error && (
                <div className="glass-card-light bg-red-50/50 border-red-100 text-red-800 p-4 flex items-start gap-4">
                    <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <AlertCircle className="w-5 h-5 text-red-600" />
                    </div>
                    <div>
                        <h3 className="font-bold">Execution Failed</h3>
                        <p className="text-sm opacity-90 mt-1">{error}</p>
                    </div>
                </div>
            )}

            {execution && (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <GraphVisualization execution={execution} />
                    <DecisionResults execution={execution} />
                </div>
            )}
        </div>
    );
}
