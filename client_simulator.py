import asyncio
import httpx
import time
import random

API_URL = "http://127.0.0.1:8000/v1/chat/completions"
NUM_REQUESTS = 50

PROMPTS = [
    "Write a python script for a fast api server.",
    "Explain quantum computing in simple terms.",
    "What are the best practices for MLOps?",
    "How does continuous batching work in vLLM?",
    "Generate a recipe for chocolate cake.",
    "What is the capital of France?",
    "Translate 'hello world' to Spanish.",
    "Summarize the plot of Inception.",
    "Give me 5 reasons to learn Rust.",
    "How do transformers handle positional encoding?"
]

async def make_request(client, idx):
    prompt = random.choice(PROMPTS)
    payload = {
        "model": "mock-llama-3-8b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": random.randint(50, 150)
    }
    
    start = time.time()
    try:
        response = await client.post(API_URL, json=payload, timeout=30.0)
        data = response.json()
        latency = time.time() - start
        
        comp_tokens = data.get('usage', {}).get('completion_tokens', 0)
        tps = comp_tokens / latency if latency > 0 else 0
        
        print(f"Req {idx:02d} | Tokens: {comp_tokens:3d} | "
              f"Latency: {latency:.2f}s | "
              f"Throughput: {tps:.1f} t/s")
    except Exception as e:
        print(f"Req {idx:02d} | FAILED: {e}")

async def main():
    print(f"Starting simulation of {NUM_REQUESTS} concurrent requests...")
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        # Fire off all requests concurrently
        tasks = [make_request(client, i) for i in range(NUM_REQUESTS)]
        await asyncio.gather(*tasks)
        
    total_time = time.time() - start_time
    print("-" * 50)
    print(f"Simulation Complete in {total_time:.2f} seconds.")
    print("Check Prometheus metrics at http://127.0.0.1:8000/metrics")

if __name__ == "__main__":
    asyncio.run(main())
