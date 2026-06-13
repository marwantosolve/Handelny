# Phase 0: Foundation & Project Setup

> **Timeline:** ~1 week | **Difficulty:** Easy | **Dependencies:** None

## Objective

Establish the development infrastructure so that any contributor can clone the repo, run one command, and have a fully working local environment. Set the quality bar for the entire project.

---

## Deliverables

- Turborepo monorepo with all workspace packages configured
- Docker Compose with PostgreSQL, Redis, MinIO (S3-compatible), Qdrant
- CI pipeline (GitHub Actions) — lint, type-check, test on every PR
- CLAUDE.md, README.md, contributing guide
- ADR templates and initial architecture decisions documented
- Pre-commit hooks (linting, formatting)

---

## Repo Structure

```
handelny/
├── CLAUDE.md
├── README.md
├── LICENSE
├── turbo.json
├── package.json                          # Root workspace config (pnpm)
├── pnpm-workspace.yaml
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                        # Lint, test, type-check
│   │   ├── cd-staging.yml                # Deploy to staging
│   │   └── cd-production.yml             # Deploy to production
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│
├── docker/
│   ├── docker-compose.yml                # Local dev (all services)
│   ├── docker-compose.prod.yml           # Production compose
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx/
│       └── nginx.conf
│
├── docs/
│   ├── architecture.md                   # System architecture
│   ├── erd.md                            # Database ERD
│   ├── api-spec.md                       # API documentation
│   ├── rag-pipeline.md                   # RAG system design
│   ├── deployment.md                     # Deployment guide
│   ├── security.md                       # Security practices
│   └── adr/                              # Architecture Decision Records
│       ├── 001-monorepo-choice.md
│       ├── 002-auth-strategy.md
│       ├── 003-vector-db-choice.md
│       └── 004-embedding-model.md
│
├── packages/
│   ├── shared/                           # Shared types, utils, constants
│   │   ├── package.json
│   │   └── src/
│   │       ├── types/
│   │       │   ├── agent.ts
│   │       │   ├── document.ts
│   │       │   ├── conversation.ts
│   │       │   ├── user.ts
│   │       │   └── api.ts
│   │       ├── constants/
│   │       │   ├── agent-modes.ts
│   │       │   └── languages.ts
│   │       └── utils/
│   │           └── validation.ts
│   └── widget/                           # Embeddable chat widget
│       ├── package.json
│       ├── src/
│       │   ├── Widget.tsx
│       │   ├── embed.ts                  # <script> entry point
│       │   └── styles.css
│       └── vite.config.ts
│
├── apps/
│   ├── web/                              # Next.js dashboard
│   │   ├── package.json
│   │   ├── next.config.js
│   │   ├── tailwind.config.ts
│   │   └── src/
│   │       ├── app/                      # App router
│   │       │   ├── [locale]/
│   │       │   │   ├── layout.tsx
│   │       │   │   ├── page.tsx          # Landing
│   │       │   │   ├── (auth)/
│   │       │   │   │   ├── login/
│   │       │   │   │   └── register/
│   │       │   │   └── (dashboard)/
│   │       │   │       ├── layout.tsx
│   │       │   │       ├── dashboard/
│   │       │   │       ├── agents/
│   │       │   │       ├── documents/
│   │       │   │       ├── playground/
│   │       │   │       ├── analytics/
│   │       │   │       └── settings/
│   │       │   └── api/                  # BFF routes if needed
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── lib/
│   │       ├── stores/
│   │       └── i18n/
│   │           ├── ar.json
│   │           └── en.json
│   │
│   └── api/                              # FastAPI backend
│       ├── pyproject.toml
│       ├── alembic.ini
│       ├── alembic/
│       │   └── versions/
│       ├── app/
│       │   ├── main.py                   # FastAPI app entry
│       │   ├── config.py                 # Settings (pydantic-settings)
│       │   ├── dependencies.py           # DI container
│       │   ├── middleware/
│       │   │   ├── tenant.py             # Multi-tenant context
│       │   │   ├── cors.py
│       │   │   └── rate_limit.py
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── router.py
│       │   │       ├── auth.py
│       │   │       ├── agents.py
│       │   │       ├── documents.py
│       │   │       ├── knowledge_bases.py
│       │   │       ├── conversations.py
│       │   │       ├── chat.py
│       │   │       ├── analytics.py
│       │   │       ├── evaluations.py
│       │   │       ├── settings.py
│       │   │       └── widget.py
│       │   ├── models/                   # SQLAlchemy models
│       │   ├── schemas/                  # Pydantic schemas
│       │   ├── services/                 # Business logic
│       │   ├── core/                     # Security, exceptions
│       │   └── workers/                  # Background tasks
│       └── tests/
│           ├── conftest.py
│           ├── unit/
│           ├── integration/
│           └── e2e/
│
└── scripts/
    ├── setup-dev.sh                      # One-command dev setup
    ├── seed-db.sh                        # Seed data
    ├── run-migrations.sh
    └── generate-api-client.sh            # OpenAPI -> TypeScript
```

---

## Tasks

### 0.1 — Initialize Git Repo
- Create repo, add comprehensive `.gitignore` (Python, Node, Docker, IDE files)
- Initial commit

### 0.2 — Root Workspace Config
- Create root `package.json` with Turborepo workspaces
- Workspaces: `apps/web`, `apps/api`, `packages/shared`, `packages/widget`
- Create `pnpm-workspace.yaml`

### 0.3 — Turborepo Pipelines
- Configure `turbo.json` with pipelines: `build`, `dev`, `lint`, `test`, `type-check`

### 0.4 — Scaffold Frontend (apps/web)
- `npx create-next-app@latest` with App Router, TypeScript, Tailwind CSS, ESLint
- Add dependencies: `shadcn/ui`, `next-intl` (i18n), `zustand`, `@tanstack/react-query`

### 0.5 — Scaffold Backend (apps/api)
- Create `pyproject.toml` with:
  - **Core:** FastAPI, uvicorn, SQLAlchemy 2.0, alembic, pydantic-settings
  - **DB:** asyncpg
  - **Auth:** python-jose, passlib, python-multipart
  - **Testing:** pytest, pytest-asyncio, httpx
  - **Linting:** ruff, mypy

### 0.6 — Scaffold Shared Package (packages/shared)
- TypeScript package with shared interfaces: Agent, Document, User, Conversation
- Constants: agent modes, supported languages, supported file types

### 0.7 — Docker Compose (Local Dev)
Create `docker/docker-compose.yml` with services:

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| postgres | `pgvector/pgvector:pg16` | 5432 | Relational DB + pgvector extension |
| redis | `redis:7-alpine` | 6379 | Cache, sessions, Celery broker |
| qdrant | `qdrant/qdrant:v1.12.5` | 6333/6334 | Vector database |
| minio | `minio/minio:latest` | 9000/9001 | S3-compatible file storage |
| backend | Custom Dockerfile | 8000 | FastAPI with hot-reload |
| frontend | Custom Dockerfile | 3000 | Next.js with hot-reload |
| celery-worker | Same as backend | — | Background task processor |

### 0.8 — Backend Dockerfile
- Python 3.12-slim base, install dependencies, uvicorn entrypoint

### 0.9 — Frontend Dockerfile
- Node 20-alpine base, install dependencies, next dev entrypoint

### 0.10 — Dev Setup Script
`scripts/setup-dev.sh`:
- Check prerequisites (Docker, Node 20+, Python 3.12+, pnpm)
- Copy `.env.example` → `.env`
- Run `docker compose up -d`
- Run database migrations
- Seed initial data
- Print "Ready at http://localhost:3000"

### 0.11 — Environment Variables
Create `.env.example`:
```env
DATABASE_URL=postgresql+asyncpg://handelny:handelny@localhost:5432/handelny
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
GOOGLE_AI_STUDIO_API_KEY=your-key-here
JWT_SECRET=your-secret-here
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
```

### 0.12 — CI Pipeline
`.github/workflows/ci.yml`:
- **Backend job:** Python 3.12, install deps (cached), run `ruff check`, `mypy`, `pytest`
- **Frontend job:** Node 20, pnpm, install deps (cached), run `eslint`, `tsc --noEmit`, `vitest`

### 0.13 — CLAUDE.md
- Project overview, tech stack, architecture summary
- How to run locally, key patterns (multi-tenant, service layer)
- Testing conventions, file naming, common commands

### 0.14 — README.md
- Project description, features, tech stack
- Quick start, prerequisites, setup
- Architecture diagram (Mermaid)
- API docs link, contributing link

### 0.15 — Architecture Documentation
`docs/architecture.md`:
- System diagram: user → widget → API → RAG → LLM
- Data flow: document ingestion pipeline
- Data flow: chat query pipeline
- Multi-tenant isolation model

### 0.16 — ADR: Monorepo Choice
`docs/adr/001-monorepo-choice.md`:
- **Decision:** Turborepo
- **Rationale:** Simpler than Nx, first-class Next.js support, good caching, small team doesn't need Nx generators

### 0.17 — Pre-commit Hooks
- Backend: ruff format, ruff check, mypy (via `pre-commit` framework)
- Frontend: eslint, prettier (via `husky` + `lint-staged`)

### 0.18 — Minimal Backend App
`apps/api/app/main.py`:
- Health endpoint returning `{"status": "ok"}`
- CORS middleware
- Global exception handlers

### 0.19 — Minimal Frontend App
`apps/web/src/app/page.tsx`:
- "Handelny — Coming Soon" with locale toggle (ar/en)

### 0.20 — Smoke Test
- `docker compose up` → visit `localhost:3000`, hit `localhost:8000/api/v1/health`
- Both return OK

---

## Tech Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Monorepo tool | **Turborepo** | Simpler than Nx, native Next.js support, excellent remote caching |
| Package manager | **pnpm** | Fast, disk-efficient, strict dependency resolution |
| Python tooling | **Ruff + mypy** | Ruff is 100x faster than flake8+black combined; mypy for type safety |
| Local S3 | **MinIO** | S3-compatible, free, avoids AWS dependency in dev |
| Container orchestration | **Docker Compose** | Sufficient for dev; production will use individual services |

---

## Testing Strategy

- [x] `docker compose up` succeeds without errors
- [x] Frontend loads at `localhost:3000`
- [x] Backend health check returns 200 at `localhost:8000/api/v1/health`
- [x] CI pipeline passes on a test PR
- [x] `scripts/setup-dev.sh` works from a clean clone

---

## Key Files Created

```
CLAUDE.md, README.md, turbo.json, package.json, pnpm-workspace.yaml,
docker/docker-compose.yml, docker/backend.Dockerfile, docker/frontend.Dockerfile,
.github/workflows/ci.yml, scripts/setup-dev.sh, .env.example,
apps/api/app/main.py, apps/api/pyproject.toml,
apps/web/src/app/page.tsx, apps/web/next.config.js,
packages/shared/src/types/agent.ts, docs/architecture.md
```
