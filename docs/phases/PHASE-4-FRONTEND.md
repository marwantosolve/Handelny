# Phase 4: Frontend Dashboard

> **Timeline:** ~3 weeks | **Difficulty:** Medium | **Dependencies:** Phase 1

## Objective

Build the user-facing SaaS dashboard where users manage their organization, agents, knowledge bases, and view analytics.

---

## Deliverables

- Landing Page
- Authentication Pages (Login, Register, Forgot Password)
- Main Dashboard overview
- Agent Management (Create Wizard, Settings)
- Knowledge Base & Document Management
- Chat Playground
- Basic Analytics Dashboard
- User & Org Settings
- Full Arabic/English UI localization (i18n)
- Evaluation Dashboard

---

## Tasks

### 4.1 — Frontend Foundation
- Configure Next.js App Router.
- Set up `next-intl` for Arabic/English routing and translation dictionaries.
- Configure Tailwind CSS with RTL support (logical properties like `ms-` instead of `ml-`).
- Configure `shadcn/ui` components.

### 4.2 — API Client & State
- Generate TypeScript client from FastAPI OpenAPI spec.
- Set up `@tanstack/react-query` for data fetching/caching.
- Set up `zustand` for global UI state (sidebar, modals).

### 4.3 — Authentication Views
- Login, Register forms with validation (`zod` + `react-hook-form`).
- Auth context provider to protect dashboard routes.

### 4.4 — Layouts
- Dashboard sidebar (Agents, KBs, Analytics, Settings).
- Top navbar (Org switcher, User profile, Language toggle).

### 4.5 — Knowledge Base UI
- KB List view.
- KB Detail view: Document upload zone (drag & drop), document status polling (Pending -> Ready).

### 4.6 — Agent Wizard & Settings
- Multi-step wizard to create an Agent (Name -> Select Mode -> Link KBs -> Customize Widget).
- Agent Settings form (System prompt, Temperature, Fallback messages).

### 4.7 — Chat Playground
- Split-pane view: Chat UI on the left, Debug/Metadata/Sources on the right.
- Connect to the streaming API.

### 4.8 — Analytics UI
- Charts for: Total conversations, Message count, Average latency, Cost tracking.
- Use a library like `recharts`.

### 4.9 — Settings UI
- User profile, Organization members, API key generation.
- Billing placeholder page.

### 4.10 — Evaluation Dashboard
Build the evaluation dashboard page showing:
- Aggregate quality scores (answer relevance, groundedness, hallucination rate).
- Per-agent evaluation breakdown.
- Trend charts over time.
- Drill-down into individual evaluated messages.
- Filters by date range and agent.
- Components: `EvalScoreCard`, `EvalTrendChart`, `EvalMessageTable`, `EvalFilterBar`.

---

## Tech Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Framework** | Next.js App Router | Best-in-class React framework, excellent SEO for landing, good layouts. |
| **State** | React Query | Handles caching, loading states, and polling (crucial for document upload status) out of the box. |
| **UI Library**| shadcn/ui | Beautiful, accessible, fully customizable. |
| **i18n** | next-intl | Native App Router support, good RTL handling. |

---

## Testing Strategy
- Verify RTL layout completely flips correctly for Arabic.
- Verify JWT storage and route protection.
- Test document drag-and-drop flow.

### 4.10 — Evaluation Dashboard
- Build UI for MLOps and Feedback.
- Aggregate quality scores (Relevance, Groundedness).
- Components: `EvalScoreCard`, `EvalTrendChart`, `EvalMessageTable` (drill-down into individual feedback).
