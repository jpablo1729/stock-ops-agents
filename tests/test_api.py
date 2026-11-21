from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

# Initialize the app for testing
client = TestClient(app)

def test_read_products():
    """Test that the products endpoint returns a list of products."""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Since we seeded 100 products, the list shouldn't be empty
    assert len(response.json()) > 0

def test_chat_endpoint():
    """Test that the chat endpoint returns a valid response."""
    payload = {
        "session_id": "test-session-001",
        "user_id": "test-user",
        "message": "Hello, how are you?"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session-001"
    assert "reply" in data
    assert isinstance(data["reply"], str)