import pytest
from src.rag_engine import chunk_documents, build_rag_prompt

def test_chunk_documents_splits_large_text_correctly():
    """Verify that a document exceeding chunk_size is split with the correct overlap."""
    # Arrange
    text = " ".join([f"word{i}" for i in range(100)])
    chunk_size = 50
    overlap = 10
    
    # Act
    chunks = chunk_documents([text], chunk_size=chunk_size, overlap=overlap)
    
    # Assert
    assert len(chunks) == 3
    # Check bounds
    assert "word0" in chunks[0]
    assert "word49" in chunks[0]
    
    # Check overlap (chunk 1 starts at step = 50-10 = 40)
    assert chunks[1].startswith("word40")
    assert chunks[1].endswith("word89")
    
    # Check remainder
    assert chunks[2].startswith("word80")
    assert chunks[2].endswith("word99")

def test_chunk_documents_leaves_small_text_whole():
    """Verify that a document smaller than chunk_size is returned as a single chunk."""
    # Arrange
    text = "This is a short sentence."
    
    # Act
    chunks = chunk_documents([text], chunk_size=10, overlap=5)
    
    # Assert
    assert len(chunks) == 1
    assert chunks[0] == text

def test_build_rag_prompt_formats_correctly():
    """Verify that the RAG prompt concatenates documents with proper numbering."""
    # Arrange
    query = "What color is the sky?"
    top_chunks = ["The sky is blue.", "It can also be gray."]
    
    # Act
    prompt = build_rag_prompt(query, top_chunks)
    
    # Assert
    assert "Document 1:\nThe sky is blue." in prompt
    assert "Document 2:\nIt can also be gray." in prompt
    assert "Query: What color is the sky?" in prompt
    assert prompt.endswith("Answer:")
