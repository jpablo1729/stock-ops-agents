from ddgs import DDGS
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.config import settings

# Initialize the LLM model using configuration from settings.
# We use get_secret_value() in case the API key is defined as SecretStr in config.
model = OpenAIChatModel(
    settings.llm_model_name,
    provider=OpenAIProvider(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key.get_secret_value() if hasattr(settings.llm_api_key,
                                                                   'get_secret_value') else settings.llm_api_key,
    ),
)

# Define the Researcher Agent
researcher_agent = Agent(
    model,
    system_prompt=(
        "You are a market intelligence analyst. "
        "Your only job is to search for current prices on the internet using your search tool "
        "and return a brief, objective summary with the found prices and the stores or sources."
    ),
)

@researcher_agent.tool_plain
def search_web_prices(query: str) -> list[dict]:
    """Searches the internet for current prices and offers for a given product name or model."""
    try:
        with DDGS() as ddgs:
            # Fetch top 5 results from DuckDuckGo
            results = list(ddgs.text(query, max_results=5))

        return [
            {
                "title": r.get("title", ""),
                "summary": r.get("body", ""),
                "url": r.get("href", ""),
            }
            for r in results
        ]
    except Exception as exc:
        return [{"error": f"Could not complete web search: {str(exc)}"}]