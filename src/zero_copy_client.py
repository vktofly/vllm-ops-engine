import time

import requests

from ipc_utils import (
    cleanup_shared_memory,
    create_shared_memory,
    read_string_from_memory,
    write_string_to_memory,
)


def run_zero_copy_inference(prompt: str, max_tokens: int = 512):
    prompt_shm_name = "ipc_prompt_block"
    output_shm_name = "ipc_output_block"

    # Pre-allocate large blocks (e.g. 5MB for prompt, 1MB for output)
    prompt_size = 5 * 1024 * 1024
    output_size = 1024 * 1024

    prompt_shm = None
    output_shm = None

    try:
        prompt_shm = create_shared_memory(prompt_shm_name, prompt_size)
        output_shm = create_shared_memory(output_shm_name, output_size)

        # 1. Write the prompt locally into memory
        write_string_to_memory(prompt_shm, prompt)

        # 2. Tell the server to generate (zero serialization)
        payload = {
            "prompt_shm_name": prompt_shm_name,
            "output_shm_name": output_shm_name,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        # This call blocks until generation is complete.
        # For real-time streaming, the client would poll output_shm in a separate thread.
        response = requests.post(
            "http://127.0.0.1:8000/v1/ipc/completions", json=payload
        )
        response.raise_for_status()

        # 3. Read the output locally from memory
        final_text = read_string_from_memory(output_shm)
        return final_text

    finally:
        if prompt_shm:
            cleanup_shared_memory(prompt_shm)
        if output_shm:
            cleanup_shared_memory(output_shm)


if __name__ == "__main__":
    prompt = "Explain the history of artificial intelligence in exactly one paragraph."
    start = time.time()
    try:
        result = run_zero_copy_inference(prompt)
        print(f"Generated in {time.time() - start:.3f}s:")
        print(result)
    except Exception as e:
        print(f"Could not connect to server: {e}")
