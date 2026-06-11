"""xAI Grok provider adapter.

xAI's API is OpenAI-compatible, so this adapter reuses the openai package.
Install `openai` and set XAI_API_KEY to enable.
Swap in by setting EXECUTOR_PROVIDER=xai or via the model toggle in the UI.
"""

import os

from .base import ProviderAdapter, ProviderResponse

_XAI_BASE_URL = "https://api.x.ai/v1"


class XAIAdapter(ProviderAdapter):
    DEFAULT_MODEL = "grok-beta"

    def __init__(self, model: str | None = None):
        self._model = model or os.getenv("XAI_MODEL", self.DEFAULT_MODEL)

    @property
    def name(self) -> str:
        return "xai"

    def generate(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
        thinking: bool = False,  # not supported; ignored
    ) -> ProviderResponse:
        try:
            import openai  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "Install the `openai` package to use the xAI adapter: pip install openai"
            ) from exc

        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url=_XAI_BASE_URL,
        )
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
