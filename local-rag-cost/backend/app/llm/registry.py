from .anthropic import AnthropicProvider
from .ollama import OllamaProvider
from .openai import StubProvider as OpenAIProvider
from .google import StubProvider as GoogleProvider
from .llamacpp import StubProvider as LlamaCppProvider


def get_provider(name: str):
    providers = {
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
        "google": GoogleProvider,
        "llamacpp": LlamaCppProvider,
    }
    if name not in providers:
        raise ValueError(f"Unknown provider: {name}")
    return providers[name]()


def list_providers() -> list[str]:
    return ["anthropic", "ollama", "openai", "google", "llamacpp"]
