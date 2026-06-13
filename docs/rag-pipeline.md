# RAG Architecture Rationale

## 1. Why RAG over Fine-Tuning?
For customer support on dynamic documents, RAG is vastly superior to fine-tuning because:
1.  **Updatability:** When a company policy changes, you just swap the PDF. Fine-tuning requires expensive retraining.
2.  **Citations:** RAG allows us to point exactly to page 4 of the manual. Fine-tuning models cannot reliably cite sources.
3.  **Hallucination Control:** RAG explicitly bounds the model's knowledge to the provided context.

## 2. Component Rationale

*   **Document Ingestion (Celery Queue):** Parsing PDFs and generating embeddings is CPU/GPU intensive. Doing this synchronously would block the FastAPI event loop and time out HTTP requests.
*   **Parsing (PyMuPDF):** Chosen over pdfplumber because it is exponentially faster and extracts robust metadata (page numbers, structural blocks) natively.
*   **Hybrid Chunking:** Fixed-size chunking (e.g., exact 512 tokens) blindly slices sentences in half. Semantic chunking respects paragraphs, ensuring complete thoughts are vectorized. We use 512 tokens as a hard ceiling, with a 64-token overlap to ensure context at the boundary isn't lost.
*   **Embedding Model (`multilingual-e5-large`):** Outstanding performance for both Arabic and English. BGE-m3 was considered, but E5 showed better alignment for the specific customer support Q&A format.
*   **Hybrid Retrieval (Qdrant):** Dense vectors (embeddings) capture *meaning* (e.g., finding "refund" when the user types "money back"). Sparse vectors (BM25) capture *keywords* (e.g., finding a specific product SKU like "XJ-9000"). RRF (Reciprocal Rank Fusion) mathematically combines both rankings for the best of both worlds.
*   **Reranking (Cross-Encoder):** Retrieval models are fast but imprecise. Rerankers are slow but highly accurate. Fetching top-20 with Qdrant, then using a local cross-encoder to reorder them to top-5, drastically improves LLM answer quality.

## 3. Multilingual Strategy (Arabic Deep Dive)

*   **Morphological Challenges:** Arabic is highly inflected. A word like "wasyaktuboonaha" (and they will write it) is a single token containing conjunction, pronoun, verb, and object. 
*   **Solution:** We apply light Arabic normalization (normalizing Alef/Hamza variants) before embedding. The `multilingual-e5-large` model is trained on diverse Arabic structures, negating the need for aggressive stemming (which ruins semantic meaning).
*   **Cross-Lingual RAG:** Because the embedding space is multilingual, a user can ask a question in Arabic, the system will retrieve the correct English document chunk, and the LLM will generate the answer back in Arabic automatically.

## 4. Mode Enforcement Mechanisms (Guardrails)

*   **Mode 1 (KB Only):** 
    *   *Problem:* LLMs inherently want to answer questions using their training weights.
    *   *Solution:* We implement a **Citation Coverage & Overlap Check**. Instead of running heavy NLI models that add 1-second latency, we use prompt engineering to force the LLM to output citations. We then programmatically verify that the nouns/entities in the response overlap with the source chunks. If the overlap is too low (hallucination detected), the system drops the response and returns the `fallback_message`.
*   **Mode 2 (KB + AI):** The prompt explicitly instructs the LLM to use phrases like "Based on my general knowledge..." when the answer is not found in the provided context.
*   **Mode 3 (KB + Web):** Web search results are appended to the context window with the tag `[Source: Web - URL]`. The citation engine treats them identically to PDF chunks.