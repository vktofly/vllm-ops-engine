import asyncio
import aiohttp
import time

URL = "http://localhost:8001/v1/chat/completions"

# Concurrent requests to simulate high-throughput batching load
NUM_REQUESTS = 20

async def fetch(session, i):
    payload = {
        "model": "gemini-2.5-flash",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Write a haiku about a robot named #{i}."}
        ],
        "max_tokens": 100
    }
    
    start_time = time.time()
    async with session.post(URL, json=payload) as response:
        res = await response.json()
        latency = time.time() - start_time
        
        # We assume the mock returns OpenAI format
        usage = res.get("usage", {})
        tokens = usage.get("completion_tokens", 0)
        
        return {
            "id": i,
            "latency": latency,
            "tokens": tokens,
            "status": response.status
        }

async def main():
    print(f"Starting load test with {NUM_REQUESTS} concurrent requests...")
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, i) for i in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    total_tokens = 0
    successful = 0
    
    for r in results:
        if isinstance(r, dict) and r.get("status") == 200:
            successful += 1
            total_tokens += r.get("tokens", 0)
        else:
            print(f"Error: {r}")
            
    tps = total_tokens / total_time
    
    print("\n--- Load Test Results ---")
    print(f"Total Requests: {NUM_REQUESTS}")
    print(f"Successful: {successful}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Total Tokens Generated: {total_tokens}")
    print(f"Tokens Per Second (TPS): {tps:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
