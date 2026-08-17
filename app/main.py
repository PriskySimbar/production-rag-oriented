import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)


app = FastAPI(
    title="Production RAG AI Assistant",
    version="1.0.0",
    description=(
        "Production-oriented RAG AI Assistant "
        "using FastAPI, PostgreSQL/pgvector, "
        "Sentence Transformers and Gemini."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    documents_router
)

app.include_router(
    chat_router
)


@app.get("/health")
def health():

    return {
        "status": "ok"
    }