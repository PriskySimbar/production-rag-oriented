from io import BytesIO

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Document, DocumentChunk
from app.services.embedding import generate_embeddings


def chunk_text(
    text: str,
) -> list[str]:

    chunks = []

    start = 0

    while start < len(text):

        end = start + settings.chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += (
            settings.chunk_size
            - settings.chunk_overlap
        )

    return chunks


def ingest_pdf(
    file_bytes: bytes,
    filename: str,
    db: Session,
):
    reader = PdfReader(
        BytesIO(file_bytes)
    )

    document = Document(
        filename=filename
    )

    db.add(document)
    db.flush()

    all_chunks = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):

        text = page.extract_text()

        if not text:
            continue

        chunks = chunk_text(text)

        for chunk_index, chunk in enumerate(chunks):

            all_chunks.append({
                "content": chunk,
                "page_number": page_number,
                "chunk_index": len(all_chunks),
            })

    # =========================
    # Generate embeddings
    # =========================

    texts = [
        chunk["content"]
        for chunk in all_chunks
    ]

    embeddings = generate_embeddings(
        texts
    )

    # =========================
    # Store chunks
    # =========================

    for chunk, embedding in zip(
        all_chunks,
        embeddings,
    ):

        db.add(
            DocumentChunk(
                document_id=document.id,
                content=chunk["content"],
                page_number=chunk["page_number"],
                chunk_index=chunk["chunk_index"],
                embedding=embedding,
            )
        )

    db.commit()

    db.refresh(document)

    return document