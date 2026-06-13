# Phase 5: Production Hardening & MLOps

> **Timeline:** ~2 weeks | **Difficulty:** Hard | **Dependencies:** Phases 1-4

## Objective

Secure the platform, implement robust evaluation pipelines, add observability, and prepare the architecture to scale from 10 to 10,000+ users.

---

## Deliverables

- Security hardening (Prompt injection, Rate limiting, Payload validation)
- MLOps Evaluation Pipelines (Offline & Online)
- Advanced Agent/KB Versioning
- Website Crawler ingestion
- Human Handoff mechanism
- Observability and Monitoring

---

## Tasks

### 5.1 — Security Hardening
- **Prompt Injection Protection:** Add LLM-based pre-screening for system prompt override attempts.
- **Retrieval Poisoning:** Validate document content anomalies.
- **Rate Limiting:** Implement Redis-based rate limiting per Org and per Visitor IP.

### 5.2 — MLOps: Offline Evaluation
Build `app/services/eval/offline.py`:
- Batch pipeline to run test datasets against the RAG pipeline.
- Measure Recall@K, MRR (Mean Reciprocal Rank).

### 5.3 — MLOps: Online Evaluation (LLM-as-a-Judge)
Build `app/workers/evaluation_worker.py`:
- Async Celery task that samples 10% of production conversations.
- Uses a secondary LLM call to score:
  - **Answer Relevance:** Does it answer the user?
  - **Groundedness:** Is the answer strictly derived from the cited chunks?
  - **Hallucination Flag:** Did it make things up?

### 5.4 — Website Crawler
- Build ingestion parser for URLs.
- Map site structure, strip boilerplate (nav/footer), chunk by page.

### 5.5 — Versioning System
- Implement immutable snapshots for Agents and KBs.
- Allow rolling back an Agent to a previous config version.

### 5.6 — Human Handoff
- When confidence is low or user requests "talk to a human".
- Pause AI generation, flag conversation in dashboard, send email/webhook notification to Org admins.

### 5.7 — Observability
- Export logs/metrics to Datadog / Prometheus / Grafana.
- Implement **OpenTelemetry (OTEL)** tracing to track the full RAG waterfall (Query -> Retrieval -> Rerank -> LLM Generation).
- Track API latency percentiles (P50, P95, P99).
- Track LLM token usage cost per Org.

### 5.8 — Feedback Analytics Pipeline
Build a pipeline that aggregates user feedback (thumbs up/down) with LLM evaluation scores to create a unified quality dashboard:
- Identify patterns: which topics get negative feedback, which documents produce poor answers.
- Feed insights into the evaluation dashboard.

---

## Tech Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Evaluation** | LLM-as-a-Judge | Ground truth data is hard to get. Using the LLM to score its own (or another model's) grounding is the industry standard for RAG observability. |
| **Crawling** | Custom BS4/Playwright | Better control over noise removal than off-the-shelf crawlers. |

---

## Testing Strategy
- Load testing: Simulate 100 concurrent chat streams.
- Security audit: Attempt prompt injection attacks.
