import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db, ChatSession
from app.schemas import ChatRequest, ChatResponse, ProductOut
from app.services.inventory import InventoryService
from app.services.history import HistoryService
from app.agents.support_agent import support_agent, AgentDeps

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed data when the app starts
    init_db()
    yield
    # (Optional) Cleanup tasks on shutdown could go here

app = FastAPI(title=settings.app_name, lifespan=lifespan)

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_agent(payload: ChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. Load previous chat history for this session
        previous_history = HistoryService.load_history(db, payload.session_id)

        # 2. Create dependencies (DB session and user ID) for the agent
        deps = AgentDeps(db=db, user_id=payload.user_id)

        # 3. Run the agent with the new message and previous context
        result = await support_agent.run(
            payload.message,
            deps=deps,
            message_history=previous_history,
        )

        # 4. Save the updated history back to the database
        HistoryService.save_history(
            db=db,
            session_id=payload.session_id,
            user_id=payload.user_id,
            messages_json_bytes=result.all_messages_json(),
        )

        # 5. Return the response to the user
        return ChatResponse(
            session_id=payload.session_id,
            reply=result.output,
            total_messages_in_history=len(result.all_messages()),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(exc)}")

@app.get("/api/v1/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    """Retrieve all products from the inventory."""
    return InventoryService.get_all(db)

@app.get("/api/v1/history/{session_id}")
def view_history_trace(session_id: str, db: Session = Depends(get_db)):
    """Audit endpoint to inspect in Postman every tool call and reasoning step."""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "trace": json.loads(session.messages_json),
    }