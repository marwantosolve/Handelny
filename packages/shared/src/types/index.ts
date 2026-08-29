export interface User {
  id: string;
  email: string;
  full_name: string;
  org_id: string;
}

export interface Organization {
  id: string;
  name: string;
}

export interface Agent {
  id: string;
  name: string;
  mode: '1' | '2' | '3';
  language: 'en' | 'ar' | 'auto';
  org_id: string;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  status: string;
  doc_count: number;
}
