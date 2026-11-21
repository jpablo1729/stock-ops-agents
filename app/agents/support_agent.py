from dataclasses import dataclass
from sqlalchemy.orm import Session
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.config import settings
from app.services.inventory import InventoryService
from app.agents.researcher_agent import researcher_agent

@dataclass
class AgentDeps:
    db: Session
    user_id: str

model = OpenAIChatModel(
    settings.llm_model_name,
    provider=OpenAIProvider(
        base_url=settings.llm_base_url,
        # Ensure we handle SecretStr from config
        api_key=settings.llm_api_key.get_secret_value() if hasattr(settings.llm_api_key, 'get_secret_value') else settings.llm_api_key,
    ),
)

support_agent = Agent(
    model,
    deps_type=AgentDeps,
    system_prompt=(
        "You are a technical operations and inventory assistant. "
        "Strict rules:\n"
        "1. Never invent prices, SKU codes, or stock quantities.\n"
        "2. Use your inventory tools to query or modify the internal database.\n"
        "3. If the user asks to compare prices with the market or internet, first check your internal price "
        "and then delegate the external search using 'check_market_price'.\n"
        "4. Respond directly, professionally, and in the language of the user."
    ),
)

@support_agent.tool
def list_catalog(ctx: RunContext[AgentDeps]) -> list[dict]:
    """Returns the complete list of available products in the inventory with their SKU, name, price, and stock."""
    products = InventoryService.get_all(ctx.deps.db)
    return [
        {
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "stock": p.stock,
        }
        for p in products
    ]

@support_agent.tool
def get_product_by_sku(ctx: RunContext[AgentDeps], sku: str) -> dict:
    """Finds the details and exact availability of a product using its SKU code (e.g., SKU-101)."""
    product = InventoryService.get_by_sku(ctx.deps.db, sku)
    if not product:
        return {"error": f"Product with SKU '{sku}' not found."}
    return {
        "sku": product.sku,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "stock": product.stock,
    }

@support_agent.tool
def reserve_stock(ctx: RunContext[AgentDeps], sku: str, quantity: int) -> dict:
    """Deducts or reserves a specific quantity of units for a product given its SKU."""
    success, message = InventoryService.reserve_stock(ctx.deps.db, sku, quantity)
    return {"success": success, "detail": message, "requested_by": ctx.deps.user_id}

@support_agent.tool
async def check_market_price(ctx: RunContext[AgentDeps], product_name: str) -> str:
    """Delegates to the researcher agent the internet search for the current market price of a product."""
    result = await researcher_agent.run(
        f"Search the internet for the current selling price of: {product_name}",
        usage=ctx.usage,
    )
    return result.output