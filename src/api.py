import os
import time
import asyncio
import random
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel

from .monitoring import REQUEST_LATENCY, TOTAL_TOKENS_GENERATED, ACTIVE_REQUESTS

app = FastAPI(title="vLLM Inference Server Proxy")

class ChatRequest(BaseModel):
    model: str = "mock-llama-3-8b"
    messages: list[dict]
    max_tokens: int = 1024
    temperature: float = 0.7

@app.get("/metrics")
def metrics():
    """Expose Prometheus metrics."""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    
    try:
        # Simulate local LLM generation time
        # Random latency based on number of generated tokens
        num_tokens = random.randint(10, req.max_tokens if req.max_tokens < 100 else 100)
        
        # Assume 30 tokens per second generation speed
        sleep_time = num_tokens / 30.0
        await asyncio.sleep(sleep_time)
        
        # Track metrics
        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)
        
        TOTAL_TOKENS_GENERATED.inc(num_tokens)
        
        # Return OpenAI compatible format
        return {
            "id": "chatcmpl-mock",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"This is a dummy response. I generated {num_tokens} tokens.",
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": num_tokens,
                "total_tokens": 15 + num_tokens
            }
        }
    finally:
        ACTIVE_REQUESTS.dec()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8001)
