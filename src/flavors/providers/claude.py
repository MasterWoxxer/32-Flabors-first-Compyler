"""Anthropic Claude provider adapter."""

import os

import anthropic

from .base import ProviderAdapter, ProviderResponse


class ClaudeAdapter(ProviderAdapter):
    DEFAULT_MODEL = "claude-opus-4-5"

    def __init__(self, model: str | None = None):
        self._model = model or os.getenv("CLAUDE_MODEL", self.DEFAULT_MODEL)
        self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    @property
    def name(self) -> str:
        return "claude"

    def generate(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> ProviderResponse:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return ProviderResponse(
            text=resp.content[0].text,
            model=self._model,
            provider=self.name,
        )
