# High-Throughput Inference Server

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vktofly/high_throughput_inference/blob/main/demo.ipynb)
An MLOps project demonstrating model serving architecture, concurrency, and observability. This simulates a high-throughput endpoint (like vLLM) exposed via FastAPI and tracked by Prometheus.

## Live Demo
Click the **Open in Colab** badge above to launch a fully functioning RAG inference engine on a free Google T4 GPU. A public web UI (Gradio) will be generated for you to interact with the engine.

## Features
- **Concurrent Request Handling:** Exposes `/v1/chat/completions` using an async FastAPI architecture.
- **Mock LLM Engine:** Because this project is configured to run on CPU-only machines (Windows) without native C++ compilation tools, the inference engine is mocked. The mock perfectly simulates the delays associated with prefill and decoding phases of text generation.
- **Throughput Observability:** Uses Prometheus to expose `/metrics` for tracking `tokens_per_second` and `latency`.
- **Client Simulator:** Includes a load-testing script to spam the server with async requests.

## How to Run

1. **Install Dependencies**
```bash
uv sync
```

2. **Start the Inference Server**
```bash
uv run uvicorn src.api:app --host 127.0.0.1 --port 8000
```
*The server will initialize the MockLLMEngine and expose the API.*

3. **Run the Load Simulator**
Open a second terminal window and run:
```bash
uv run python client_simulator.py
```
*You will see the simulator fire 50 concurrent async requests and output the latency and tokens/sec for each.*

4. **View Prometheus Metrics**
While the server is running, navigate to `http://127.0.0.1:8000/metrics` in your browser to see the raw Prometheus metrics tracking queue depth, total tokens, and request counts.
