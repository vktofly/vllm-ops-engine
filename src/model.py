import time
import random

class MockLLMEngine:
    """
    A simulated LLM Engine designed to mock the behavior of vLLM or llama.cpp.
    Used for local testing on machines without C++/CUDA support, allowing us
    to test the API's concurrency, batching architecture, and Prometheus metrics.
    """
    def __init__(self):
        print("Initializing MockLLMEngine (Simulating C++ backend loading...)")
        time.sleep(1.0) # Simulate loading weights
        print("Mock Model initialized successfully.")
        
    def __call__(self, prompt, max_tokens=128, temperature=0.7, **kwargs):
        """
        Simulates generation. Tokens take time to generate.
        """
        # Calculate how many tokens we will 'generate'
        num_tokens = min(max_tokens, random.randint(20, 128))
        
        # Simulate processing delay:
        # Time to first token (prefill) + Time per output token (decode)
        prefill_time = len(prompt) * 0.001
        decode_time = num_tokens * 0.02
        
        time.sleep(prefill_time + decode_time)
        
        mock_response = f"This is a simulated response to: '{prompt[:20]}...' generated with {num_tokens} tokens."
        
        return {
            "choices": [{"text": mock_response}],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": num_tokens,
                "total_tokens": len(prompt.split()) + num_tokens
            }
        }

def load_model() -> MockLLMEngine:
    return MockLLMEngine()
