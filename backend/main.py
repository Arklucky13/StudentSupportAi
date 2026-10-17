
from fastapi import FastAPI

app = FastAPI(
    title="Student Support RAG API",
    description="Backend for a student support assistant",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "Student Support RAG API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "student-support-rag"
    }
