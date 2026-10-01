# High-Throughput vLLM Inference Engine
*By [Vikash Kumar](https://vktofly.github.io/) — Full Stack AI Engineer & Founder*
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vktofly/vllm-ops-engine/blob/main/demo.ipynb)

📄 **[Read the Architecture Writeup (Overview)](./docs/writeup.pdf)**

🔬 **[Read the Technical Research Paper (arXiv Format)](./docs/research_paper.pdf)**

An MLOps project demonstrating a high-performance model serving architecture designed specifically for autonomous multi-agent workloads. Built around the vLLM asynchronous engine, it features zero-copy IPC for massive prompt offloading, unified RAG endpoints with O(N log K) reranking, and dynamic cross-platform hardware abstraction.

## Live Demo
Click the **Open in Colab** badge above to launch a fully functioning RAG inference engine on a free Google T4 GPU. A public web UI (Gradio) will be automatically generated for you to interact with the engine.

## Advanced Features
- **Cross-Platform Engine Abstraction**: Seamlessly transitions between the native `vLLM AsyncEngine` (on CUDA/Linux) and a highly accurate `MockLLMEngine` (on Windows/CPU), ensuring uninterrupted development cycles without requiring an expensive local GPU.
- **Zero-Copy IPC (Shared Memory)**: A dedicated `/v1/ipc/completions` endpoint utilizing POSIX shared memory. This enables external orchestrators to transmit enormous prompt topologies directly into RAM, completely bypassing the HTTP body and JSON deserialization overhead.
- **Unified RAG Endpoint (`/v1/rag`)**: Consolidates document chunking, embedding (via `sentence-transformers`), and semantic reranking. Implements an **O(N log K) Min-Heap algorithm** for high-speed retrieval that avoids the O(N log N) bottlenecks of traditional sorting.
- **Auto-Tuning Memory Scheduler**: Profiles available VRAM at startup and reserves dynamic margins for OS and auxiliary models, preventing VRAM fragmentation. Implements OOM-safe graceful degradation to abort individual requests without crashing the server.
- **Strict SRP Architecture**: A thin FastAPI presentation controller (`api.py`) coupled with purely functional domain logic (`rag_engine.py`), ensuring extreme modularity and testability.
- **Throughput Observability**: Uses Prometheus to expose `/metrics` for real-time tracking of `tokens_per_second`, active requests, and tail latencies.

## How to Run Locally (Development Mode)

1. **Install Dependencies**
```bash
uv sync
```

2. **Start the Inference Server**
```bash
uv run uvicorn src.api:app --host 127.0.0.1 --port 8000
```
*On Windows, the server will automatically detect the lack of CUDA and initialize the `MockLLMEngine`.*

3. **Run the Load Simulator**
Open a second terminal window and run:
```bash
uv run python client_simulator.py
```
*Fires concurrent async requests and benchmarks the latency and tokens/sec for each.*

4. **View Prometheus Metrics**
While the server is running, navigate to `http://127.0.0.1:8000/metrics` in your browser to see the raw Prometheus telemetry.

## Testing
The repository includes a comprehensive `pytest` suite for the domain logic:
```bash
uv run pytest -v tests/
```
