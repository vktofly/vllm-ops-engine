import gradio as gr
import requests
import json
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/v1/rag")

DEFAULT_DOCS = """The High-Throughput Inference Engine uses zero-copy shared memory.
It was built to solve the GPU IPC bottleneck.
It natively supports RAG using sentence-transformers for embedding and reranking.
It processes chunking and reranking synchronously but offloads LLM inference asynchronously.
"""

def predict(message, history, custom_docs):
    # Split the docs by newline to simulate multiple documents
    docs = [d.strip() for d in custom_docs.split('\n') if d.strip()]
    
    payload = {
        "query": message,
        "documents": docs,
        "top_k": 3,
        "stream": True
    }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            stream=True
        )
        
        if response.status_code != 200:
            yield f"Error from backend: {response.text}"
            return
            
        partial_message = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    data_str = decoded_line[6:]
                    if data_str == '[DONE]':
                        break
                    
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                partial_message += delta["content"]
                                yield partial_message
                    except json.JSONDecodeError:
                        continue
                        
    except requests.exceptions.ConnectionError:
        yield "Error: Could not connect to the backend. Is the FastAPI server running on port 8000?"
    except Exception as e:
        yield f"An unexpected error occurred: {str(e)}"

demo = gr.ChatInterface(
    predict,
    additional_inputs=[
        gr.Textbox(value=DEFAULT_DOCS, label="Knowledge Base (1 doc per line)", lines=5)
    ],
    title="High-Throughput RAG Inference Engine",
    description="Test the zero-copy RAG inference engine. The Knowledge Base text is embedded and reranked on the fly."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=True)
