/**
 * TypeScript type definitions for the application.
 */

export interface ExecuteRequest {
    query: string;
    session_id?: string;
}

export interface ExecutionResponse {
    execution_id: string;
    session_id: string;
    status: 'running' | 'completed' | 'failed' | 'awaiting_approval';
    final_decision?: string;
    confidence_score?: number;
    risk_score?: number;
    risk_level?: string;
    recommendations: string[];
    alternative_options: string[];
    citations: string[];
    agent_reasoning: Record<string, string>;
    execution_path: string[];
    started_at?: string;
    completed_at?: string;
    error_message?: string;
}

export interface DocumentUploadResponse {
    success: boolean;
    filename: string;
    file_id?: number;
    message: string;
}

export interface DocumentResponse {
    id: number;
    filename: string;
    file_type: string;
    file_size: number;
    uploaded_at: string;
    processed: boolean;
    chunk_count: number;
}

export interface ConversationResponse {
    id: number;
    session_id: string;
    title?: string;
    created_at: string;
    updated_at: string;
    message_count: number;
}

export interface AnalyticsResponse {
    total_conversations: number;
    total_decisions: number;
    total_documents: number;
    total_chunks: number;
    avg_confidence_score?: number;
    avg_risk_score?: number;
}

export interface HealthResponse {
    status: string;
    version: string;
    llm_provider: string;
    database: string;
    vector_store_chunks: number;
}
