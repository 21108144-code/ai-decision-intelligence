import React, { useState, useCallback } from 'react';
import { Upload, File, Trash2, CheckCircle, Loader2, AlertCircle } from 'lucide-react';
import { apiService } from '@/services/api';
import type { DocumentResponse } from '@/types';

export default function DocumentUpload() {
    const [documents, setDocuments] = useState<DocumentResponse[]>([]);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [dragActive, setDragActive] = useState(false);

    const loadDocuments = useCallback(async () => {
        try {
            const docs = await apiService.listDocuments();
            setDocuments(docs);
        } catch (err) {
            console.error('Failed to load documents:', err);
        }
    }, []);

    React.useEffect(() => {
        loadDocuments();
    }, [loadDocuments]);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await handleFiles(e.dataTransfer.files);
        }
    };

    const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            await handleFiles(e.target.files);
        }
    };

    const handleFiles = async (files: FileList) => {
        setUploading(true);
        setError(null);

        try {
            for (let i = 0; i < files.length; i++) {
                const file = files[i];

                // Upload file
                const uploadResult = await apiService.uploadDocument(file);

                // Ingest into vector store
                if (uploadResult.file_id) {
                    await apiService.ingestDocument(uploadResult.file_id);
                }
            }

            // Reload documents
            await loadDocuments();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to upload document');
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (documentId: number) => {
        if (!confirm('Are you sure you want to delete this document?')) return;

        try {
            await apiService.deleteDocument(documentId);
            await loadDocuments();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete document');
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    return (
        <div className="space-y-6">
            {/* Upload Area */}
            <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Upload Documents
                </h2>

                <div
                    className={`
            relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
            ${dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50'}
            ${uploading ? 'opacity-50 pointer-events-none' : 'hover:border-primary-400'}
          `}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        multiple
                        onChange={handleChange}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        disabled={uploading}
                        accept=".pdf,.docx,.txt,.csv,.json"
                    />

                    <div className="space-y-3">
                        {uploading ? (
                            <>
                                <Loader2 className="w-12 h-12 text-primary-600 mx-auto animate-spin" />
                                <p className="text-gray-700 font-medium">Uploading and processing...</p>
                            </>
                        ) : (
                            <>
                                <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                                <div>
                                    <p className="text-gray-700 font-medium">
                                        Drop files here or click to browse
                                    </p>
                                    <p className="text-sm text-gray-500 mt-1">
                                        Supports PDF, DOCX, TXT, CSV, JSON
                                    </p>
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {error && (
                    <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-start space-x-2">
                            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Document List */}
            <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Uploaded Documents ({documents.length})
                </h3>

                {documents.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">
                        No documents uploaded yet
                    </p>
                ) : (
                    <div className="space-y-2">
                        {documents.map((doc) => (
                            <div
                                key={doc.id}
                                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                            >
                                <div className="flex items-center space-x-3 flex-1 min-w-0">
                                    <File className="w-5 h-5 text-gray-600 flex-shrink-0" />
                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium text-gray-900 truncate">
                                            {doc.filename}
                                        </p>
                                        <p className="text-sm text-gray-500">
                                            {formatFileSize(doc.file_size)} • {doc.chunk_count} chunks
                                            {doc.processed && (
                                                <span className="ml-2 inline-flex items-center space-x-1">
                                                    <CheckCircle className="w-3 h-3 text-green-600" />
                                                    <span className="text-green-600">Processed</span>
                                                </span>
                                            )}
                                        </p>
                                    </div>
                                </div>

                                <button
                                    onClick={() => handleDelete(doc.id)}
                                    className="ml-4 p-2 text-gray-400 hover:text-red-600 transition-colors"
                                    title="Delete document"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
