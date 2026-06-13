# Phase 2: RAG Pipeline

> **Timeline:** ~3 weeks | **Difficulty:** Hard | **Dependencies:** Phase 1

## Objective

Build the complete document ingestion and retrieval pipeline: parse uploaded documents, clean and chunk them, generate multilingual embeddings, store in vector DB, and retrieve relevant context for queries. This is the core intelligence of the platform.

---

## Deliverables

- Document parser supporting PDF, DOCX, TXT, MD
- Text cleaning and preprocessing pipeline
- Hybrid chunking strategy
- Multilingual embedding generation (Arabic + English)
- Vector storage and retrieval in Qdrant
- Hybrid retrieval (dense + sparse)
- Cross-encoder reranking
- Context construction and prompt orchestration
- Citation extraction
- Background worker for async ingestion (Celery)

---

## Tasks

### 2.1 — Celery Worker Setup
Build `app/workers/celery_app.py`:
- Configure Celery with Redis broker and result backend
- Add to Docker Compose

### 2.2 — Document Parser
Build `app/services/ingestion/parser.py`:
- **PDF:** `pymupdf` (fitz) - extract text, page numbers, detect scans
- **DOCX:** `python-docx` - extract paragraphs, preserve headings
- **TXT:** Plain text with `chardet` encoding detection
- **MD:** Preserve markdown structure, strip HTML
- Output: `list[ParsedPage(content, page_number, metadata)]`

### 2.3 — Text Cleaning
Build `app/services/ingestion/cleaner.py`:
- Normalization (whitespace, Unicode)
- Arabic normalization: alef/hamza variants
- Handle mixed Arabic+English text without breaking mid-word
- Collapse duplicate newlines, strip repetitive headers/footers

### 2.4 — Language Detection
Build `app/services/ingestion/language.py`:
- Use `lingua-py` for reliable Arabic vs English detection
- Detect per-paragraph and aggregate to document-level

### 2.5 — Chunking Strategy
Build `app/services/ingestion/chunker.py`:
- **DECISION: Hybrid Strategy**
- *Semantic:* Split on headings (H1-H6) and paragraphs
- *Size-based fallback:* Target 512 tokens, 64 token overlap (using `tiktoken`)
- *Arabic-aware:* Split on proper Arabic sentence boundaries (، . ؟ !)
- Output: chunks with rich metadata (page_numbers, heading_hierarchy)

### 2.6 — Metadata Extraction
Build `app/services/ingestion/metadata.py`:
- Extract title, author, creation date
- Extract heading hierarchy for breadcrumbs

### 2.7 — Embedding Service
Build `app/services/embedding.py`:
- **DECISION: `intfloat/multilingual-e5-large`**
- Load via `sentence-transformers`
- Batch processing (32 at a time)
- Prefix handling ("query: " vs "passage: ")

### 2.8 — Vector Store Integration
Build `app/services/vector_store.py`:
- **DECISION: Qdrant**
- Create collection per org (`org_{org_id}`)
- Dense vector (1024-dim, cosine distance)
- Sparse vector (BM25)
- Payload filtering by `kb_id`, `document_id`

### 2.9 — Sparse Encoding (BM25)
Build `app/services/sparse_encoder.py`:
- Use Qdrant's FastEmbed or implement custom BM25
- Arabic tokenization (whitespace + stemming)

### 2.10 — Ingestion Orchestrator
Build `app/workers/ingestion_worker.py`:
- Tie 2.2-2.9 together in `@celery.task`
- Fetch → Parse → Clean → Detect Lang → Chunk → Embed → Save PG → Upsert Qdrant → Update Status

### 2.11 — Retrieval Service
Build `app/services/retrieval.py`:
- Detect query language -> Embed -> Sparse encode
- Hybrid search Qdrant (Dense + Sparse with RRF merging)
- Filter by `kb_ids` payload

### 2.12 — Reranking Service
Build `app/services/reranker.py`:
- **DECISION: Cross-encoder (Local)**
- Model: `cross-encoder/ms-marco-MiniLM-L-12-v2` or `BAAI/bge-reranker-v2-m3`
- Rerank top-20 to top-5

### 2.13 — Context Construction
Build `app/services/context_builder.py`:
- Assemble reranked chunks into LLM context window
- Add source metadata inline `[Source: {filename}, Page {page}]`

### 2.14 — Prompt Orchestration
Build `app/services/prompt.py`:
- Templates for Mode 1 (Strict KB), Mode 2 (KB + AI), Mode 3 (KB + Web)
- Inject context, history, and system prompt

### 2.15 — LLM Response Generation
Build `app/services/llm.py`:
- Google AI Studio client (`google-genai` SDK)
- Model: `gemma-4-31b-it`
- Handle rate limits, retries, and token usage tracking

### 2.16 — Citation Extraction
Build `app/services/citation.py`:
- Match generated response sentences back to source chunks to create citation markers

### 2.17 — Upload Triggers
- Wire POST `/documents` to trigger Celery task
- Add polling endpoint for document status

### 2.18 — Debug Endpoint
- `POST /api/v1/debug/query` (admin only) to test full pipeline and inspect intermediate RAG stages.

### 2.19 & 2.20 — Testing
- Unit test each pipeline stage
- Full integration test (upload Arabic/English docs -> wait for ready -> query -> check citations)

---

## Tech Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Embedding** | `intfloat/multilingual-e5-large` | Best free model for Arabic+English. 1024-dim, no API cost, outperforms ADA-002 on multilingual. |
| **Vector DB** | Qdrant | Native sparse vectors, payload filtering for multi-tenant, free self-hosted. |
| **Chunking** | Hybrid (Semantic + Size) | Preserves meaning while guaranteeing window limits. |
| **Reranker** | `BAAI/bge-reranker-v2-m3` | Free, local, massive quality boost. Avoids Cohere API cost. |
| **Queue** | Celery + Redis | Proven, reliable async processing. |

---

## Testing Strategy
- Create a test set of 20 English + 20 Arabic question-answer pairs
- Benchmark retrieval recall@5
- Benchmark ingestion speed
