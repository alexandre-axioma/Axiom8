from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from ..config.settings import get_settings
from .prompts import WORKFLOW_GENERATOR_PROMPT
from .tools import all_tools

settings = get_settings()

# 1. Explicitly create the provider with the API key from settings.
# We must call .get_secret_value() to access the string inside the SecretStr object.
provider = AnthropicProvider(api_key=settings.anthropic_api_key.get_secret_value())

# 2. Define the model, passing the name and the configured provider.
model = AnthropicModel(
    "claude-3-5-sonnet-20240620",
    provider=provider,
)

# 3. Initialize the agent with the fully configured model instance.
workflow_generator_agent = Agent(
    model=model,
    system_prompt=str(WORKFLOW_GENERATOR_PROMPT.content),
    tools=all_tools,
    output_type=str,
)   