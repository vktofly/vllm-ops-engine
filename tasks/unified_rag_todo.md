# Task List: Unified RAG Endpoint

## Phase 1: Foundation

### Task 1: Update Memory Scheduler for Auxiliary Models
**Description:** Modify `get_optimal_memory_utilization` in `src/api.py` to accept a new parameter (e.g., `aux_models_mb=2048`) that reserves dedicated VRAM for the embedding and reranker models, ensuring vLLM leaves enough space.
**Acceptance criteria:**
- [ ] Memory scheduler subtracts `aux_models_mb` from available VRAM before calculating `gpu_memory_utilization`.
- [ ] Server successfully starts without CUDA OOM.
**Files likely touched:** `src/api.py`
**Estimated scope:** Small: 1 file

## Phase 2: Auxiliary Models

### Task 2: Implement Embedding Model Loader
**Description:** Create `src/rag_engine.py` to lazily load a lightweight embedding model (e.g. `sentence-transformers/all-MiniLM-L6-v2` or `BGE-small`) onto the GPU. Include a function to compute embeddings for a list of strings asynchronously.
**Acceptance criteria:**
- [ ] Embedding model is loaded successfully onto the `cuda` device.
- [ ] Provides an async-friendly inference function.
**Files likely touched:** `src/rag_engine.py`
**Estimated scope:** Small: 1 file

### Task 3: Implement Reranker Model Loader
**Description:** In `src/rag_engine.py`, add support for loading a CrossEncoder reranker (e.g. `BAAI/bge-reranker-base`). Provide an async function to score a query against a list of documents and return the top K documents.
**Acceptance criteria:**
- [ ] Reranker model is loaded successfully onto the `cuda` device.
- [ ] Inference function correctly sorts and returns the top K documents.
**Files likely touched:** `src/rag_engine.py`
**Estimated scope:** Small: 1 file

## Phase 3: Core Features

### Task 4: Build the `/v1/rag` API Endpoint
**Description:** Add a new `POST /v1/rag` route in `src/api.py`. The endpoint accepts a `query` and a list of `documents`. It must asynchronously execute the embedding and reranking steps using `src/rag_engine.py`, then pass the result to the LLM generator.
**Acceptance criteria:**
- [ ] Endpoint accepts standard JSON payload (query, documents, max_tokens, temperature).
- [ ] Orchestrates embedding (if retrieval is needed) and reranking.
**Files likely touched:** `src/api.py`
**Estimated scope:** Medium: 3-5 files

### Task 5: Implement RAG Prompt Template
**Description:** Inside the `/v1/rag` endpoint, format the reranked documents into a system prompt that constraints the LLM to answer the query based strictly on the provided context.
**Acceptance criteria:**
- [ ] Reranked documents are injected into the prompt.
- [ ] Output is streamed back to the client using vLLM's existing generator.
**Files likely touched:** `src/api.py`
**Estimated scope:** Small: 1 file

## Phase 4: Polish

### Task 6: End-to-End Testing Script
**Description:** Create `src/test_rag.py` to hit the `/v1/rag` endpoint with a sample user query and 10 dummy documents (some relevant, some irrelevant).
**Acceptance criteria:**
- [ ] Script prints the streaming generation output.
- [ ] The generated answer utilizes the correct documents.
**Files likely touched:** `src/test_rag.py`
**Estimated scope:** Small: 1 file
