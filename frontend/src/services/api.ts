/**
 * API service for backend communication.
 */
import axios from 'axios';
import type {
    ExecuteRequest,
    ExecutionResponse,
    DocumentUploadResponse,
    DocumentResponse,
    ConversationResponse,
    AnalyticsResponse,
    HealthResponse,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const apiService = {
    // Graph execution
    async executeWorkflow(request: ExecuteRequest): Promise<ExecutionResponse> {
        const response = await api.post<ExecutionResponse>('/api/execute', request);
        return response.data;
    },

    async getExecutionStatus(executionId: string): Promise<ExecutionResponse> {
        const response = await api.get<ExecutionResponse>(`/api/execution/${executionId}`);
        return response.data;
    },

    async approveDecision(executionId: string, approved: boolean, feedback?: string): Promise<void> {
        await api.post(`/api/execution/${executionId}/approve`, { approved, feedback });
    },

    // Documents
    async uploadDocument(file: File): Promise<DocumentUploadResponse> {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post<DocumentUploadResponse>('/api/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    async ingestDocument(fileId: number): Promise<any> {
        const response = await api.post('/api/documents/ingest', { file_id: fileId });
        return response.data;
    },

    async listDocuments(): Promise<DocumentResponse[]> {
        const response = await api.get<DocumentResponse[]>('/api/documents/');
        return response.data;
    },

    async deleteDocument(documentId: number): Promise<void> {
        await api.delete(`/api/documents/${documentId}`);
    },

    async getDocumentStats(): Promise<any> {
        const response = await api.get('/api/documents/stats');
        return response.data;
    },

    // Conversations
    async listConversations(): Promise<ConversationResponse[]> {
        const response = await api.get<ConversationResponse[]>('/api/conversations/');
        return response.data;
    },

    async getConversation(conversationId: number): Promise<ConversationResponse> {
        const response = await api.get<ConversationResponse>(`/api/conversations/${conversationId}`);
        return response.data;
    },

    // Analytics
    async getAnalytics(): Promise<AnalyticsResponse> {
        const response = await api.get<AnalyticsResponse>('/api/analytics/metrics');
        return response.data;
    },

    async getRecentDecisions(limit: number = 10): Promise<any[]> {
        const response = await api.get(`/api/analytics/decisions/recent?limit=${limit}`);
        return response.data;
    },

    // Health
    async healthCheck(): Promise<HealthResponse> {
        const response = await api.get<HealthResponse>('/health');
        return response.data;
    },
};
