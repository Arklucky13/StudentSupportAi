
from pathlib import Path
import sys

# --------------------------------------------------
# 1. Configure project paths
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

DOCUMENTS_DIR = ROOT_DIR / "sample_docs"

# --------------------------------------------------
# 2. Import required libraries
# --------------------------------------------------

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from backend.db.client import supabase

# --------------------------------------------------
# 3. Configuration
# --------------------------------------------------

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 180
CHUNK_OVERLAP = 30
BATCH_SIZE = 32

ALLOWED_CATEGORIES = {
    "academics",
    "career",
    "study",
}

ALLOWED_EXTENSIONS = {".txt", ".pdf"}


# --------------------------------------------------
# 4. Extract text from TXT and PDF files
# --------------------------------------------------

def extract_text(file_path: Path) -> str:
    """Extract text from a TXT or PDF document."""

    extension = file_path.suffix.lower()

    if extension == ".txt":
        return file_path.read_text(encoding="utf-8")

    if extension == ".pdf":
        reader = PdfReader(str(file_path))
        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )


# --------------------------------------------------
# 5. Split text into overlapping chunks
# --------------------------------------------------

def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into word-based chunks with overlap."""

    words = text.split()

    if not words:
        return []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller "
            "than chunk size."
        )

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if start + chunk_size >= len(words):
            break

    return chunks


# --------------------------------------------------
# 6. Process and upload one document
# --------------------------------------------------

def ingest_file(
    file_path: Path,
    model: SentenceTransformer,
) -> int:
    """Extract, chunk, embed, and store one document."""

    relative_path = file_path.relative_to(
        DOCUMENTS_DIR
    ).as_posix()

    category = file_path.parent.name.lower()

    # Determine whether the folder is an allowed category.
    if category not in ALLOWED_CATEGORIES:
        print(
            f"Skipping unknown category: {relative_path}"
        )
        return 0

    # Extract document text.
    try:
        text = extract_text(file_path).strip()
    except Exception as error:
        print(
            f"Could not read {relative_path}: {error}"
        )
        return 0

    if not text:
        print(f"No text found: {relative_path}")
        return 0

    # Create chunks.
    chunks = split_into_chunks(text)

    if not chunks:
        print(f"No chunks created: {relative_path}")
        return 0

    print(f"\nProcessing: {relative_path}")
    print(f"Category: {category}")
    print(f"Chunks created: {len(chunks)}")

    # Generate embeddings.
    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()

    # Prepare all database rows before uploading.
    rows = []

    for index, chunk in enumerate(chunks):
        rows.append(
            {
                "document_name": relative_path,
                "category": category,
                "chunk_index": index,
                "content": chunk,
                "embedding": embeddings[index],
            }
        )

    # Remove the previous version of this document.
    # This allows the document to be re-indexed.
    try:
        (
            supabase.table("document_chunks")
            .delete()
            .eq("document_name", relative_path)
            .eq("category", category)
            .execute()
        )

        # Upload rows in batches.
        for start in range(0, len(rows), BATCH_SIZE):
            batch = rows[start:start + BATCH_SIZE]

            (
                supabase.table("document_chunks")
                .insert(batch)
                .execute()
            )

    except Exception as error:
        print(
            f"Supabase upload failed for "
            f"{relative_path}: {error}"
        )
        raise

    print(f"Successfully indexed: {relative_path}")

    return len(chunks)


# --------------------------------------------------
# 7. Main ingestion workflow
# --------------------------------------------------

def main():
    """Find documents and index them in Supabase."""

    print("=" * 50)
    print("STUDENT SUPPORT DOCUMENT INGESTION")
    print("=" * 50)

    # Verify the documents directory exists.
    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(
            f"Documents folder not found: {DOCUMENTS_DIR}"
        )

    # Discover PDF and TXT files recursively.
    files = sorted(
        path
        for path in DOCUMENTS_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in ALLOWED_EXTENSIONS
    )

    if not files:
        print("No PDF or TXT documents found.")
        print(f"Check this folder: {DOCUMENTS_DIR}")
        return

    print(f"Documents discovered: {len(files)}")

    # Load the embedding model once.
    print("\nLoading embedding model...")
    print(f"Model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded successfully.")

    total_chunks = 0
    successful_files = 0

    # Process each discovered document.
    for file_path in files:
        try:
            chunks_indexed = ingest_file(
                file_path,
                model,
            )

            total_chunks += chunks_indexed

            if chunks_indexed > 0:
                successful_files += 1

        except Exception as error:
            print(
                f"Failed to process {file_path.name}: "
                f"{error}"
            )

    # Print final summary.
    print("\n" + "=" * 50)
    print("DOCUMENT INGESTION FINISHED")
    print("=" * 50)
    print(f"Files discovered: {len(files)}")
    print(f"Files indexed: {successful_files}")
    print(f"Chunks indexed: {total_chunks}")
    print("=" * 50)


# --------------------------------------------------
# 8. Entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()
