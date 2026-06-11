"""Anthropic Claude provider adapter."""

import os

import anthropic

from .base import ProviderAdapter, ProviderResponse

# Thinking tokens count toward max_tokens — when thinking is on, make sure
# the request has room for both the trace and the answer.
_THINKING_MAX_TOKENS = 16000


class ClaudeAdapter(ProviderAdapter):
    DEFAULT_MODEL = "claude-opus-4-8"

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
        thinking: bool = False,
    ) -> ProviderResponse:
        extra: dict = {}
        if thinking:
            # Opus 4.6+ supports adaptive thinking only (budget_tokens 400s).
            # display="summarized" opts into visible thinking text — on
            # Opus 4.7+ the default is "omitted" (blocks arrive empty), and
            # the whole point here is showing the trace in the UI.
            extra["thinking"] = {"type": "adaptive", "display": "summarized"}
            max_tokens = max(max_tokens, _THINKING_MAX_TOKENS)

        resp = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            # cache_control: the pipeline reuses the same system prompts every
            # call. Note Opus's minimum cacheable prefix is 4096 tokens, so
            # this only pays off once prompts grow past that — harmless below.
            system=[
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages,
            **extra,
        )

        text = "".join(b.text for b in resp.content if b.type == "text")
        thinking_trace = (
            "".join(b.thinking for b in resp.content if b.type == "thinking") or None
        )
        return ProviderResponse(
            text=text,
            model=self._model,
            provider=self.name,
            thinking=thinking_trace,
        )
