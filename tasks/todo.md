# Task List: Zero-Copy IPC

## Phase 1: Foundation

### Task 1: Enable vLLM Prefix Caching
**Description:** Configure the AsyncLLMEngine to enable prefix caching, allowing the KV cache to automatically retain shared system prompts across multiple agent interactions.
**Acceptance criteria:**
- [x] `enable_prefix_caching=True` is passed to `AsyncEngineArgs` in `src/api.py`.
- [x] The server boots successfully without CUDA errors.

### Task 2: Create Shared Memory Manager Utility
**Description:** Create a robust utility module `src/ipc_utils.py` that handles the lifecycle (creation, reading, writing, and cleanup) of `multiprocessing.shared_memory` blocks.
**Acceptance criteria:**
- [x] Functions to allocate memory blocks, write string/bytes, and read them.
- [x] Safe cleanup function that unlinks memory even on crashes.
**Files likely touched:** `src/ipc_utils.py`

## Phase 2: Core Features

### Task 3: Build IPC Control Endpoint
**Description:** Create a new FastAPI route `/v1/ipc/completions` that accepts a payload containing the name of a shared memory block (where the prompt lives) and the name of an output block.
**Acceptance criteria:**
- [x] Endpoint successfully reads the prompt string directly from the specified memory block.
- [x] Endpoint queues the generation request in vLLM.
**Files likely touched:** `src/api.py`

### Task 4: Stream Generator to Shared Memory
**Description:** Modify the generation loop for the IPC endpoint to continuously write the output text chunks directly into the designated shared memory output block.
**Acceptance criteria:**
- [x] Output text is encoded and appended to the shared memory block in real-time.
- [x] A termination signal (e.g., a specific byte sequence) is written when generation finishes.
**Files likely touched:** `src/api.py`, `src/ipc_utils.py`

## Phase 3: Polish

### Task 5: Build Zero-Copy Client Simulator
**Description:** Create `src/zero_copy_client.py` to act as the agent. It should allocate memory, write the prompt, trigger the IPC endpoint, and read the streaming response from memory.
**Acceptance criteria:**
- [x] Client successfully interacts with the server entirely via shared memory for payloads.
**Files likely touched:** `src/zero_copy_client.py`

### Task 6: End-to-End Latency Benchmark
**Description:** Write a benchmarking script to compare the end-to-end latency of a 10k token prompt via standard HTTP JSON vs the new Zero-Copy IPC route.
**Acceptance criteria:**
- [x] Benchmark outputs clear latency metrics proving the elimination of serialization overhead.
**Files likely touched:** `src/benchmark_ipc.py`
