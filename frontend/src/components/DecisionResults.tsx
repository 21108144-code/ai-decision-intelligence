import React from 'react';
import { TrendingUp, Shield, checkCircle2, Target, Lightbulb, FileText, ChevronRight } from 'lucide-react';
import type { ExecutionResponse } from '@/types';

interface DecisionResultsProps {
    execution: ExecutionResponse;
}

export default function DecisionResults({ execution }: DecisionResultsProps) {
    const getRiskColor = (level?: string) => {
        switch (level?.toLowerCase()) {
            case 'low': return 'from-emerald-400 to-green-500';
            case 'medium': return 'from-amber-400 to-orange-500';
            case 'high': return 'from-orange-500 to-red-600';
            case 'critical': return 'from-red-600 to-rose-700';
            default: return 'from-gray-400 to-gray-500';
        }
    };

    return (
        <div className="space-y-6">
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Confidence Source */}
                <div className="glass-card p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-violet-400/20 to-fuchsia-400/20 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700" />
                    <div className="relative">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <p className="text-sm font-bold text-gray-500 uppercase tracking-wider">Confidence Score</p>
                                <p className="text-xs text-gray-400 mt-1">AI Certainty Level</p>
                            </div>
                            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-100 to-fuchsia-100 flex items-center justify-center">
                                <TrendingUp className="w-6 h-6 text-violet-600" />
                            </div>
                        </div>
                        <div className="flex items-baseline gap-2">
                            <span className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-fuchsia-600">
                                {((execution.confidence_score || 0) * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-2 mt-4 overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 transition-all duration-1000"
                                style={{ width: `${(execution.confidence_score || 0) * 100}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Risk Assessment */}
                <div className="glass-card p-6 relative overflow-hidden group">
                    <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${getRiskColor(execution.risk_level)} opacity-10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700`} />
                    <div className="relative">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <p className="text-sm font-bold text-gray-500 uppercase tracking-wider">Risk Level</p>
                                <p className="text-xs text-gray-400 mt-1">Compliance & Safety</p>
                            </div>
                            <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center">
                                <Shield className="w-6 h-6 text-gray-600" />
                            </div>
                        </div>
                        <div className="flex items-baseline gap-2">
                            <span className={`text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r ${getRiskColor(execution.risk_level)} uppercase`}>
                                {execution.risk_level || 'Unknown'}
                            </span>
                        </div>
                        <p className="mt-2 text-sm font-semibold text-gray-500">
                            Risk Score: {((execution.risk_score || 0) * 100).toFixed(0)}%
                        </p>
                    </div>
                </div>
            </div>

            {/* Final Decision */}
            <div className="glass-panel p-1">
                <div className="bg-white/80 backdrop-blur-xl rounded-[1.4rem] p-8 border border-white/50">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                            <Target className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-gray-900">Final Decision</h3>
                            <p className="text-gray-500 font-medium">Strategic recommendation based on analysis</p>
                        </div>
                    </div>
                    <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed font-medium">
                        {execution.final_decision}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recommendations */}
                {execution.recommendations && execution.recommendations.length > 0 && (
                    <div className="glass-card p-6 border-t-4 border-t-amber-400">
                        <div className="flex items-center gap-3 mb-6">
                            <Lightbulb className="w-6 h-6 text-amber-500 fill-current" />
                            <h3 className="text-xl font-bold text-gray-900">Action Plan</h3>
                        </div>
                        <ul className="space-y-4">
                            {execution.recommendations.map((rec, index) => (
                                <li key={index} className="flex gap-4 group">
                                    <span className="w-8 h-8 rounded-full bg-amber-100 text-amber-600 font-bold flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                                        {index + 1}
                                    </span>
                                    <span className="text-gray-700 font-medium pt-1">{rec}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Audit Trail */}
                {execution.agent_reasoning && (
                    <div className="glass-card p-6 border-t-4 border-t-violet-500">
                        <div className="flex items-center gap-3 mb-6">
                            <FileText className="w-6 h-6 text-violet-500" />
                            <h3 className="text-xl font-bold text-gray-900">Audit Trail</h3>
                        </div>
                        <div className="space-y-2">
                            {Object.entries(execution.agent_reasoning).map(([agent, reasoning], index) => (
                                <details key={index} className="group bg-gray-50 rounded-xl overflow-hidden border border-gray-100">
                                    <summary className="px-4 py-3 cursor-pointer flex items-center justify-between font-bold text-gray-700 hover:bg-violet-50 hover:text-violet-700 transition-colors">
                                        <span className="capitalize">{agent} Agent Analysis</span>
                                        <ChevronRight className="w-4 h-4 text-gray-400 group-open:rotate-90 transition-transform" />
                                    </summary>
                                    <div className="px-4 py-4 bg-white border-t border-gray-100 text-sm text-gray-600 leading-relaxed">
                                        {reasoning}
                                    </div>
                                </details>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
