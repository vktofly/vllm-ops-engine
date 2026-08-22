import asyncio
import random
from dataclasses import dataclass
from .protocol import AsyncLLMEngineProtocol

@dataclass
class MockGenerationResult:
    output_text: str
    generated_tokens: int

class MockAsyncLLMEngine:
    """
    An async simulated LLM Engine designed to mock the behavior of vLLM.
    Simulates prefill and decoding latency.
    """
    def __init__(self, token_speed: float = 30.0):
        self.token_speed = token_speed

    async def generate(self, prompt: str, max_tokens: int, temperature: float = 0.7) -> MockGenerationResult:
        # Simulate local LLM generation time
        num_tokens = min(max_tokens, random.randint(20, max(21, max_tokens)))
        
        # Assume token_speed tokens per second generation speed
        sleep_time = num_tokens / self.token_speed
        await asyncio.sleep(sleep_time)
        
        mock_response = f"This is a simulated response to: '{prompt[:20]}...' generated with {num_tokens} tokens."
        
        return MockGenerationResult(
            output_text=mock_response,
            generated_tokens=num_tokens
        )
