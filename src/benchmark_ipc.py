import time
import requests
from zero_copy_client import run_zero_copy_inference

def benchmark_standard_http(prompt: str):
    payload = {
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.7
    }
    response = requests.post("http://127.0.0.1:8000/v1/completions", json=payload)
    response.raise_for_status()
    return response.json()["text"]

def run_benchmarks():
    # 1. Create a massive prompt to simulate multi-agent memory context or RAG retrieval
    # ~50,000 words
    huge_prompt = "Agent Context " * 50000 
    
    payload_size_mb = len(huge_prompt.encode('utf-8')) / 1024 / 1024
    print(f"Payload size: {payload_size_mb:.2f} MB")
    
    # Warmup
    try:
        benchmark_standard_http("warmup")
        run_zero_copy_inference("warmup")
    except Exception:
        print("Server not running. Please start the server on port 8000 to run actual benchmarks.")
        return
        
    print("\n--- Running Standard HTTP Benchmark ---")
    start = time.time()
    benchmark_standard_http(huge_prompt)
    http_time = time.time() - start
    print(f"Standard HTTP Latency: {http_time:.4f}s")
    
    print("\n--- Running Zero-Copy IPC Benchmark ---")
    start = time.time()
    run_zero_copy_inference(huge_prompt)
    ipc_time = time.time() - start
    print(f"Zero-Copy IPC Latency: {ipc_time:.4f}s")
    
    print("\n--- Results ---")
    print(f"Speedup: {http_time / ipc_time:.2f}x faster with IPC")
    
if __name__ == "__main__":
    run_benchmarks()
