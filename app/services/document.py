from io import BytesIO

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk
from app.services.embedding import generate_embedding


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def process_pdf(
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

    for page_index, page in enumerate(
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

            document_chunk = DocumentChunk(
                document_id=document.id,
                content=chunk,
                page_number=page_index,
                chunk_index=global_chunk_index,
                embedding=embedding,
            )

            db.add(document_chunk)

            global_chunk_index += 1

    db.commit()

    return document