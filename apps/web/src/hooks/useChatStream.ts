'use client';

import { useCallback, useRef, useState } from 'react';
import { API_BASE_URL } from '@/lib/api';
import type { ChatCitation } from '@/types';

export type { ChatCitation };

interface ChatStreamHandlers {
  onToken: (text: string) => void;
  onCitations: (sources: ChatCitation[]) => void;
  onDone: (messageId: string) => void;
  onError?: (error: Error) => void;
}

/**
 * Streams a reply from POST /chat/{agentId}/message.
 *
 * The backend responds with a `text/event-stream` body (not a real
 * `EventSource`, since that only supports GET). We read the raw
 * `ReadableStream`, decode it, and parse `event:`/`data:` frames
 * ourselves, separated by blank lines.
 */
export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (
      agentId: string,
      sessionId: string,
      message: string,
      handlers: ChatStreamHandlers
    ): Promise<void> => {
      const controller = new AbortController();
      abortRef.current = controller;
      setIsStreaming(true);

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/v1/chat/${agentId}/message`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Accept: 'text/event-stream',
            },
            body: JSON.stringify({ session_id: sessionId, message }),
            signal: controller.signal,
          }
        );

        if (!response.ok || !response.body) {
          throw new Error(`Chat request failed with status ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          let frameEnd = buffer.indexOf('\n\n');
          while (frameEnd !== -1) {
            const frame = buffer.slice(0, frameEnd);
            buffer = buffer.slice(frameEnd + 2);
            handleFrame(frame, handlers);
            frameEnd = buffer.indexOf('\n\n');
          }
        }

        if (buffer.trim().length > 0) {
          handleFrame(buffer, handlers);
        }
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          handlers.onError?.(error);
        }
      } finally {
        setIsStreaming(false);
      }
    },
    []
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { sendMessage, cancel, isStreaming };
}

function handleFrame(frame: string, handlers: ChatStreamHandlers): void {
  const lines = frame.split('\n');
  let eventName = 'message';
  const dataLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith('event:')) {
      eventName = line.slice('event:'.length).trim();
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice('data:'.length).trim());
    }
  }

  if (dataLines.length === 0) return;

  const dataStr = dataLines.join('\n');

  try {
    const data: Record<string, unknown> = JSON.parse(dataStr);

    if (eventName === 'token' && typeof data.text === 'string') {
      handlers.onToken(data.text);
    } else if (eventName === 'citations' && Array.isArray(data.sources)) {
      handlers.onCitations(data.sources as ChatCitation[]);
    } else if (eventName === 'done' && typeof data.message_id === 'string') {
      handlers.onDone(data.message_id);
    }
  } catch {
    // Ignore malformed frames.
  }
}
