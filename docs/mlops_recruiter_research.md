# Research Findings: What Recruiters Look for in LLM/MLOps Portfolios (2026)

Based on recent industry searches for MLOps and GenAI engineering roles, here is what recruiters and hiring managers prioritize, and how our project maps to these expectations.

## 1. Production Engineering vs. "Notebook Prototypes"
Recruiters actively filter out portfolios that only show Jupyter Notebook prototypes. They look for systems that are "production-ready."
* **What they want:** Docker containerization, CI/CD pipelines, API gateways, and proper error handling.
* **Our Project:** We already have the FastAPI controller, graceful degradation (OOM safe), and Pytest.
* **Gap:** We should explicitly mention Docker/Kubernetes deployment readiness in the writeup.

## 2. Specialization in LLM Infrastructure
Buzzwords like "Prompt Engineering" are no longer enough for engineering roles. Recruiters are looking for deep systems knowledge.
* **What they want:** Keywords like `Continuous Batching`, `PagedAttention` (KV-Cache management), and `Quantization` (AWQ, GPTQ, GGUF).
* **Our Project:** Our code actually uses an AWQ quantized model (`casperhansen/llama-3-8b-instruct-awq`) and relies on vLLM's Continuous Batching and PagedAttention, but we haven't highlighted this enough in the PDF!
* **Action:** Add a section detailing how we leverage Continuous Batching and AWQ Quantization to maximize throughput.

## 3. Quantifiable Impact & Cloud Cost Reduction
Hiring managers want to see that you understand the financial cost of running LLMs.
* **What they want:** Hard metrics like Tokens-Per-Second (TPS), latency reduction, and GPU VRAM savings.
* **Our Project:** We added the benchmark table, which is perfect. We can enhance it by explicitly tying the Auto-Tuning Memory Scheduler to "Cloud Cost Reduction" by allowing multi-tenant hosting on smaller GPUs (like the T4).

## 4. End-to-End RAG Evaluation
Building a RAG is easy; proving it works is hard.
* **What they want:** Evidence of RAG evaluation pipelines (using tools like `Ragas`, `DeepEval`, or `TruLens`) to track hallucination rates and retrieval recall.
* **Our Project:** We built the Min-Heap reranker, but we haven't mentioned *how* we evaluate its accuracy. 
* **Action (Future):** We could add "Automated RAG Evaluation via Ragas" to our Future Scope section.

## Summary of Next Steps for the PDF
To truly stand out, we should inject the following into the `writeup.tex`:
1. Mention **AWQ Quantization** and **Continuous Batching** as core throughput strategies.
2. Frame the architecture as completely **Docker / Container native**.
3. Add **Automated RAG Evaluation (Ragas)** to the Future Scope.
