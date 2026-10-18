
from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
from backend.db.client import supabase

# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "sample_docs"

load_dotenv(ROOT_DIR / ".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from the root .env file.")

client = genai.Client(api_key=api_key)

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHUNK_WORDS = 180
OVERLAP_WORDS = 30
BATCH_SIZE = 50

ALLOWED_CATEGORIES = {"academics", "career", "study"}


# --------------------------------------------------
# Read TXT and PDF documents
# --------------------------------------------------

def read_document(file_path: Path) -> str:
    if file_path.suffix.lower() == ".txt":
        return file_path.read_text(encoding="utf-8", errors="replace")

    if file_path.suffix.lower() == ".pdf":
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    return ""


# --------------------------------------------------
# Split text into overlapping chunks
# --------------------------------------------------

def chunk_text(
    text: str,
    chunk_words: int = CHUNK_WORDS,
    overlap_words: int = OVERLAP_WORDS,
) -> list[str]:
    words = text.split()

    if not words:
        return []

    if overlap_words >= chunk_words:
        raise ValueError("OVERLAP_WORDS must be smaller than CHUNK_WORDS.")

    chunks = []
    step = chunk_words - overlap_words

    for start in range(0, len(words), step):
        chunk = " ".join(words[start:start + chunk_words])
        if chunk:
            chunks.append(chunk)

    return chunks


# --------------------------------------------------
# Generate Gemini embeddings
# --------------------------------------------------

def generate_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={
            "output_dimensionality": EMBEDDING_DIMENSIONS,
            "task_type": "RETRIEVAL_DOCUMENT",
        },
    )

    if not response.embeddings:
        raise RuntimeError("Gemini returned no embedding.")

    embedding = response.embeddings[0].values

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"received {len(embedding)}."
        )

    return embedding


# --------------------------------------------------
# Discover documents and ingest chunks
# --------------------------------------------------

def main():
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Documents folder not found: {DOCS_DIR}")

    document_paths = sorted(
        path
        for path in DOCS_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in {".txt", ".pdf"}
    )

    if not document_paths:
        print(f"No TXT/PDF documents found in {DOCS_DIR}")
        return

    total_chunks = 0

    for file_path in document_paths:
        relative_path = file_path.relative_to(DOCS_DIR)
        parts = relative_path.parts

        if len(parts) < 2 or parts[0].lower() not in ALLOWED_CATEGORIES:
            print(f"Skipping document outside category folders: {relative_path}")
            continue

        category = parts[0].lower()
        document_name = relative_path.as_posix()

        print(f"\nProcessing: {document_name}")

        text = read_document(file_path).strip()
        chunks = chunk_text(text)

        if not chunks:
            print("  Skipping: no extractable text.")
            continue

        # Generate all embeddings before replacing stored data.
        # This preserves existing chunks if embedding generation fails.
        rows = []

        for index, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)

            rows.append(
                {
                    "document_name": document_name,
                    "category": category,
                    "chunk_index": index,
                    "content": chunk,
                    "embedding": embedding,
                }
            )

            print(f"  Embedded chunk {index + 1}/{len(chunks)}")

        # Delete only this document from the new table.
        supabase.table("document_chunks_gemini").delete().eq(
            "document_name", document_name
        ).eq("category", category).execute()

        # Upload in batches.
        for start in range(0, len(rows), BATCH_SIZE):
            batch = rows[start:start + BATCH_SIZE]

            supabase.table("document_chunks_gemini").insert(
                batch
            ).execute()

        total_chunks += len(rows)
        print(f"  Stored {len(rows)} chunks.")

    print(f"\nIngestion complete. Total chunks processed: {total_chunks}")


if __name__ == "__main__":
    main()
