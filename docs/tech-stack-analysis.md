# Tech Stack Analysis & Alternatives

## 1. Frontend Framework

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **Next.js (Chosen)** | Industry standard, App Router supports Server Components, massive ecosystem, excellent SEO. | App Router learning curve, Vercel vendor lock-in risk. | **Chosen.** Required for high-quality SaaS dashboard and SEO-friendly landing pages. |
| Remix | Great nested routing, standard web APIs. | Smaller ecosystem than Next.js. | Rejected. Next.js has better shadcn/ui support. |
| SvelteKit | Excellent performance, less boilerplate. | Smaller community, fewer enterprise UI libraries. | Rejected. React ecosystem is larger for AI dashboard components. |
| Nuxt | Vue ecosystem is approachable. | Less TypeScript support traditionally (though improving). | Rejected. Team is standardizing on React/TS. |

## 2. Backend Framework

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **FastAPI (Chosen)** | Extremely fast, native async/await, auto-generated OpenAPI docs, great Python AI ecosystem. | Requires strict discipline for large apps, smaller ecosystem than Django. | **Chosen.** The AI/ML ecosystem is in Python. FastAPI is the modern standard for Python APIs. |
| Django | "Batteries included", great ORM and admin panel. | Heavy, async is bolted on, overkill for API-only backend. | Rejected. We need high-performance async for streaming LLM responses. |
| Express.js | Unified TS stack (full-stack JS). | Python is required for advanced RAG/ML tooling (sentence-transformers). | Rejected. ML pipeline requires Python. |
| NestJS | Great enterprise architecture for Node. | Still runs in Node, making Python AI integration complex. | Rejected. Need Python natively. |

## 3. Database

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **PostgreSQL (Chosen)** | Rock solid, ACID compliant, excellent JSONB support, Row-Level Security (RLS). | Vertical scaling limits. | **Chosen.** Best-in-class relational DB. RLS is crucial for multi-tenant security. |
| MySQL | Very fast for reads, ubiquitous. | Less robust JSON support, weaker array types compared to Postgres. | Rejected. Postgres is superior for complex SaaS schemas. |
| MongoDB | Flexible schema, fast iteration. | No native RLS, complex joins are painful. | Rejected. SaaS platforms heavily rely on relational data (Users -> Orgs -> Agents). |
| CockroachDB | Distributed SQL, scales horizontally. | Higher latency for simple queries, more complex to operate. | Rejected. Overkill for MVP, Postgres scales high enough. |

## 4. Vector Database

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **Qdrant (Chosen)** | Native sparse+dense vectors (hybrid search), Rust-based (fast), payload filtering, free self-hosting. | Newer ecosystem compared to Pinecone. | **Chosen.** Payload filtering is critical for tenant isolation (`org_id`). Hybrid search is built-in. |
| Pinecone | Fully managed, zero setup, industry standard. | Expensive, no self-hosted option, strict limits on free tier. | Rejected. Avoid high operational costs for the MVP. |
| Weaviate | Great features, robust multi-tenant support. | Heavier resource footprint, GraphQL interface can be polarizing. | Rejected. Qdrant is more lightweight for Docker Compose dev. |
| Milvus | Highly scalable for massive datasets. | Extremely complex to deploy (requires etcd, MinIO, Pulsar). | Rejected. Unnecessary complexity for the current scale. |
| pgvector | Keeps all data in Postgres, simple stack. | Slower than dedicated vector DBs, scaling vectors scales the relational DB. | Rejected. Vector search and relational data have different scaling profiles. |

## 5. Authentication

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **Custom JWT (Chosen)** | Zero cost, full control over user data and flows, zero external dependencies. | You have to build it yourself (reset passwords, etc). | **Chosen.** Keeps MVP completely self-contained and free to host. |
| Supabase Auth | Fantastic DX, ties into Postgres RLS natively. | Vendor dependency, migration is hard. | Considered for Phase 6. |
| Auth0 | Industry standard, beautiful UIs, SAML/SSO. | Very expensive at scale, vendor lock-in. | Rejected. |
| Clerk | Amazing developer experience for Next.js. | High pricing per MAU. | Rejected. |
| Firebase Auth | Free tier is generous. | Ties you into Google Cloud ecosystem heavily. | Rejected. |

## 6. File Storage

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **MinIO/S3 (Chosen)**| S3-compatible, free, runs locally in Docker. AWS S3 scales infinitely in prod. | You manage MinIO infra locally. | **Chosen.** Acts as an S3 clone locally; in production we seamlessly swap the URL to AWS S3. |
| Google Cloud Storage| Fast, integrates with GCP ecosystem. | Not S3-compatible without translation. | Rejected. Prefer S3 API standard. |
| Azure Blob | Great enterprise integration. | Unnecessary if not running full Azure stack. | Rejected. |
| Cloudflare R2 | Zero egress fees, very fast. | Missing some advanced S3 features (lifecycle rules). | Could be an alternative, but sticking to standard S3 for now. |

## 7. Deployment

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **AWS (Chosen)** | Enterprise standard (ECS/EKS/RDS), infinitely scalable. | High complexity, steep learning curve. | **Chosen.** Proves enterprise architecture skills for portfolio. |
| GCP (Cloud Run) | Excellent serverless containers. | GCP UI and IAM can be confusing. | Good alternative, but AWS is more common in job postings. |
| Railway | Push-to-deploy, incredibly easy. | Expensive at scale, less control over VPCs. | Excellent for the MVP/Demo, but AWS is better for the architecture design doc. |
| Fly.io | Edge deployments, fast. | Persistent volumes can be tricky. | Rejected. |
| Vercel + Railway | Great frontend (Vercel) + easy backend (Railway). | Fragmented infrastructure. | Rejected in favor of consolidated AWS architecture. |

## 8. Monitoring

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **Prometheus+Grafana**| Open source, highly customizable, industry standard. | Requires hosting and configuring. | **Chosen.** No SaaS fees, demonstrates DevOps skills. |
| Datadog | Incredible visibility, APM, zero setup. | Extremely expensive. | Rejected for MVP. |
| New Relic | Great APM and tracing. | Costly. | Rejected. |
| Elastic Stack | Great for log aggregation. | Heavy JVM footprint for self-hosting. | Rejected. |

## 9. CI/CD

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **GitHub Actions** | Native to GitHub, free for public repos, massive action marketplace. | Can be tricky to debug locally. | **Chosen.** Standard for open-source and portfolio projects. |
| GitLab CI | Excellent pipelines, robust runner architecture. | We are hosting code on GitHub. | Rejected. |
| CircleCI | Very fast, docker-first. | Paid tiers can get expensive. | Rejected. |
| Jenkins | Extremely customizable. | Requires managing a Jenkins server, outdated UI. | Rejected. |

## 10. Task Queue

| Option | Pros | Cons | Tradeoffs / Decision |
|---|---|---|---|
| **Celery + Redis** | Battle-tested, integrates well with FastAPI and Redis. | Complex configuration, polling overhead. | **Chosen.** Standard for Python background workers (doc ingestion). |
| Dramatiq | Simpler than Celery, faster. | Smaller community. | Good alternative, but Celery is more recognizable on a resume. |
| Huey | Very lightweight and simple. | Lacks some advanced enterprise features. | Rejected. |
| Bull (Node.js) | Great for TS/JS. | Runs in Node, but we need Python for ML tasks. | Rejected. |