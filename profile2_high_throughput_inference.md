# Project 2: High-Throughput Local Inference Engine (vLLM)

## Overview
Package a quantized model inside a Dockerized FastAPI server that implements continuous batching and exposes an OpenAI-compatible endpoint with Prometheus metrics.

## Architecture & Tech Stack
- **Inference Engine:** vLLM (implements PagedAttention and continuous batching)
- **Model:** Quantized Llama-3 (AWQ or GGUF format)
- **API Layer:** FastAPI (Python)
- **Deployment:** Docker
- **Observability:** Prometheus + Grafana (for token throughput & latency tracking)

## Directory Structure (Target: `c:\Users\vikash\Documents\projects\vllm_inference_server`)
```text
vllm_inference_server/
├── src/
│   ├── api.py             # FastAPI wrapper / vLLM AsyncEngine integration
│   └── monitoring.py      # Prometheus metric collectors
├── docker/
│   ├── Dockerfile         # GPU-enabled vLLM Dockerfile
│   └── docker-compose.yml # Server + Prometheus + Grafana
├── grafana_dashboards/    # Pre-configured JSON dashboards
└── README.md
```

## Step-by-Step Build Plan
1. **Model Acquisition:** Download an AWQ-quantized model from HuggingFace to reduce VRAM requirements.
2. **Server Logic:** Write a FastAPI server that initializes the `vllm.AsyncLLMEngine`. Expose a `/v1/chat/completions` endpoint.
3. **Metrics Integration:** Add Prometheus middleware to FastAPI to track `tokens_per_second`, `request_latency`, and `queue_depth`.
4. **Containerization:** Write a Dockerfile using the official NVIDIA CUDA base image.
5. **Observability Stack:** Spin up Grafana and Prometheus alongside the FastAPI server via Docker Compose. Connect the dashboard to visualize GPU memory and throughput.
