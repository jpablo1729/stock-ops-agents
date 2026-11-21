🤖 Multi-Agent Inventory System

A production-ready backend that uses Agentic AI to manage an inventory database. The system features a Supervisor/Worker architecture where a Support Agent queries a local PostgreSQL database and delegates web searches to a Researcher Agent.

🚀 Features

. Multi-Agent Architecture: Built with pydantic-ai, featuring a Support Agent (database queries) and a Researcher Agent (web search via DuckDuckGo).

. LLM Agnostic: Connects seamlessly to local LLMs via LM Studio (OpenAI-compatible API).

. Persistent Memory: Chat histories are serialized and stored in PostgreSQL using SQLAlchemy.

. Dockerized: Fully containerized environment with FastAPI, PostgreSQL, and Docker Compose.

. Well-Tested: Includes Pytest API tests and HTTP request files for manual testing.

🛠️ Tech Stack

. Framework: FastAPI
. AI Framework: Pydantic-AI
. Database: PostgreSQL + SQLAlchemy
. LLM: LM Studio (Qwen 3-4B)
. Testing: Pytest, HTTPX
. Deployment: Docker & Docker Compose

🏗️ Architecture Diagram

![Architecture Diagram](https://raw.githubusercontent.com/jpablo1729/stock-ops-agents/blob/main/arch.png)

🚦 Getting Started

I. Prerequisites
. 
. Docker & Docker Compose installed.
. LM Studio running locally with a model loaded (e.g., Qwen) and the local server started on port 1234.

II. Installation

. Clone the repository: git clone https://github.com/your-username/stock-ops-agents.git
. cd stock-ops-agents

. Copy the environment variables: cp .env.example .env

. Start the containers: docker compose up --build (The database will automatically seed with 100 random products on the first run).

III. API Usage

. Swagger UI: Access the interactive docs at http://localhost:8000/docs.
. Chat Endpoint: Send a POST request to /api/v1/chat with the following JSON body:

{
  "session_id": "session-001",
  "user_id": "mando",
  "message": "Compare the price of our SKU-001 with the market."
}

🧪 Running Tests

To run the test suite inside the Docker container without starting the whole stack: docker compose run --rm api pytest
