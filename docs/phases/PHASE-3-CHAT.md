# Phase 3: Chat & Agent System

> **Timeline:** ~2 weeks | **Difficulty:** Hard | **Dependencies:** Phase 2

## Objective

Build the real-time chat system: streaming responses, conversation memory, three agent response modes, confidence scoring, fallback logic, web search for Mode 3, and the embeddable chat widget. After this phase, users can talk to their AI agents.

---

## Deliverables

- Chat API with Server-Sent Events (SSE) streaming
- Conversation management (create, list, history)
- Three agent response modes fully implemented
- Confidence scoring and fallback logic
- Web search integration (Mode 3)
- Source citations in responses
- Embeddable chat widget (JavaScript snippet)
- Playground chat in dashboard API
- User feedback collection (thumbs up/down)
- Mode enforcement guardrails

---

## Tasks

### 3.1 — Conversation Service
Build `app/services/conversation.py`:
- CRUD for conversations.
- Track `session_id`, `visitor_id`, `channel`, and `language`.

### 3.2 — Conversation Memory Manager
Build `app/services/memory.py`:
- Fetch last N messages, truncate to token budget (e.g. max 2000 tokens).

### 3.3 — Chat Orchestrator
Build `app/services/chat.py`:
- Load config -> Detect Lang -> Retrieve Context -> Build Prompt -> Generate (stream) -> Extract Citations -> Save to DB.

### 3.4 — Mode 1: KB Only
Build `app/services/modes/kb_only.py`:
- Strict retrieval. If relevance < threshold, return fallback message. No hallucination allowed.

### 3.5 — Mode 2: KB + AI Knowledge
Build `app/services/modes/kb_plus_ai.py`:
- Prefer KB. If insufficient, allow general knowledge but tag output metadata to indicate source.

### 3.6 & 3.7 — Mode 3: KB + Web Search
Build `app/services/modes/kb_plus_web.py` & `app/services/web_search.py`:
- Try KB first. If confidence low -> query Serper API (Google) -> append to context -> generate.
- Cache web results.

### 3.8 — Confidence Scoring
Build `app/services/confidence.py`:
- Implement a hardcoded scoring formula: `confidence = 0.5 * retrieval_score + 0.3 * reranker_score + 0.2 * grounding_score`
- High (>0.7), Medium (0.4-0.7), Low (<0.4).

### 3.9 — Fallback Logic
Build `app/services/fallback.py`:
- Route low-confidence queries based on Agent Mode.
- Escalate to human handoff after 2 consecutive failures.

### 3.10 — Streaming Chat API
Build `app/api/v1/chat.py`:
- `POST /api/v1/chat/{agent_id}/message` using FastAPI `StreamingResponse` (SSE).
- Yield tokens, then sources, then metadata.

### 3.11 — Widget Public API
Build `app/api/v1/widget.py`:
- Public, unauthenticated, rate-limited endpoint for the embeddable widget.
- Endpoint to fetch widget UI config (colors, greetings).

### 3.12 — Embeddable Chat Widget
Build `packages/widget/`:
- Preact + TypeScript (tiny bundle).
- Vite build to single `widget.js`.
- Features: Floating button, streaming text, citations, auto-RTL for Arabic, session persistence.

### 3.13 — Conversation History API
- Endpoints to list conversations and fetch full message history.

### 3.14 — User Feedback Collection
Build `app/services/feedback.py` and add `POST /api/v1/messages/{id}/feedback` endpoint:
- Support thumbs up/down rating and optional text comment.
- Store in the `feedback` table.
- Add `GET /api/v1/feedback?agent_id=` for listing feedback.
- This feeds into the evaluation pipeline.

### 3.15 — Mode Enforcement Guardrails
Build `app/services/guardrails.py`:
- **Mode 1 (KB Only):** Implement pre-generation citation coverage checks and source overlap checks to verify the response uses retrieved context, rather than heavy NLI models.
- **Mode 2:** Add metadata tagging to distinguish KB-sourced vs AI-sourced content.
- **Mode 3:** Merge web citations with KB citations in a unified format.

---

## Tech Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Streaming Protocol**| SSE (Server-Sent Events) | Native to HTTP, simple to implement in FastAPI and JS, firewall-friendly compared to WebSockets. |
| **Web Search API** | Serper | Cheap, fast Google Search API. |
| **Widget Framework**| Preact | Tiny footprint (<50KB), React-compatible API, essential for 3rd-party embedding without bloat. |

---

## Testing Strategy
- Test SSE streaming disconnects/reconnects
- Verify Arabic RTL layout in widget
- Verify fallback behavior when asking out-of-domain questions

### 3.14 — User Feedback Collection
- Build `app/services/feedback.py`
- Add `POST /api/v1/messages/{id}/feedback` (thumbs up/down, optional comment)
- Feeds data directly into the evaluation pipeline.

### 3.15 — Mode Enforcement Guardrails
- Build `app/services/guardrails.py`
- Mode 1: Pre-generation citation coverage check & source overlap check (avoids the high latency of NLI models).
- Mode 2: Metadata tagging for KB vs General knowledge.
- Mode 3: Unified web/PDF citation merging.
