# API Specification

Base URL: `https://api.handelny.com/api/v1`

## 1. Authentication APIs

### Register
`POST /auth/register` (Public)
```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "Ahmed Admin",
  "org_name": "Acme Corp"
}

// Response (201 Created)
{
  "user": { "id": "uuid", "email": "user@example.com" },
  "organization": { "id": "uuid", "name": "Acme Corp" },
  "access_token": "jwt...",
  "refresh_token": "jwt..."
}
```

### Login
`POST /auth/login` (Public)
```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

// Response (200 OK)
{
  "access_token": "jwt...",
  "refresh_token": "jwt..."
}
```

## 2. Agent APIs

### Create Agent
`POST /agents` (Auth: Admin)
```json
// Request
{
  "name": "Customer Support Bot",
  "mode": "2",
  "language": "auto",
  "system_prompt": "You are a helpful assistant for Acme Corp."
}

// Response (201 Created)
{
  "id": "agent_uuid",
  "name": "Customer Support Bot",
  "mode": "2",
  "status": "active"
}
```

### Get Agent Embed Code
`GET /agents/{id}/embed-code` (Auth: Member)
```json
// Response (200 OK)
{
  "script_tag": "<script src=\"https://cdn.handelny.com/widget.js\" data-agent=\"agent_uuid\"></script>"
}
```

## 3. Knowledge Base & Document APIs

### Upload Document
`POST /knowledge-bases/{kb_id}/documents` (Auth: Admin, Multipart Form)
*   **Headers:** `Content-Type: multipart/form-data`
*   **Body:** `file` (binary PDF/DOCX)

```json
// Response (202 Accepted)
{
  "id": "doc_uuid",
  "filename": "policies.pdf",
  "status": "pending"
}
```

### Poll Document Status
`GET /documents/{id}/status` (Auth: Member)
```json
// Response (200 OK)
{
  "id": "doc_uuid",
  "status": "ready", // pending, processing, ready, error
  "chunk_count": 145
}
```

## 4. Chat APIs

### Send Message (Streaming)
`POST /chat/{agent_id}/message` (Public Widget / Auth Playground)
```json
// Request
{
  "session_id": "session_123",
  "message": "What is the refund policy?"
}
```

**Response (200 OK - `text/event-stream`)**
```text
event: token
data: {"text": "You "}

event: token
data: {"text": "can "}

event: token
data: {"text": "refund "}

event: citations
data: {"sources": [{"doc": "policies.pdf", "page": 4}]}

event: done
data: {"message_id": "msg_uuid"}
```

## 5. Feedback & Analytics APIs

### Submit Feedback
`POST /messages/{id}/feedback` (Public)
```json
// Request
{
  "rating": "thumbs_down",
  "comment": "The answer was outdated."
}

// Response (201 Created)
{
  "status": "success"
}
```

### Get Overview Analytics
`GET /analytics/overview?days=30` (Auth: Admin)
```json
// Response (200 OK)
{
  "total_conversations": 1450,
  "total_messages": 8340,
  "avg_latency_ms": 1200,
  "estimated_cost_usd": 4.50
}
```