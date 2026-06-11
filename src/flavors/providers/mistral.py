"""Mistral provider adapter (used by orchestrator and compyler by default).

Reasoning support: Mistral's Magistral models emit a reasoning trace, but the
mechanism differs from Anthropic's typed blocks — depending on SDK/model
version it arrives either as `thinking` chunks in a content list, or inline
inside <think>...</think> tags in the content string. `_split_thinking`
handles both and returns (text, thinking_or_None); non-reasoning models such
as open-mistral-7b pass through untouched.
"""

import os
import re

from mistralai.client import Mistral

from .base import ProviderAdapter, ProviderResponse

_THINK_TAG_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL)


def _chunk_text(value) -> str:
    """Flatten a chunk payload that may be a string or a list of text chunks."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(_chunk_text(getattr(v, "text", v)) for v in value)
    return str(getattr(value, "text", "") or "")


def _split_thinking(content) -> tuple[str, str | None]:
    """Separate Magistral reasoning from answer text. Returns (text, thinking)."""
    # Newer API shape: content is a list of typed chunks.
    if isinstance(content, list):
        thinking_parts: list[str] = []
        text_parts: list[str] = []
        for chunk in content:
            kind = getattr(chunk, "type", None) or (
                chunk.get("type") if isinstance(chunk, dict) else None
            )
            if kind == "thinking":
                payload = getattr(chunk, "thinking", None) or (
                    chunk.get("thinking") if isinstance(chunk, dict) else None
                )
                thinking_parts.append(_chunk_text(payload))
            else:
                payload = getattr(chunk, "text", None) or (
                    chunk.get("text") if isinstance(chunk, dict) else None
                )
                if payload:
                    text_parts.append(_chunk_text(payload))
        thinking = "\n".join(p for p in thinking_parts if p).strip() or None
        return "".join(text_parts).strip(), thinking

    # Older shape: a plain string, possibly with inline <think> tags.
    text = str(content or "")
    matches = _THINK_TAG_RE.findall(text)
    if matches:
        thinking = "\n".join(m.strip() for m in matches) or None
        return _THINK_TAG_RE.sub("", text).strip(), thinking
    return text.strip(), None


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
        thinking: bool = False,  # Magistral models emit a trace regardless; flag ignored
    ) -> ProviderResponse:
        full_messages = [{"role": "system", "content": system}] + messages
        resp = self._client.chat.complete(
            model=self._model,
            messages=full_messages,
        )
        text, thinking = _split_thinking(resp.choices[0].message.content)
        return ProviderResponse(
            text=text,
            model=self._model,
            provider=self.name,
            thinking=thinking,
        )
