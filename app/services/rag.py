from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import (
    Conversation,
    Document,
    DocumentChunk,
    Message,
)
from app.services.embedding import generate_embeddings
from app.services.llm import stream_generate


def retrieve_candidates(
    question: str,
    db: Session,
):
    query_embedding = generate_embeddings([question])[0]

    distance = (
        DocumentChunk.embedding.cosine_distance(
            query_embedding
        )
    )

    statement = (
        select(
            DocumentChunk,
            Document.filename,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .order_by(distance)
        .limit(settings.top_k_retrieval)
    )

    rows = db.execute(statement).all()

    candidates = []

    for chunk, filename, distance in rows:
        candidates.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "filename": filename,
                "content": chunk.content,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "vector_distance": float(distance),
            }
        )

    return candidates


def get_history(
    conversation_id: str,
    db: Session,
):
    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at)
    ).all()

    return messages[-10:]


def build_prompt(
    question: str,
    history: list,
    chunks: list,
):
    history_text = "\n".join(
        f"{message.role}: {message.content}"
        for message in history
    )

    context_parts = []

    for i, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"""
[Document {i}]
Source: {chunk["filename"]}
Page: {chunk["page_number"]}
Chunk: {chunk["chunk_index"]}

{chunk["content"]}
"""
        )

    context = "\n".join(context_parts)

    return f"""
You are a document-grounded AI assistant.

Your job is to answer the user's question
using the provided document context.

STRICT RULES:

1. Use the documents as the primary source.
2. Do not invent facts.
3. If the documents do not contain enough
   information, say so clearly.
4. Do not pretend that unrelated documents
   are relevant.
5. Give a concise but useful answer.
6. When possible, mention the relevant source
   and page.

Conversation history:
--------------------
{history_text}
--------------------

Retrieved documents:
--------------------
{context}
--------------------

Current question:
--------------------
{question}
--------------------
"""


def stream_rag_answer(
    question: str,
    conversation_id: str,
    db: Session,
):
    candidates = retrieve_candidates(
        question,
        db,
    )

    # Hasil sudah diurutkan berdasarkan cosine distance dari pgvector.
    ranked_chunks = candidates[: settings.top_k_final]

    history = get_history(
        conversation_id,
        db,
    )

    prompt = build_prompt(
        question=question,
        history=history,
        chunks=ranked_chunks,
    )

    full_response = ""

    try:
        for token in stream_generate(prompt):
            full_response += token
            yield token

    except Exception:
        db.rollback()
        raise

    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=full_response,
    )

    db.add(assistant_message)
    db.commit()


def create_conversation(
    db: Session,
):
    conversation = Conversation()

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation