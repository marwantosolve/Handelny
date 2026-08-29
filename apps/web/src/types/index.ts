export interface Agent {
  id: string;
  org_id: string;
  kb_id: string | null;
  name: string;
  system_prompt: string | null;
  welcome_message: string | null;
  fallback_message: string | null;
  language: string;
  is_active: boolean;
  created_at: string;
}

export interface KnowledgeBase {
  id: string;
  org_id: string;
  name: string;
  status: string;
  doc_count: number;
  chunk_count: number;
  created_at: string;
}

export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'error';

export interface DocumentItem {
  id: string;
  filename: string;
  status: DocumentStatus;
  chunk_count: number;
  error_message: string | null;
}

export interface Conversation {
  id: string;
  session_id: string;
  created_at: string;
  message_count: number;
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: ChatCitation[] | null;
  created_at: string;
}

export interface ChatCitation {
  filename: string;
  page_number: number | null;
  chunk_id: string;
}
