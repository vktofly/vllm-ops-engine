from typing import Protocol

class GenerationResult(Protocol):
    """Protocol for the result of an LLM generation."""
    @property
    def output_text(self) -> str: ...
    
    @property
    def generated_tokens(self) -> int: ...

class AsyncLLMEngineProtocol(Protocol):
    """
    Protocol defining how the API layer interacts with the underlying LLM engine.
    This allows us to swap MockLLMEngine and vLLM easily.
    """
    async def generate(self, prompt: str, max_tokens: int, temperature: float = 0.7) -> GenerationResult:
        ...
