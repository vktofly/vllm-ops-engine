# Task List: Unified RAG Endpoint

## Phase 1: Foundation

### Task 1: Update Memory Scheduler for Auxiliary Models
**Description:** Modify `get_optimal_memory_utilization` in `src/api.py` to accept a new parameter (e.g., `aux_models_mb=2048`) that reserves dedicated VRAM for the embedding and reranker models, ensuring vLLM leaves enough space.
**Acceptance criteria:**
- [x] Memory scheduler subtracts `aux_models_mb` from available VRAM before calculating `gpu_memory_utilization`.
- [x] Server successfully starts without CUDA OOM.
**Files likely touched:** `src/api.py`
**Estimated scope:** Small: 1 file

## Phase 2: Auxiliary Models

### Task 2: Implement Embedding Model Loader
**Description:** Create `src/rag_engine.py` to lazily load a lightweight embedding model onto the GPU. The model name should be configurable via the `EMBEDDING_MODEL_NAME` environment variable (default `BAAI/bge-small-en-v1.5`). Include a function to compute embeddings for a list of strings asynchronously.
**Acceptance criteria:**
- [x] Embedding model is loaded successfully onto the `cuda` device.
- [x] Provides an async-friendly inference function.
**Files likely touched:** `src/rag_engine.py`
**Estimated scope:** Small: 1 file

### Task 3: Implement Reranker Model Loader
**Description:** In `src/rag_engine.py`, add support for loading a CrossEncoder reranker. The model name should be configurable via the `RERANKER_MODEL_NAME` environment variable (default `BAAI/bge-reranker-base`). Provide an async function to score a query against a list of documents and return the top K documents.
**Acceptance criteria:**
- [x] Reranker model is loaded successfully onto the `cuda` device.
- [x] Inference function correctly sorts and returns the top K documents.
**Files likely touched:** `src/rag_engine.py`
**Estimated scope:** Small: 1 file

## Phase 3: Core Features

### Task 4: Build the `/v1/rag` API Endpoint
**Description:** Add a new `POST /v1/rag` route in `src/api.py`. The endpoint accepts a `query` and a list of `documents`. It must first chunk the provided documents, then asynchronously execute the embedding (if retrieval is needed) and reranking steps using `src/rag_engine.py`, then pass the result to the LLM generator.
**Acceptance criteria:**
- [x] Endpoint accepts standard JSON payload (query, documents, max_tokens, temperature).
- [x] Orchestrates embedding (if retrieval is needed) and reranking.
**Files likely touched:** `src/api.py`
**Estimated scope:** Medium: 3-5 files

### Task 5: Implement RAG Prompt Template
**Description:** Inside the `/v1/rag` endpoint, format the reranked documents into a system prompt that constraints the LLM to answer the query based strictly on the provided context.
**Acceptance criteria:**
- [x] Reranked documents are injected into the prompt.
- [x] Output is streamed back to the client using vLLM's existing generator.
**Files likely touched:** `src/api.py`
**Estimated scope:** Small: 1 file

## Phase 4: Polish

### Task 6: End-to-End Testing Script
**Description:** Create `src/test_rag.py` to hit the `/v1/rag` endpoint with a sample user query and 10 dummy documents (some relevant, some irrelevant).
**Acceptance criteria:**
- [x] Script prints the streaming generation output.
- [x] The generated answer utilizes the correct documents.
**Files likely touched:** `src/test_rag.py`
**Estimated scope:** Small: 1 file
