import asyncio
import heapq
import os

# Attempt to import sentence_transformers, but don't fail immediately if missing
try:
    from sentence_transformers import CrossEncoder, SentenceTransformer
except ImportError:
    SentenceTransformer = None
    CrossEncoder = None

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL_NAME", "BAAI/bge-reranker-base")


class RAGEngine:
    def __init__(self):
        self.embedding_model = None
        self.reranker_model = None

    def load_models(self):
        """Lazily load models onto the GPU when first needed."""
        if SentenceTransformer is None or CrossEncoder is None:
            raise ImportError(
                "sentence-transformers is not installed. Please `pip install sentence-transformers`"
            )

        if self.embedding_model is None:
            print(f"Loading Embedding Model: {EMBEDDING_MODEL_NAME}")
            self.embedding_model = SentenceTransformer(
                EMBEDDING_MODEL_NAME, device="cuda"
            )

        if self.reranker_model is None:
            print(f"Loading Reranker Model: {RERANKER_MODEL_NAME}")
            self.reranker_model = CrossEncoder(RERANKER_MODEL_NAME, device="cuda")

    async def compute_embeddings_async(self, texts: list[str]) -> list[list[float]]:
        """Asynchronously compute embeddings for a list of strings."""
        if self.embedding_model is None:
            self.load_models()

        # Run the blocking sentence-transformers call in a separate thread
        embeddings = await asyncio.to_thread(
            self.embedding_model.encode, texts, normalize_embeddings=True
        )
        return embeddings.tolist()

    async def rerank_documents_async(
        self, query: str, documents: list[str], top_k: int = 3
    ) -> list[str]:
        """Asynchronously score a query against documents and return the top K."""
        if not documents:
            return []

        if self.reranker_model is None:
            self.load_models()

        # Prepare pairs of (query, document)
        pairs = [[query, doc] for doc in documents]

        # Compute scores in a separate thread
        scores = await asyncio.to_thread(self.reranker_model.predict, pairs)

        # Use heapq.nlargest for O(N log K) performance instead of O(N log N) sort
        # zip pairs (score, doc) so heapq sorts primarily by score
        top_items = heapq.nlargest(top_k, zip(scores, documents))
        return [doc for score, doc in top_items]


def chunk_documents(
    documents: list[str], chunk_size: int = 200, overlap: int = 20
) -> list[str]:
    """Chunk documents into smaller overlapping text segments."""
    step = chunk_size - overlap
    chunked_docs = []
    append_chunk = chunked_docs.append

    for doc in documents:
        words = doc.split()
        num_words = len(words)

        if num_words <= chunk_size:
            append_chunk(doc)
        else:
            for i in range(0, num_words, step):
                append_chunk(" ".join(words[i : i + chunk_size]))

    return chunked_docs


def build_rag_prompt(query: str, top_chunks: list[str]) -> str:
    """Format the retrieved chunks into a standard LLM prompt."""
    context_str = "\n\n".join(
        f"Document {i + 1}:\n{chunk}" for i, chunk in enumerate(top_chunks)
    )
    return f"""You are a helpful AI assistant. Use the following context to answer the user's query. If the answer is not in the context, say "I don't know based on the context."

Context:
{context_str}

Query: {query}

Answer:"""


# Singleton instance for the server to use
rag_engine = RAGEngine()
