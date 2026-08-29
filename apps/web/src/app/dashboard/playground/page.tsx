'use client';

import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch, ApiError } from '@/lib/api';
import { useChatStream } from '@/hooks/useChatStream';
import type { Agent, ChatCitation } from '@/types';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatCitation[];
}

const SESSION_KEY = 'handelny_playground_session_id';

export default function PlaygroundPage() {
  const router = useRouter();
  const { sendMessage, isStreaming } = useChatStream();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string>('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function initialize() {
      try {
        const agents = await apiFetch<Agent[]>('/agents');
        const firstAgent = agents[0];

        if (!firstAgent) {
          router.replace('/dashboard');
          return;
        }

        setAgent(firstAgent);

        let sessionId = window.sessionStorage.getItem(SESSION_KEY);
        if (!sessionId) {
          sessionId = crypto.randomUUID();
          window.sessionStorage.setItem(SESSION_KEY, sessionId);
        }
        sessionIdRef.current = sessionId;
      } catch (err) {
        setError(
          err instanceof ApiError ? err.message : 'Failed to load agent.'
        );
      } finally {
        setIsLoading(false);
      }
    }

    void initialize();
  }, [router]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!agent || !input.trim() || isStreaming) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
    };
    const assistantId = crypto.randomUUID();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput('');
    setError(null);

    await sendMessage(agent.id, sessionIdRef.current, userMessage.content, {
      onToken: (text) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId
              ? { ...msg, content: msg.content + text }
              : msg
          )
        );
      },
      onCitations: (sources) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId ? { ...msg, sources } : msg
          )
        );
      },
      onDone: () => {
        // Message content is already fully streamed into place.
      },
      onError: () => {
        setError('Something went wrong while streaming the response.');
      },
    });
  }

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading…</p>;
  }

  if (!agent) {
    return null;
  }

  return (
    <div className="flex h-[70vh] flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-6 py-4">
        <h1 className="text-lg font-semibold text-slate-900">Playground</h1>
        <p className="text-sm text-slate-500">Chatting with {agent.name}</p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-6 py-4">
        {messages.length === 0 && (
          <p className="text-sm text-slate-400">
            Send a message to see how {agent.name} responds.
          </p>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
                message.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content || '…'}</p>
              {message.sources && message.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {message.sources.map((source, index) => (
                    <span
                      key={`${source.chunk_id}-${index}`}
                      className="rounded-full bg-white px-2 py-0.5 text-xs font-medium text-slate-600 shadow-sm"
                    >
                      {source.filename}
                      {source.page_number != null
                        ? ` · p.${source.page_number}`
                        : ''}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={scrollRef} />
      </div>

      {error && (
        <p className="border-t border-slate-100 px-6 py-2 text-sm text-red-600">
          {error}
        </p>
      )}

      <form
        onSubmit={handleSend}
        className="flex items-center gap-3 border-t border-slate-200 px-6 py-4"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question…"
          disabled={isStreaming}
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Send
        </button>
      </form>
    </div>
  );
}
