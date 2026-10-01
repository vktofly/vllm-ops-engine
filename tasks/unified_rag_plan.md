# Implementation Plan: Unified RAG Endpoint

## Overview
This feature integrates an embedding model and a reranking model directly into the existing vLLM API server, exposing a single `/v1/rag` endpoint. Instead of developers orchestrating three separate microservices (embedding, ranking, generation), this unified engine handles the entire RAG pipeline internally. It dynamically balances the GPU memory pool between the auxiliary models and the vLLM generation engine.

## Architecture Decisions
- **Model Colocation**: We will use `sentence-transformers` (or `vLLM`'s native embedding support if available) to load lightweight embedding (e.g., `BAAI/bge-small-en-v1.5`) and reranking (e.g., `BAAI/bge-reranker-base`) models on the same GPU.
- **VRAM Partitioning**: We will update the `get_optimal_memory_utilization` function in `src/api.py` to reserve an explicit memory block (e.g., 1.5 - 2GB) for the embedding and reranking models, preventing vLLM from hoarding 100% of the VRAM.
- **Synchronous vs Asynchronous Aux Models**: To avoid blocking the event loop while embedding or reranking, we should run the auxiliary model inferences in a ThreadPoolExecutor or leverage batched processing if possible.

## Task List

### Phase 1: Foundation (VRAM Partitioning)
- [ ] Task 1: Update Memory Scheduler to reserve VRAM for auxiliary models.

### Checkpoint: Foundation
- [ ] Server boots correctly with the new memory scheduler logic.
- [ ] vLLM successfully starts with a reduced memory utilization footprint.

### Phase 2: Auxiliary Models
- [ ] Task 2: Implement Embedding model loader and inference wrapper.
- [ ] Task 3: Implement Reranker model loader and inference wrapper.

### Checkpoint: Auxiliary Models
- [ ] The models can load successfully onto the GPU alongside vLLM without throwing OOM errors.
- [ ] Basic unit test for generating embeddings and reranking scores passes.

### Phase 3: Core Features
- [ ] Task 4: Build the `/v1/rag` FastAPI endpoint to orchestrate embedding, reranking, and generation.
- [ ] Task 5: Implement the RAG prompt template to inject top-k context.

### Checkpoint: Core Features
- [ ] End-to-end RAG pipeline works when hitting `/v1/rag`.
- [ ] The response is streamed correctly using the existing vLLM generation setup.

### Phase 4: Polish
- [ ] Task 6: Create an end-to-end test script `src/test_rag.py`.

### Checkpoint: Complete
- [ ] All acceptance criteria met.
- [ ] Ready for review.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| CUDA Out of Memory | High | Accurately estimate the VRAM needed for embedding/reranking models and aggressively cap vLLM's `gpu_memory_utilization`. |
| Event Loop Blocking | Med | Wrap the blocking `sentence-transformers` inference calls in `asyncio.to_thread` to preserve FastAPI concurrency. |
| Slow TTFT (Time To First Token) | Med | Restrict the number of documents passed to the reranker (Top-K) to ensure the ranking phase doesn't throttle generation. |

## Resolved Questions
- **Model flexibility**: We expose model names (embedding/reranker) as environment variables (`EMBEDDING_MODEL_NAME`, `RERANKER_MODEL_NAME`) to allow users to swap out BGE for Nomic or others.
- **Chunking support**: We will support chunking of documents inside the `/v1/rag` endpoint to ensure long documents fit in context and improve retrieval precision.
