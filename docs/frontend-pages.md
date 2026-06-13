# Frontend Pages Design

## 1. Landing Page
*   **User Flows:** View hero section -> View features (modes 1,2,3) -> View pricing -> Click "Get Started" to route to `/register`.
*   **Components:** `HeroSection`, `FeatureGrid`, `InteractiveDemoWidget`, `PricingTable`, `Footer`.
*   **State Management:** Local state only (static content).
*   **UX Rationale:** Optimized for conversion and SEO. Clear explanation of Arabic/English capabilities.

## 2. Login & Register Pages
*   **User Flows:** Enter credentials -> Validation error (if invalid) -> Submit -> Store JWT -> Redirect to `/dashboard`.
*   **Components:** `AuthForm`, `SocialLoginButtons` (Google/GitHub).
*   **State Management:** `react-hook-form` + `zod` for validation. Zustand for storing the user session upon success.
*   **UX Rationale:** Clean, distraction-free layout (split screen with branding on left, form on right).

## 3. Dashboard (Main Overview)
*   **User Flows:** Login -> View high-level stats -> Quick action to "Create Agent" or "View Chats".
*   **Components:** `Sidebar`, `TopNav`, `StatCard`, `RecentActivityList`.
*   **State Management:** React Query fetches `GET /analytics/overview`.
*   **UX Rationale:** Instant visibility into usage limits and recent customer interactions.

## 4. Agent Creation Wizard
*   **User Flows:** Step 1: Name & Language -> Step 2: Select Mode (1,2,3) -> Step 3: Link KBs -> Step 4: System Prompt -> Finish & Deploy.
*   **Components:** `WizardStepper`, `ModeSelectorCard`, `KBCheckboxList`, `PromptEditor`.
*   **State Management:** Zustand to hold multi-step form data until the final submit.
*   **UX Rationale:** Breaking creation into steps prevents cognitive overload. Mode selection visually explains differences.

## 5. Knowledge Base & Document Management
*   **User Flows:** Click "Upload" -> Drag and Drop PDF -> See progress bar -> See status change from "Pending" to "Ready".
*   **Components:** `DragDropZone`, `DocumentTable`, `StatusBadge`.
*   **State Management:** React Query polling (`refetchInterval: 3000`) while document status is `pending` or `processing`.
*   **UX Rationale:** Asynchronous processing means the user needs clear visual feedback that chunks are being generated in the background.

## 6. Chat Playground
*   **User Flows:** Select Agent -> Type message -> View streaming response -> Inspect citations -> Inspect raw JSON metadata (for debugging).
*   **Components:** `ChatUI`, `MessageBubble`, `CitationTooltip`, `DebugPanel`.
*   **State Management:** Local array of messages. Custom hook `useSSE` to handle the streaming chunk events.
*   **UX Rationale:** Split-pane design allows the developer/admin to chat on the left and see exactly *why* the AI answered that way (sources, confidence score) on the right.

## 7. Analytics Dashboard
*   **User Flows:** Select date range -> View charts -> Export to CSV.
*   **Components:** `DateRangePicker`, `LineChart` (Recharts), `CostGauge`.
*   **State Management:** React Query with parameterized queries (`?days=7`).
*   **UX Rationale:** Visual data representation helps non-technical managers understand ROI and volume.

## 8. Evaluation Dashboard (NEW)
*   **User Flows:** View average Groundedness/Relevance scores -> Spot a dip in quality -> Click into individual flagged messages -> Read the user's thumbs_down comment.
*   **Components:** `EvalScoreCard`, `QualityTrendChart`, `FeedbackTable`.
*   **State Management:** React Query for fetching paginated evaluation data.
*   **UX Rationale:** Bridges the gap between MLOps (AI metrics) and Customer Success (User feedback) in one unified view.

## 9. Global Architecture
*   **Routing:** Next.js App Router (`app/(dashboard)/agents/[id]/page.tsx`).
*   **RTL Strategy:** Tailwind CSS logical properties (e.g., `ps-4` instead of `pl-4`). The `html dir="rtl"` tag flips the entire UI seamlessly for Arabic users based on the `next-intl` locale.
*   **Theme:** `next-themes` integrated with `shadcn/ui` for dark/light mode out of the box.