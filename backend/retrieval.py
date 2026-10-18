
from sentence_transformers import SentenceTransformer
from backend.db.client import supabase

# Use the same embedding model used during ingestion.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load the model once when this module is imported.
embedding_model = SentenceTransformer(MODEL_NAME)


def retrieve_chunks(
    question: str,
    match_count: int = 5,
) -> list[dict]:
    """
    Convert a question into an embedding and retrieve
    the most similar document chunks from Supabase.
    """

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    # Generate a 384-dimensional embedding for the question.
    question_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    # Call the PostgreSQL vector-search function.
    response = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": question_embedding,
            "match_count": match_count,
        },
    ).execute()

    # Return the retrieved chunks.
    results = response.data or []

    return [
        {
            "document_name": item["document_name"],
            "category": item["category"],
            "chunk_index": item["chunk_index"],
            "content": item["content"],
            "similarity": item["similarity"],
        }
        for item in results
    ]
