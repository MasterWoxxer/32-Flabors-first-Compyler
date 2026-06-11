"""OpenAI provider adapter.

Install the `openai` package and set OPENAI_API_KEY to enable.
Swap in by setting EXECUTOR_PROVIDER=openai or via the model toggle in the UI.
"""

import os

from .base import ProviderAdapter, ProviderResponse


class OpenAIAdapter(ProviderAdapter):
    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, model: str | None = None):
        self._model = model or os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)

    @property
    def name(self) -> str:
        return "openai"

    def generate(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> ProviderResponse:
        try:
            import openai  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "Install the `openai` package to use the OpenAI adapter: pip install openai"
            ) from exc

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}] + messages,
        )
        return ProviderResponse(
            text=response.choices[0].message.content,
            model=self._model,
            provider=self.name,
        )
