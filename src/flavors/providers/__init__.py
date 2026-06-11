"""Provider adapter registry and factory."""

from .base import ProviderAdapter, ProviderResponse
from .claude import ClaudeAdapter
from .gemini import GeminiAdapter
from .mistral import MistralAdapter
from .openai import OpenAIAdapter
from .xai import XAIAdapter

_REGISTRY: dict[str, type[ProviderAdapter]] = {
    "claude": ClaudeAdapter,
    "mistral": MistralAdapter,
    "openai": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "xai": XAIAdapter,
}


def get_adapter(provider: str, **kwargs: object) -> ProviderAdapter:
    """
    Instantiate a provider adapter by name.

    Args:
        provider: One of 'claude', 'mistral', 'openai', 'gemini', 'xai'.
        **kwargs: Forwarded to the adapter constructor (e.g. model='gpt-4o').

    Raises:
        ValueError: If the provider name is not registered.
    """
    if provider not in _REGISTRY:
        raise ValueError(
            f"Unknown provider '{provider}'. Available: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[provider](**kwargs)


__all__ = [
    "ProviderAdapter",
    "ProviderResponse",
    "get_adapter",
    "ClaudeAdapter",
    "MistralAdapter",
    "OpenAIAdapter",
    "GeminiAdapter",
    "XAIAdapter",
]
