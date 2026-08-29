# Phase 1: Core Backend & Auth

> **Timeline:** ~2 weeks | **Difficulty:** Medium | **Dependencies:** Phase 0

## Objective

Build the foundational backend: database schema, authentication, RBAC, file upload, multi-tenant isolation, and core CRUD APIs for agents, knowledge bases, and documents. After this phase, a developer can register, create an org, create agents, upload documents, and manage KBs — all via API.

---

## Deliverables

- Complete PostgreSQL schema with migrations
- JWT authentication with refresh tokens
- RBAC system (owner, admin, member, viewer)
- Multi-tenant middleware with `org_id` injection
- File upload to MinIO/S3
- Full CRUD APIs: Auth, Orgs, Agents, KBs, Documents
- API documentation (auto-generated via FastAPI/Swagger)
- Integration tests for all endpoints

---

## Tasks

### 1.1 — App Configuration
Configure `pydantic-settings` in `app/config.py`:
- Database URLs (Postgres, Redis, Qdrant, MinIO)
- Google AI API Key
- JWT secrets and expiration times
- File upload limits (e.g., 50MB) and allowed types (`pdf`, `docx`, `txt`, `md`)

### 1.2 — Database Setup
- Set up SQLAlchemy 2.0 async engine + session factory
- Create `DeclarativeBase` with common columns (`id: UUID`, `created_at`, `updated_at`, `org_id`)
- Create `TenantBase` mixin that auto-includes `org_id`

### 1.3 — SQLAlchemy Models
Create models in `apps/api/app/models/`:
- `user.py`: id, email, password_hash, full_name, locale, is_active
- `organization.py`: id, name, slug, plan, settings (JSONB)
- `membership.py`: user_id, org_id, role (enum)
- `agent.py`: id, org_id, name, mode (1,2,3), system_prompt, language, version
- `knowledge_base.py`: id, org_id, name, embedding_model, chunk_size, status
- `agent_kb_link.py`: M:M join table between agents and KBs
- `document.py`: id, kb_id, org_id, filename, status (pending/processing/ready/error)
- `chunk.py`: id, document_id, org_id, content, token_count, chunk_index, metadata
- `feedback.py`: id, message_id, org_id, rating (thumbs_up/thumbs_down enum), comment (optional text), created_at
- `analytics_event.py`: id, org_id, agent_id, event_type, metadata JSONB, created_at
- `api_key.py`: id, org_id, name, key_hash, prefix, scopes JSONB, last_used_at, expires_at, created_at
- *Plus schemas for later: conversation, message, evaluation*

### 1.4 — Alembic Migrations
- Initialize Alembic (`alembic init alembic`)
- Configure for async and auto-detect
- Generate initial migration
- Add PostgreSQL Row-Level Security (RLS) policies in a manual migration:
  ```sql
  CREATE POLICY tenant_isolation ON <table>
  USING (org_id = current_setting('app.current_org_id')::uuid);
  ```

### 1.5 — Auth Service
Build `app/services/auth.py`:
- `register`: → User + auto-create Organization
- `login`: → return access_token, refresh_token
- `refresh`: → issue new access token
- Password hashing: `passlib` with bcrypt
- JWT creation/validation: `python-jose`
- Store refresh tokens in Redis with TTL

### 1.6 — Auth API Routes
Build `app/api/v1/auth.py`:
- `POST /register`, `POST /login`, `POST /refresh`, `POST /logout`
- `POST /forgot-password`, `POST /reset-password`
- `GET /me`, `PATCH /me`

### 1.7 — Auth Dependencies
Build `app/api/deps.py`:
- `get_current_user`: decode JWT, fetch user
- `get_current_org`: extract org_id
- `require_role(min_role)`: enforce RBAC

### 1.8 — Multi-Tenant Middleware
Build `app/middleware/tenant.py`:
- Extract `org_id` from JWT or headers
- Set PostgreSQL session variable: `SET app.current_org_id = '<org_id>'`
- Inject `org_id` into request state for service layer access

### 1.9 — Organization Service
- CRUD for organizations
- Member invites, role management

### 1.10 — File Upload Service
Build `app/services/file_upload.py`:
- Async upload to MinIO/S3 using `aioboto3`
- Org-scoped paths: `/{org_id}/documents/{doc_id}/{filename}`
- Validate file type and size
- Generate presigned URLs

### 1.11 — Agent Service & API
- CRUD operations for Agents, scoped to `org_id`
- Link/unlink Knowledge Bases
- Agent duplication (deep copy)
- Version tracking
- Embed code generator (`<script>` snippet)

### 1.12 — Knowledge Base Service & API
- CRUD for KBs
- Track `doc_count` and `chunk_count`
- Cascade delete: KB delete -> delete docs + chunks + vectors

### 1.13 — Document Service & API
- Upload flow: validate -> S3 -> DB (`status=pending`) -> return 202
- List/Get/Delete documents within a KB
- Bulk upload support

### 1.14 — Pydantic Schemas
- Build strict validation schemas for all requests and responses in `app/schemas/`
- Implement pagination schemas (`PageParams`, `PageResponse`)

### 1.15 — Error Handling
- Custom exception classes (NotFound, Forbidden, Validation, etc.)
- Global exception handler mapping to consistent JSON

### 1.16 — Request Logging
- Add structured JSON logging middleware (structlog)
- Log method, path, status, latency, user_id, org_id, request_id

### 1.17 — Integration Tests
- Pytest setup with async test client and test DB
- Test full auth flow
- Test tenant isolation strictly (User A cannot see User B's data)
- Test CRUD for Agents, KBs, Documents

### 1.18 — OpenAPI Spec
- Verify Swagger UI at `localhost:8000/docs`
- Export `openapi.json` for frontend client generation

### 1.19 — Analytics Service & API
Build `app/services/analytics.py` and `app/api/v1/analytics.py`:
- `GET /analytics/overview`: total conversations, messages, avg latency, cost.
- `GET /analytics/agents/{id}`: per-agent stats.
- `GET /analytics/costs`: cost breakdown by org.
- Track events via the `analytics_events` table.

---

## Tech Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Auth** | Custom JWT | Avoids external dependency/cost for MVP. Easy to migrate to Supabase Auth in Phase 5 if needed. |
| **ORM** | SQLAlchemy 2.0 async | Industry standard, excellent async support, works perfectly with Alembic. |
| **Multi-tenancy** | RLS + App filtering | Belt-and-suspenders: Postgres RLS is a safety net; app-layer `org_id` WHERE clause is the primary mechanism. |
| **File Storage** | MinIO | S3-compatible API means the exact same code works locally and in AWS/GCP production. |
| **Password hashing**| bcrypt | Industry standard via passlib. |

---

## Testing Strategy
- Unit tests for password hashing, JWT operations, tenant logic
- Integration tests for full auth flows and tenant data isolation
- Swagger UI manual verification

### 1.19 — Analytics & Feedback
- Build `app/services/analytics.py` and `app/api/v1/analytics.py`
- Endpoints: `GET /analytics/overview`, `GET /analytics/agents/{id}`, `GET /analytics/costs`
- Create `feedback` table (thumbs up/down)
- Create `analytics_events` table for tracking
- Create `api_keys` table for programmatic access
