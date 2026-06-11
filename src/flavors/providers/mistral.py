"""Mistral provider adapter (used by orchestrator and compyler by default)."""

import os

from mistralai.client import Mistral

from .base import ProviderAdapter, ProviderResponse


class MistralAdapter(ProviderAdapter):
    DEFAULT_MODEL = "open-mistral-7b"

    def __init__(self, model: str | None = None):
        self._model = model or os.getenv("MISTRAL_MODEL", self.DEFAULT_MODEL)
        self._client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    @property
    def name(self) -> str:
        return "mistral"

    def generate(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> ProviderResponse:
        full_messages = [{"role": "system", "content": system}] + messages
        resp = self._client.chat.complete(
            model=self._model,
            messages=full_messages,
        )
        return ProviderResponse(
            text=resp.choices[0].message.content.strip(),
            model=self._model,
            provider=self.name,
        )
