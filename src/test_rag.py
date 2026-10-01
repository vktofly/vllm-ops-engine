import json
import time

import requests


def test_rag_endpoint():
    url = "http://127.0.0.1:8000/v1/rag"

    # Create a dummy set of documents. Some relevant, some irrelevant.
    documents = [
        "The Apollo 11 mission landed on the moon on July 20, 1969. It was a monumental achievement for humanity.",
        "Python is a high-level, interpreted programming language created by Guido van Rossum.",
        "The fastest land animal is the cheetah, which can reach speeds of up to 75 mph.",
        "The capital of France is Paris, famous for the Eiffel Tower and the Louvre.",
        "vLLM is a high-throughput and memory-efficient LLM serving engine using PagedAttention.",
        "Artificial Intelligence dates back to antiquity, with myths of artificial beings endowed with intelligence.",
        "To bake a chocolate cake, you need flour, sugar, cocoa powder, eggs, and butter. Bake at 350F for 30 minutes.",
        "Neil Armstrong and Buzz Aldrin were the first two humans to walk on the lunar surface during the Apollo 11 mission.",
        "The Pacific Ocean is the largest and deepest of Earth's oceanic divisions.",
        "In machine learning, RAG stands for Retrieval-Augmented Generation, which combines document retrieval with language modeling.",
    ]

    query = (
        "Who were the first people to walk on the moon and exactly when did it happen?"
    )

    payload = {
        "query": query,
        "documents": documents,
        "max_tokens": 100,
        "temperature": 0.3,
        "top_k": 2,
        "chunk_size": 50,
    }

    print(f"Sending RAG request...\nQuery: '{query}'\n")

    start = time.time()
    try:
        # stream=True is critical for reading the SSE stream in real-time
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        print("Response Stream:")
        print("-" * 40)

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[6:]

                    if data_str == "[DONE]":
                        break

                    try:
                        data_json = json.loads(data_str)
                        # Print tokens as they arrive
                        print(data_json.get("text", ""), end="", flush=True)
                    except json.JSONDecodeError:
                        pass

        print(f"\n\nCompleted in {time.time() - start:.2f} seconds.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed. Is the server running on port 8000? Error: {e}")


if __name__ == "__main__":
    test_rag_endpoint()
