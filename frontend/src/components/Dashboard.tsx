import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, FileText, MessageSquare, Database } from 'lucide-react';
import { apiService } from '@/services/api';
import type { AnalyticsResponse } from '@/types';

export default function Dashboard() {
    const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        try {
            const data = await apiService.getAnalytics();
            setAnalytics(data);
        } catch (err) {
            console.error('Failed to load analytics:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="card">
                <p className="text-center text-gray-500">Loading analytics...</p>
            </div>
        );
    }

    if (!analytics) {
        return (
            <div className="card">
                <p className="text-center text-gray-500">Failed to load analytics</p>
            </div>
        );
    }

    const stats = [
        {
            label: 'Total Conversations',
            value: analytics.total_conversations,
            icon: MessageSquare,
            color: 'text-blue-600 bg-blue-50',
        },
        {
            label: 'Total Decisions',
            value: analytics.total_decisions,
            icon: BarChart3,
            color: 'text-purple-600 bg-purple-50',
        },
        {
            label: 'Documents',
            value: analytics.total_documents,
            icon: FileText,
            color: 'text-green-600 bg-green-50',
        },
        {
            label: 'Vector Chunks',
            value: analytics.total_chunks,
            icon: Database,
            color: 'text-orange-600 bg-orange-50',
        },
    ];

    return (
        <div className="space-y-6">
            <div className="card">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Analytics Dashboard</h2>
                <p className="text-gray-600">System metrics and performance overview</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map((stat) => {
                    const Icon = stat.icon;
                    return (
                        <div key={stat.label} className="card">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                                    <p className="text-3xl font-bold text-gray-900 mt-1">
                                        {stat.value.toLocaleString()}
                                    </p>
                                </div>
                                <div className={`p-3 rounded-lg ${stat.color}`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Average Scores */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="card bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-green-700">
                                Avg. Confidence Score
                            </p>
                            <p className="text-3xl font-bold text-green-900 mt-1">
                                {analytics.avg_confidence_score
                                    ? `${(analytics.avg_confidence_score * 100).toFixed(1)}%`
                                    : 'N/A'}
                            </p>
                        </div>
                        <TrendingUp className="w-10 h-10 text-green-600 opacity-50" />
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-yellow-700">
                                Avg. Risk Score
                            </p>
                            <p className="text-3xl font-bold text-yellow-900 mt-1">
                                {analytics.avg_risk_score
                                    ? `${(analytics.avg_risk_score * 100).toFixed(1)}%`
                                    : 'N/A'}
                            </p>
                        </div>
                        <BarChart3 className="w-10 h-10 text-yellow-600 opacity-50" />
                    </div>
                </div>
            </div>

            {/* System Info */}
            <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <dt className="text-sm font-medium text-gray-600">LLM Provider</dt>
                        <dd className="mt-1 text-lg font-semibold text-gray-900">Ollama (Local)</dd>
                    </div>
                    <div>
                        <dt className="text-sm font-medium text-gray-600">Database</dt>
                        <dd className="mt-1 text-lg font-semibold text-gray-900">SQLite</dd>
                    </div>
                    <div>
                        <dt className="text-sm font-medium text-gray-600">Vector Store</dt>
                        <dd className="mt-1 text-lg font-semibold text-gray-900">ChromaDB</dd>
                    </div>
                    <div>
                        <dt className="text-sm font-medium text-gray-600">Embedding Model</dt>
                        <dd className="mt-1 text-lg font-semibold text-gray-900">all-MiniLM-L6-v2</dd>
                    </div>
                </dl>
            </div>
        </div>
    );
}
