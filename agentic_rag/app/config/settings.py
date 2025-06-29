from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Build a robust path to the .env file, assuming it's in the `agentic_rag` root
env_path = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    # FastAPI
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Axiom8 - n8n RAG Agent"
    debug: bool = False

    # Anthropic (Required)
    anthropic_api_key: SecretStr = Field(...)
    anthropic_model: str = "claude-3-5-sonnet-20240620"
    
    # OpenAI (Required for o3-mini model)
    openai_api_key: SecretStr = Field(...)
    openai_model: str = "o3-mini"

    # LangSmith Observability
    langchain_tracing_v2: str = Field(default="false")
    langchain_project: Optional[str] = Field(default=None)
    langchain_api_key: Optional[SecretStr] = Field(default=None)

    # n8n Webhook URLs for RAG tools
    n8n_workflow_search_url: str = Field(...)
    n8n_documentation_search_url: str = Field(...)
    n8n_nodes_search_url: str = Field(...)
    n8n_workflows_search_url: str = Field(...)

    model_config = SettingsConfigDict(
        env_file=env_path, env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    # The following line may show a false-positive error in some linters.
    # This is because the linter performs static analysis and doesn't know that
    # Pydantic will load the required fields from the .env file at runtime.
    # We can safely ignore this warning.
    return Settings()  # type: ignore
