import os
import time
import torch
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from prometheus_client import generate_latest
from monitoring import MetricsRegistry
from ipc_utils import get_shared_memory, read_string_from_memory, write_string_to_memory
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

app = FastAPI(title="High-Throughput vLLM Inference Engine")

metrics = MetricsRegistry()

@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)
        
    start_time = time.time()
    metrics.active_requests.inc()
    
    try:
        response = await call_next(request)
        return response
    finally:
        metrics.active_requests.dec()
        process_time = time.time() - start_time
        metrics.request_latency.observe(process_time)

@app.get("/metrics")
def metrics_endpoint():
    return Response(generate_latest(), media_type="text/plain")

def get_optimal_memory_utilization(reserve_mb: int = 2048) -> float:
    """
    Auto-Tuning Memory Scheduler: 
    Dynamically profile GPU memory to configure vLLM's gpu_memory_utilization.
    Reserves a fixed amount of VRAM for OS and PyTorch context overhead.
    """
    if not torch.cuda.is_available():
        print("CUDA not available. Falling back to default gpu_memory_utilization (0.90)")
        return 0.90
        
    free_mem, total_mem = torch.cuda.mem_get_info()
    
    reserve_bytes = reserve_mb * 1024 * 1024
    available_for_vllm = total_mem - reserve_bytes
    
    # Calculate safe fraction for vLLM
    utilization = available_for_vllm / total_mem
    
    # Clamp between 0.4 and 0.98 to avoid OOM or underutilization
    clamped_utilization = max(0.4, min(0.98, utilization))
    
    print(f"GPU Mem Total: {total_mem / (1024**3):.2f} GB")
    print(f"GPU Mem Free: {free_mem / (1024**3):.2f} GB")
    print(f"Reserved: {reserve_mb} MB")
    print(f"Auto-Tuning Memory Scheduler -> gpu_memory_utilization set to: {clamped_utilization:.2f}")
    
    return clamped_utilization

# Engine setup
MODEL_NAME = os.getenv("MODEL_NAME", "casperhansen/llama-3-8b-instruct-awq")

optimal_utilization = get_optimal_memory_utilization(reserve_mb=2048)

engine_args = AsyncEngineArgs(
    model=MODEL_NAME,
    quantization="awq",
    gpu_memory_utilization=optimal_utilization,
    max_model_len=4096,
    trust_remote_code=True,
    enforce_eager=False, # Use CUDA graphs for max throughput
    enable_prefix_caching=True, # Task 1: Enable global prefix caching
)

engine = AsyncLLMEngine.from_engine_args(engine_args)

class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7

@app.post("/v1/completions")
async def completions(request: ChatRequest):
    request_id = random_uuid()
    sampling_params = SamplingParams(
        temperature=request.temperature, 
        max_tokens=request.max_tokens
    )
    
    try:
        results_generator = engine.generate(request.prompt, sampling_params, request_id)
        
        final_output = None
        async for request_output in results_generator:
            final_output = request_output
            
        if final_output is None:
            raise HTTPException(status_code=500, detail="Generation failed.")
            
        # Update prometheus metrics
        tokens_generated = len(final_output.outputs[0].token_ids)
        metrics.total_tokens_generated.inc(tokens_generated)
            
        return {
            "id": request_id,
            "text": final_output.outputs[0].text
        }
    except ValueError as e:
        # Gracefully handle vLLM validations (e.g., prompt > max_model_len)
        engine.abort(request_id)
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except torch.cuda.OutOfMemoryError:
        # OOM-Safe Graceful Degradation: Abort this request to save the engine
        engine.abort(request_id)
        raise HTTPException(status_code=503, detail="Server is out of memory. Request gracefully aborted.")
    except Exception as e:
        # Catch-all to ensure the engine doesn't get stuck with a zombie request
        engine.abort(request_id)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

class IPCRequest(BaseModel):
    prompt_shm_name: str
    output_shm_name: str
    max_tokens: int = 512
    temperature: float = 0.7

@app.post("/v1/ipc/completions")
async def ipc_completions(request: IPCRequest):
    request_id = random_uuid()
    
    try:
        prompt_shm = get_shared_memory(request.prompt_shm_name)
        prompt_text = read_string_from_memory(prompt_shm)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read prompt from SHM: {str(e)}")
        
    try:
        output_shm = get_shared_memory(request.output_shm_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to access output SHM: {str(e)}")
        
    sampling_params = SamplingParams(
        temperature=request.temperature, 
        max_tokens=request.max_tokens
    )
    
    try:
        results_generator = engine.generate(prompt_text, sampling_params, request_id)
        
        final_output = None
        async for request_output in results_generator:
            final_output = request_output
            # Stream the accumulated text to shared memory directly
            current_text = request_output.outputs[0].text
            write_string_to_memory(output_shm, current_text)
            
        if final_output is None:
            raise HTTPException(status_code=500, detail="Generation failed.")
            
        # Write termination explicitly if needed, but HTTP return also signals completion
        
        # Update prometheus metrics
        tokens_generated = len(final_output.outputs[0].token_ids)
        metrics.total_tokens_generated.inc(tokens_generated)
        
        return {"status": "completed", "id": request_id}
        
    except ValueError as e:
        engine.abort(request_id)
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except torch.cuda.OutOfMemoryError:
        engine.abort(request_id)
        raise HTTPException(status_code=503, detail="Server is out of memory. Request gracefully aborted.")
    except Exception as e:
        engine.abort(request_id)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
