from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define the absolute path to the .env file based on the project root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    app_name: str = "Backend Multi-Agent"

    # Use SecretStr to hide sensitive data in logs
    database_url: SecretStr = SecretStr("postgresql+psycopg2://user:password@db:5432/agents_db")

    llm_base_url: str = "http://localhost:1234/v1"
    llm_api_key: SecretStr = SecretStr("lm-studio")
    llm_model_name: str = "qwen3-4b-2507"

    # Load env file from the absolute path, ignoring extra variables (like Postgres vars)
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()