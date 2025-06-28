from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Build a robust path to the .env file, assuming it's in the `agentic_rag` root
# This makes the settings loading independent of the current working directory.
# settings.py -> config -> app -> agentic_rag -> .env
env_path = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    # FastAPI
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Axiom8"
    debug: bool = Field(default=False)

    # Anthropic (Required)
    anthropic_api_key: str = Field(..., description="Anthropic API key.")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20240620", description="Claude model to use."
    )

    # LangSmith Observability
    langchain_tracing_v2: bool = Field(
        default=True, description="Enable LangSmith tracing."
    )
    langchain_api_key: str = Field(..., description="LangSmith API key.")
    langchain_project: str = Field(
        default="Axiom8", description="LangSmith project name."
    )

    # n8n RAG Tool Webhook URLs
    n8n_core_rag_url: AnyHttpUrl = Field(
        ..., description="Webhook URL for n8n Core RAG tool."
    )
    n8n_management_rag_url: AnyHttpUrl = Field(
        ..., description="Webhook URL for n8n Management RAG tool."
    )
    n8n_integrations_rag_url: AnyHttpUrl = Field(
        ..., description="Webhook URL for n8n Integrations RAG tool."
    )
    n8n_workflows_rag_url: AnyHttpUrl = Field(
        ..., description="Webhook URL for n8n Workflows RAG tool."
    )

    # Session / caching
    redis_url: Optional[AnyHttpUrl] = Field(
        default=None, description="Redis URL for session caching."
    )

    model_config = SettingsConfigDict(
        env_file=env_path, env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
