from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Conversation, Message
from app.services.rag import (
    create_conversation,
    stream_rag_answer,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


class MessageRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=4000,
    )


@router.post("")
def create_new_conversation(
    db: Session = Depends(get_db),
):

    conversation = create_conversation(
        db
    )

    return {
        "id": conversation.id
    }


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):

    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id
            == conversation_id
        )
        .order_by(Message.created_at)
    ).all()

    return {
        "id": conversation.id,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


@router.post(
    "/{conversation_id}/messages"
)
def send_message(
    conversation_id: str,
    request: MessageRequest,
    db: Session = Depends(get_db),
):

    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )

    db.add(user_message)

    db.commit()

    return StreamingResponse(
        stream_rag_answer(
            question=request.message,
            conversation_id=conversation_id,
            db=db,
        ),
        media_type="text/plain",
    )