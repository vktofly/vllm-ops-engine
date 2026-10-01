# Research Notes: High-Throughput LLM Inference (vLLM)

This document contains a summary of primary research papers and concepts relevant to building a high-throughput local inference engine using vLLM, continuous batching, and quantized models.

## 1. PagedAttention & vLLM
* **Paper:** "Efficient Memory Management for Large Language Model Serving with PagedAttention" (SOSP 2023)
* **Authors:** Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, et al.
* **Significance:** This is the foundational paper for vLLM. It introduces **PagedAttention**, an algorithm inspired by virtual memory in OS. It partitions the Key-Value (KV) cache into non-contiguous blocks (pages). This nearly eliminates memory fragmentation in the KV cache, which historically restricted batch sizes. PagedAttention allows for 2-4x higher throughput compared to prior systems.
* **Relevance to Project:** vLLM is the core inference engine of the architecture. Understanding PagedAttention is key to tuning metrics like `gpu_memory_utilization` and max batch sizes.

## 2. Continuous Batching (Iteration-Level Scheduling)
* **Paper:** "Orca: A Distributed Serving System for Transformer-Based Generative Models" (OSDI 2022)
* **Significance:** While vLLM popularized it, Orca introduced the concept of **continuous batching** (or iteration-level scheduling). Unlike static batching which waits for the longest request in a batch to finish, continuous batching evicts finished requests at the token level and injects new ones immediately. 
* **Relevance to Project:** Explains why vLLM achieves such high throughput and justifies tracking `queue_depth` and `tokens_per_second` in Prometheus.

## 3. AWQ: Activation-aware Weight Quantization
* **Paper:** "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration" (MLSys 2024 Best Paper)
* **Significance:** Identifies that protecting ~1% of "salient" weight channels (based on activation distributions) significantly reduces quantization error. It is extremely hardware-friendly and enables massive speedups on GPUs.
* **Relevance to Project:** The project aims to use an AWQ or GGUF quantized Llama-3 model. AWQ is natively supported by vLLM (alongside optimized kernels like Marlin) and is the recommended format for enterprise-grade GPU serving, making it the ideal choice for this FastAPI + Docker deployment.

## 4. Recent Developments (2024/2025)
* **vAttention:** "vAttention: Dynamic Memory Management for Serving LLMs without PagedAttention" proposes using low-level OS demand paging for contiguous virtual memory instead of custom attention kernels. 
* **FairBatching:** Proposes dynamic budget-adjustment to prevent prefill queuing delays caused by prioritizing decode tasks.
* **GGUF (GPT-Generated Unified Format):** While not an algorithm paper, GGUF has become the community standard for local inference via `llama.cpp`. However, for high-throughput GPU serving (the goal of this project), AWQ within vLLM is generally preferred due to its optimization for fused CUDA kernels.

## Summary for Project Implementation
* **Engine:** vLLM (leverages PagedAttention & Continuous Batching for max throughput).
* **Model Format:** AWQ is recommended over GGUF for this stack, as vLLM is highly optimized for AWQ GPU kernels.
* **Metrics:** Focus on `tokens_per_second` and latency, as continuous batching fundamentally changes how batching delays affect overall request latency.
