"""Google Gemini provider adapter.

Install `google-generativeai` and set GEMINI_API_KEY to enable.
Swap in by setting EXECUTOR_PROVIDER=gemini or via the model toggle in the UI.
"""

import os

from .base import ProviderAdapter, ProviderResponse


class GeminiAdapter(ProviderAdapter):
    DEFAULT_MODEL = "gemini-1.5-pro"

    def __init__(self, model: str | None = None):
        self._model = model or os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)

    @property
    def name(self) -> str:
        return "gemini"

    def generate(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
        thinking: bool = False,  # not supported; ignored
    ) -> ProviderResponse:
        try:
            import google.generativeai as genai  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "Install `google-generativeai` to use the Gemini adapter: "
                "pip install google-generativeai"
            ) from exc

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(
            model_name=self._model,
            system_instruction=system,
            generation_config={"max_output_tokens": max_tokens},
        )
        # Convert to Gemini role format (user / model)
        gemini_msgs = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in messages
        ]
        response = model.generate_content(gemini_msgs)
        return ProviderResponse(
            text=response.text,
            model=self._model,
            provider=self.name,
        )
