
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from backend.db.client import supabase

# Load environment variables from the project root.
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from the environment.")

client = genai.Client(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768


def embed_question(question: str) -> list[float]:
    """Convert a user's question into a Gemini embedding."""

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config={
            "output_dimensionality": EMBEDDING_DIMENSIONS,
            "task_type": "RETRIEVAL_QUERY",
        },
    )

    if not response.embeddings:
        raise RuntimeError("Gemini returned no query embedding.")

    embedding = response.embeddings[0].values

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"received {len(embedding)}."
        )

    return embedding


def retrieve_chunks(question: str, match_count: int = 5) -> list[dict]:
    """Retrieve the most relevant document chunks from Supabase."""

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if not 1 <= match_count <= 10:
        raise ValueError("match_count must be between 1 and 10.")

    question_embedding = embed_question(question)

    response = supabase.rpc(
        "match_document_chunks_gemini",
        {
            "query_embedding": question_embedding,
            "match_count": match_count,
        },
    ).execute()

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
