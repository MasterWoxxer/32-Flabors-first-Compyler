"""Abstract base class for all model provider adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderResponse:
    """Normalized response returned by every adapter."""

    text: str
    model: str
    provider: str
    # Extended-thinking / reasoning trace, when the provider exposes one
    # (currently the Claude adapter). None for providers without it.
    thinking: str | None = None


class ProviderAdapter(ABC):
    """
    Minimal interface all provider adapters must implement.

    Swap providers by changing the executor_provider / orchestrator_provider /
    compyler_provider fields in PipelineConfig — no pipeline logic changes needed.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable identifier: 'claude' | 'openai' | 'gemini' | 'xai' | 'mistral'."""

    @abstractmethod
    def generate(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
        thinking: bool = False,
    ) -> ProviderResponse:
        """
        Call the provider and return a normalized ProviderResponse.

        Args:
            system:    System-prompt string.
            messages:  List of {"role": "user"|"assistant", "content": str} dicts.
            max_tokens: Upper bound on response tokens.
            thinking:  Request a visible reasoning trace where the provider
                supports it (currently Claude's adaptive thinking; Mistral's
                Magistral models emit one regardless). Adapters without the
                capability accept and ignore it.
        """
