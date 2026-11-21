from sqlalchemy.orm import Session
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from app.database import ChatSession

class HistoryService:
    @staticmethod
    def load_history(db: Session, session_id: str) -> list[ModelMessage]:
        """Loads the chat history for a given session from the database."""
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

        # If no session exists or there are no messages, return an empty list
        if not session or not session.messages_json:
            return []

        # Deserialize the JSON string back into Pydantic AI message objects
        return ModelMessagesTypeAdapter.validate_json(session.messages_json)

    @staticmethod
    def save_history(db: Session, session_id: str, user_id: str, messages_json_bytes: bytes) -> None:
        """Saves or updates the chat history for a session."""
        # Convert the Pydantic AI serialized bytes into a UTF-8 string for the database
        json_str = messages_json_bytes.decode("utf-8")

        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

        if session:
            # Update existing session
            session.messages_json = json_str
        else:
            # Create a new session if it doesn't exist
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                messages_json=json_str,
            )
            db.add(session)

        # Commit the transaction to the database
        db.commit()