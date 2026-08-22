import time
from typing import Annotated
from fastapi import FastAPI, Depends
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel

from .engine.protocol import AsyncLLMEngineProtocol
from .engine.mock import MockAsyncLLMEngine
from .monitoring import MetricsRegistry

app = FastAPI(title="vLLM Inference Server Proxy")

# Global instances for the app (can be overridden in tests via dependency overrides)
engine_instance = MockAsyncLLMEngine()
metrics_registry = MetricsRegistry()

def get_engine() -> AsyncLLMEngineProtocol:
    return engine_instance

def get_metrics() -> MetricsRegistry:
    return metrics_registry

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
async def chat_completions(
    req: ChatRequest, 
    engine: Annotated[AsyncLLMEngineProtocol, Depends(get_engine)],
    metrics: Annotated[MetricsRegistry, Depends(get_metrics)]
):
    metrics.active_requests.inc()
    start_time = time.time()
    
    try:
        # Construct a simple prompt from messages (mocking behavior)
        prompt = " ".join([m.get("content", "") for m in req.messages])
        
        # Generation is completely abstracted behind the protocol
        result = await engine.generate(
            prompt=prompt, 
            max_tokens=req.max_tokens, 
            temperature=req.temperature
        )
        
        # Track metrics
        latency = time.time() - start_time
        metrics.request_latency.observe(latency)
        metrics.total_tokens_generated.inc(result.generated_tokens)
        
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
                        "content": result.output_text,
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": result.generated_tokens,
                "total_tokens": len(prompt.split()) + result.generated_tokens
            }
        }
    finally:
        metrics.active_requests.dec()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8001)
