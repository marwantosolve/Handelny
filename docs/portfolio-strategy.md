# GitHub Portfolio Strategy

To impress recruiters and hiring managers, the project repository must be immaculate, highly visual, and immediately understandable.

## 1. Repository Structure

*   **Top Level:** Clean. Only `README.md`, `CLAUDE.md`, `LICENSE`, and standard config files.
*   **`docs/` Folder:** Contains all architecture, API specs, security, and RAG rationale docs. Shows rigorous planning.
*   **Badges:** Top of README must have CI passing, Code Coverage >80%, and MIT License badges.

## 2. README Structure

1.  **Hero Image/GIF:** A beautiful mockup of the chat widget working on a website.
2.  **Hook:** "Create AI Customer Support Agents From Your Documents in 3 Minutes."
3.  **Key Features (with small icons):** Multilingual (Arabic/English), 3 Agent Modes, Full MLOps evaluation, RAG Pipeline.
4.  **Tech Stack:** Grid of logos (Next.js, FastAPI, Postgres, Qdrant, Google AI).
5.  **Architecture Diagram:** Embedded Mermaid diagram of the system flow.
6.  **Quick Start:** Step-by-step `docker compose up` instructions.
7.  **Links:** Links to the detailed `docs/` files.

## 3. Demo Strategy

*   **Live App:** Hosted on Vercel (Frontend) and Render (Backend).
*   **Demo Accounts:** Provide `guest@handelny.com` with read-only access to a pre-seeded "Acme Corp" account.
*   **Pre-seeded Data:** The account must already have an Agent created and 5 PDF documents uploaded so the recruiter can instantly test the chat without doing setup work.
*   **Fallback:** If the live demo spins down due to inactivity, the README MUST contain a 2-minute YouTube video link.

## 4. Screenshot Plan (docs/screenshots/)

1.  `01-dashboard-overview.png`: High-level analytics.
2.  `02-agent-wizard.png`: Showing the 3 Agent Modes selection.
3.  `03-document-upload.png`: Showing the processing pipeline UI.
4.  `04-chat-playground-english.png`: Testing an agent in English.
5.  `05-chat-playground-arabic.png`: Testing an agent in Arabic (RTL layout visible).
6.  `06-evaluation-dashboard.png`: Showing MLOps metrics.

## 5. Demo Video Storyboard

*   **0:00 - 0:15:** Introduce Handelny, log in to dashboard.
*   **0:15 - 0:45:** Create a new Agent, select "Mode 2" (KB + AI), upload a sample PDF.
*   **0:45 - 1:30:** Open playground, ask a question in English. Show the streaming response and citations.
*   **1:30 - 2:00:** Ask a question in Arabic. Show the RTL layout and accurate Arabic RAG response.
*   **2:00 - 2:30:** Show the embed code snippet, and briefly flash the analytics/evaluation dashboards.

## 6. Skills Showcase Matrix

| Project Component | Hiring Manager Skill Demonstrated |
| :--- | :--- |
| **Qdrant + Hybrid Reranking** | Advanced RAG Engineering & Information Retrieval |
| **Gemma 31B Integration** | LLM Engineering & Prompt Orchestration |
| **Celery Worker Pipeline** | Backend Engineering & Async Queue Management |
| **Postgres RLS / JWT** | Security & Multi-tenant SaaS Architecture |
| **Next.js + SSE Streaming** | Modern Frontend Engineering & UX Design |
| **Evaluation Dashboards** | MLOps & AI Observability |