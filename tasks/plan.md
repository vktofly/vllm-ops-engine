# Implementation Plan: Global Prefix Caching & Shared Memory Tensors

## Overview
Implement a zero-copy inter-process communication (IPC) layer for the vLLM server to completely bypass HTTP serialization overhead for co-located agents. This combines vLLM's prefix caching with Python's `multiprocessing.shared_memory` to enable instantaneous "infinite context" interactions.

## Architecture Decisions
- **Shared Memory:** We will use standard library `multiprocessing.shared_memory` for moving token arrays between the client and server instead of NCCL/Arrow to minimize complex C++ dependencies.
- **Prefix Caching:** We will utilize vLLM's native `enable_prefix_caching=True` flag to let the engine hash and cache system prompts at the KV cache level automatically.
- **Control Plane:** We will add a dedicated `/v1/ipc/completions` endpoint that only accepts shared memory block names (metadata) instead of full JSON text prompts.

## Task List

### Phase 1: Foundation
- [ ] Task 1: Enable vLLM Prefix Caching
- [ ] Task 2: Create Shared Memory Manager Utility

### Checkpoint: Foundation
- [ ] Engine starts correctly with prefix caching enabled
- [ ] Shared memory blocks can be created, written to, read from, and unlinked without memory leaks

### Phase 2: Core Features
- [ ] Task 3: Build IPC Control Endpoint
- [ ] Task 4: Stream Generator to Shared Memory

### Checkpoint: Core Features
- [ ] The engine can accept a prompt reference via IPC and write generated tokens to a designated output memory block.

### Phase 3: Polish
- [ ] Task 5: Build Zero-Copy Client Simulator
- [ ] Task 6: End-to-End Latency Benchmark

### Checkpoint: Complete
- [ ] Client can send a massive prompt and receive a response with verifiable 0ms HTTP serialization overhead.
- [ ] Ready for review

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Shared Memory Leaks | High | Implement strict `try/finally` blocks and a periodic garbage collection task for orphaned memory blocks. |
| vLLM Prefix Cache Thrashing | Med | Tune `gpu_memory_utilization` to ensure enough KV cache space is available for long-lived prefixes. |

## Open Questions
- Should we support dynamic resizing of the output shared memory block if generation exceeds the initially allocated block size, or enforce a strict max-token allocation upfront?
