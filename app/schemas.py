from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(..., examples=["session-001"])
    user_id: str = Field(..., examples=["mando"])
    message: str = Field(
        ...,
        examples=["Compare the price of our ESP32-S3 DevKit Module (SKU-104) with online stores."]
    )

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    total_messages_in_history: int

class ProductOut(BaseModel):
    sku: str
    name: str
    category: str
    price: float
    stock: int

    # Allows Pydantic to read data directly from SQLAlchemy models
    model_config = {"from_attributes": True}