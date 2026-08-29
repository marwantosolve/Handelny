'use client';

import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import Link from 'next/link';
import { apiFetch, ApiError } from '@/lib/api';
import type { Agent } from '@/types';

const LANGUAGES = [
  { value: 'auto', label: 'Auto-detect' },
  { value: 'en', label: 'English' },
  { value: 'ar', label: 'Arabic' },
];

export default function DashboardPage() {
  const [agents, setAgents] = useState<Agent[] | null>(null);
  const [name, setName] = useState('');
  const [language, setLanguage] = useState('auto');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    void loadAgents();
  }, []);

  async function loadAgents() {
    try {
      const data = await apiFetch<Agent[]>('/agents');
      setAgents(data);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : 'Failed to load agents.'
      );
      setAgents([]);
    }
  }

  async function handleCreateAgent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const agent = await apiFetch<Agent>('/agents', {
        method: 'POST',
        body: { name, language },
      });
      setAgents([agent]);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : 'Failed to create agent.'
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (agents === null) {
    return <p className="text-sm text-slate-500">Loading agents…</p>;
  }

  const agent = agents[0] ?? null;

  if (!agent) {
    return (
      <div className="mx-auto max-w-md">
        <h1 className="text-xl font-bold text-slate-900">
          Create your agent
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Set up your first AI support agent. You can connect a knowledge
          base next.
        </p>

        <form
          onSubmit={handleCreateAgent}
          className="mt-6 space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-slate-700"
            >
              Agent name
            </label>
            <input
              id="name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Support Bot"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label
              htmlFor="language"
              className="block text-sm font-medium text-slate-700"
            >
              Language
            </label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? 'Creating…' : 'Create agent'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-900">Your agent</h1>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600">
          {error}
        </p>
      )}

      <div className="mt-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              {agent.name}
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              Language: <span className="font-medium">{agent.language}</span>
            </p>
            <p className="mt-1 text-sm text-slate-600">
              Knowledge base:{' '}
              <span className="font-medium">
                {agent.kb_id ? 'Connected' : 'Not connected yet'}
              </span>
            </p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              agent.is_active
                ? 'bg-green-100 text-green-700'
                : 'bg-slate-100 text-slate-600'
            }`}
          >
            {agent.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>

        <div className="mt-6 flex gap-3">
          <Link
            href="/dashboard/documents"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500"
          >
            Manage documents
          </Link>
          <Link
            href="/dashboard/playground"
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Open playground
          </Link>
        </div>
      </div>
    </div>
  );
}
