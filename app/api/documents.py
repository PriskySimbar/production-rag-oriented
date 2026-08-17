from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document
from app.services.ingestion import ingest_pdf


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="File is empty.",
        )

    document = ingest_pdf(
        file_bytes=file_bytes,
        filename=file.filename,
        db=db,
    )

    return {
        "id": document.id,
        "filename": document.filename,
        "message": "Document uploaded successfully.",
    }


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
):

    documents = db.scalars(
        select(Document)
        .order_by(
            Document.created_at.desc()
        )
    ).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
):

    document = db.get(
        Document,
        document_id,
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully."
    }