from io import BytesIO

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Document, DocumentChunk
from app.services.embedding import generate_embedding


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

    global_chunk_index = 0

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):

        text = page.extract_text()

        if not text:
            continue

        chunks = chunk_text(text)

        for chunk in chunks:

            embedding = generate_embedding(
                chunk
            )

            db.add(
                DocumentChunk(
                    document_id=document.id,
                    content=chunk,
                    page_number=page_number,
                    chunk_index=global_chunk_index,
                    embedding=embedding,
                )
            )

            global_chunk_index += 1

    db.commit()

    db.refresh(document)

    return document