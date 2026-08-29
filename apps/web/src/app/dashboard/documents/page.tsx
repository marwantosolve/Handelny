'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { ChangeEvent, DragEvent } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch, ApiError } from '@/lib/api';
import type { Agent, DocumentItem, KnowledgeBase } from '@/types';

export default function DocumentsPage() {
  const router = useRouter();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const documentsRef = useRef<DocumentItem[]>([]);

  useEffect(() => {
    documentsRef.current = documents;
  }, [documents]);

  const loadDocuments = useCallback(async (kbId: string) => {
    try {
      const docs = await apiFetch<DocumentItem[]>(
        `/knowledge-bases/${kbId}/documents`
      );
      setDocuments(docs);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : 'Failed to load documents.'
      );
    }
  }, []);

  useEffect(() => {
    async function initialize() {
      try {
        const agents = await apiFetch<Agent[]>('/agents');
        const firstAgent = agents[0];

        if (!firstAgent) {
          router.replace('/dashboard');
          return;
        }

        let currentAgent = firstAgent;

        if (!currentAgent.kb_id) {
          const kb = await apiFetch<KnowledgeBase>('/knowledge-bases', {
            method: 'POST',
            body: { name: `${currentAgent.name} Knowledge Base` },
          });

          currentAgent = await apiFetch<Agent>(`/agents/${currentAgent.id}`, {
            method: 'PATCH',
            body: { kb_id: kb.id },
          });
        }

        setAgent(currentAgent);
        if (currentAgent.kb_id) {
          await loadDocuments(currentAgent.kb_id);
        }
      } catch (err) {
        setError(
          err instanceof ApiError ? err.message : 'Failed to load documents.'
        );
      } finally {
        setIsLoading(false);
      }
    }

    void initialize();
  }, [router, loadDocuments]);

  // Poll every 3s while any document is pending/processing.
  useEffect(() => {
    if (!agent?.kb_id) return;
    const kbId = agent.kb_id;

    const interval = setInterval(() => {
      const hasPending = documentsRef.current.some(
        (doc) => doc.status === 'pending' || doc.status === 'processing'
      );
      if (hasPending) {
        void loadDocuments(kbId);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [agent?.kb_id, loadDocuments]);

  async function uploadFile(file: File) {
    if (!agent?.kb_id) return;
    setError(null);
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      await apiFetch(`/knowledge-bases/${agent.kb_id}/documents`, {
        method: 'POST',
        body: formData,
      });

      await loadDocuments(agent.kb_id);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : 'Failed to upload file.'
      );
    } finally {
      setIsUploading(false);
    }
  }

  function handleFileInputChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) void uploadFile(file);
    event.target.value = '';
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) void uploadFile(file);
  }

  async function handleDelete(documentId: string) {
    if (!agent?.kb_id) return;

    try {
      await apiFetch(`/documents/${documentId}`, { method: 'DELETE' });
      await loadDocuments(agent.kb_id);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : 'Failed to delete document.'
      );
    }
  }

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading…</p>;
  }

  if (!agent) {
    return null;
  }

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-900">Documents</h1>
      <p className="mt-1 text-sm text-slate-600">
        Upload documents to power {agent.name}&apos;s knowledge base.
      </p>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600">
          {error}
        </p>
      )}

      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`mt-6 cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
          isDragging
            ? 'border-indigo-400 bg-indigo-50'
            : 'border-slate-300 bg-white'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md"
          className="hidden"
          onChange={handleFileInputChange}
        />
        <p className="text-sm font-medium text-slate-700">
          {isUploading
            ? 'Uploading…'
            : 'Drag & drop a file here, or click to browse'}
        </p>
        <p className="mt-1 text-xs text-slate-500">
          Supports PDF, TXT, and Markdown files.
        </p>
      </div>

      <div className="mt-8 overflow-hidden rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Filename</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Chunks</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {documents.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-slate-500">
                  No documents yet.
                </td>
              </tr>
            )}
            {documents.map((doc) => (
              <tr key={doc.id} className="border-b border-slate-100 last:border-0">
                <td className="px-4 py-3 font-medium text-slate-900">
                  {doc.filename}
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={doc.status} />
                </td>
                <td className="px-4 py-3 text-slate-600">
                  {doc.chunk_count}
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="text-sm font-medium text-red-600 hover:text-red-500"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    processing: 'bg-blue-100 text-blue-700',
    ready: 'bg-green-100 text-green-700',
    error: 'bg-red-100 text-red-700',
  };

  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-medium ${
        styles[status] ?? 'bg-slate-100 text-slate-600'
      }`}
    >
      {status}
    </span>
  );
}
