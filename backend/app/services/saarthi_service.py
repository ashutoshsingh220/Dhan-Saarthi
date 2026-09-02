import uuid
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSession
from app.models.user import User
from app.providers.gemini_client import GeminiClient
from app.schemas.chat import ChatMessageDetail, ChatMessageResponse, ChatSessionSummary
from app.services.context_builder import ContextBuilder


class SaarthiService:
    def __init__(self, gemini_client: GeminiClient | None = None):
        self.gemini_client = gemini_client or GeminiClient()

    def process_message(
        self, db: Session, user: User, message_text: str, session_uuid: str | None = None
    ) -> ChatMessageResponse:
        clean_text = message_text.strip()
        if not clean_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message content cannot be empty")

        if session_uuid:
            session = db.scalar(
                select(ChatSession).where(ChatSession.session_uuid == session_uuid)
            )
            if session is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
            if session.user_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this chat session is denied")
        else:
            title_text = clean_text[:40] + ("..." if len(clean_text) > 40 else "")
            session = ChatSession(user_id=user.id, title=title_text)
            db.add(session)
            db.flush()  # assign session.id & session_uuid

        # Fetch last 8 messages for context window
        recent_messages = db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(8)
        ).all()

        # Reverse to chronological order
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(recent_messages)
        ]

        # Build context
        system_instruction = ContextBuilder.get_system_instruction()
        user_context = ContextBuilder.build_user_context(user, db=db)


        # Call Gemini AI Provider
        ai_response = self.gemini_client.generate_response(
            system_instruction=system_instruction,
            user_context=user_context,
            history=history,
            user_message=clean_text,
        )

        # Persist user message and model response
        user_msg = ChatMessage(session_id=session.id, role="user", content=clean_text)
        model_msg = ChatMessage(session_id=session.id, role="model", content=ai_response)

        db.add(user_msg)
        db.add(model_msg)
        session.updated_at = datetime.now()

        db.commit()
        db.refresh(model_msg)

        return ChatMessageResponse(
            session_id=session.session_uuid,
            message_id=model_msg.id,
            response=ai_response,
            created_at=model_msg.created_at,
        )

    def process_message_stream(
        self, db: Session, user: User, message_text: str, session_uuid: str | None = None
    ):
        """
        Prepares context synchronously and yields streaming response chunks.
        Persists final response safely into DB at end of stream.
        """
        clean_text = message_text.strip()
        if not clean_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message content cannot be empty")

        if session_uuid:
            session = db.scalar(
                select(ChatSession).where(ChatSession.session_uuid == session_uuid)
            )
            if session is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
            if session.user_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this chat session is denied")
        else:
            title_text = clean_text[:40] + ("..." if len(clean_text) > 40 else "")
            session = ChatSession(user_id=user.id, title=title_text)
            db.add(session)
            db.flush()

        recent_messages = db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(8)
        ).all()

        history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(recent_messages)
        ]

        system_instruction = ContextBuilder.get_system_instruction()
        user_context = ContextBuilder.build_user_context(user, db=db)

        user_msg = ChatMessage(session_id=session.id, role="user", content=clean_text)
        db.add(user_msg)
        db.commit()

        session_db_id = session.id

        def stream_generator():
            accumulated_chunks = []
            for chunk in self.gemini_client.generate_response_stream(
                system_instruction=system_instruction,
                user_context=user_context,
                history=history,
                user_message=clean_text,
            ):
                accumulated_chunks.append(chunk)
                yield chunk

            full_ai_response = "".join(accumulated_chunks).strip()
            if not full_ai_response:
                full_ai_response = "Saarthi received an empty response. Please try asking your question again."

            try:
                model_msg = ChatMessage(session_id=session_db_id, role="model", content=full_ai_response)
                db.add(model_msg)
                db.commit()
            except Exception:
                db.rollback()

        return stream_generator()




    def get_user_sessions(self, db: Session, user: User, limit: int = 20, offset: int = 0) -> list[ChatSessionSummary]:
        sessions = db.scalars(
            select(ChatSession)
            .where(ChatSession.user_id == user.id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
        return [
            ChatSessionSummary(
                session_id=s.session_uuid,
                title=s.title,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]

    def get_session_messages(self, db: Session, user: User, session_uuid: str, limit: int = 50, offset: int = 0) -> list[ChatMessageDetail]:
        session = db.scalar(
            select(ChatSession).where(ChatSession.session_uuid == session_uuid)
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
        if session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this chat session is denied")

        messages = db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .offset(offset)
        ).all()

        return [
            ChatMessageDetail(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ]
