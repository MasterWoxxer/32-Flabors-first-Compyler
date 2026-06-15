"""Anthropic Claude provider adapter."""

import os
import threading

import anthropic

from .base import ProviderAdapter, ProviderResponse

# Thinking tokens count toward max_tokens — when thinking is on, make sure
# the request has room for both the trace and the answer.
_THINKING_MAX_TOKENS = 16000

# Web-search budget. Vercel's free tier kills the function at 60s.
# - Use the lighter (non-dynamic-filtering) tool: ~7s/search vs ~20s for the
#   _20260209 dynamic-filtering version, which compounds past the budget.
# - Cap searches so a multi-part query can't loop indefinitely.
# - Enforce a HARD wall-clock deadline in a daemon thread. The SDK's `timeout=`
#   does NOT bound the server-side web_search loop (its read timeout resets as
#   the held-open response streams), so we time the call ourselves and return an
#   honest "couldn't verify" rather than let Vercel kill the function at 60s.
_WEB_SEARCH_TOOL = "web_search_20250305"
_WEB_SEARCH_MAX_USES = 2
_WEB_SEARCH_DEADLINE_S = 52.0

# Block types the server emits while running web search / dynamic filtering.
_TOOL_RESULT_BLOCK_TYPES = (
    "web_search_tool_result",
    "code_execution_tool_result",
    "server_tool_use",
)


def _final_answer_text(content: list) -> str:
    """Return only the model's answer, dropping search-process narration.

    With server-side web search the model interleaves narration ("Let me parse
    the JSON…") with tool blocks, then writes the real answer after the last
    tool result. Keep only the text blocks that follow the final tool block; if
    there were no tool blocks, keep all text (normal, non-search calls).
    """
    last_tool = -1
    for i, b in enumerate(content):
        if b.type in _TOOL_RESULT_BLOCK_TYPES:
            last_tool = i
    answer_blocks = content[last_tool + 1:] if last_tool >= 0 else content
    text = "".join(b.text for b in answer_blocks if b.type == "text").strip()
    # Fallback: if stripping left nothing (e.g. answer came before a trailing
    # tool block), fall back to all text rather than returning empty.
    if not text:
        text = "".join(b.text for b in content if b.type == "text").strip()
    return text


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
        web_search: bool = False,
    ) -> ProviderResponse:
        extra: dict = {}
        if web_search:
            # Server-side web search. Cap searches; the wall-clock is enforced
            # below (a daemon thread), not via the SDK timeout.
            extra["tools"] = [
                {
                    "type": _WEB_SEARCH_TOOL,
                    "name": "web_search",
                    "max_uses": _WEB_SEARCH_MAX_USES,
                }
            ]
        if thinking:
            # Opus 4.6+ supports adaptive thinking only (budget_tokens 400s).
            # display="summarized" opts into visible thinking text — on
            # Opus 4.7+ the default is "omitted" (blocks arrive empty), and
            # the whole point here is showing the trace in the UI.
            extra["thinking"] = {"type": "adaptive", "display": "summarized"}
            max_tokens = max(max_tokens, _THINKING_MAX_TOKENS)

        def _create():
            return self._client.messages.create(
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

        if web_search:
            # Hard wall-clock bound: run in a daemon thread and abandon it if it
            # overruns. The orphaned thread won't block process exit (daemon),
            # and on Vercel it dies with the function. Returning timed_out lets
            # the caller disclose instead of shipping ungrounded claims.
            box: dict = {}

            def _run():
                try:
                    box["resp"] = _create()
                except Exception as exc:  # noqa: BLE001
                    box["err"] = exc

            th = threading.Thread(target=_run, daemon=True)
            th.start()
            th.join(_WEB_SEARCH_DEADLINE_S)
            if th.is_alive() or isinstance(box.get("err"), anthropic.APITimeoutError):
                return ProviderResponse(
                    text="", model=self._model, provider=self.name,
                    searched=False, timed_out=True,
                )
            if "err" in box:
                raise box["err"]
            resp = box["resp"]
        else:
            resp = _create()

        text = _final_answer_text(resp.content)
        thinking_trace = (
            "".join(b.thinking for b in resp.content if b.type == "thinking") or None
        )
        searched = any(b.type in _TOOL_RESULT_BLOCK_TYPES for b in resp.content)
        return ProviderResponse(
            text=text,
            model=self._model,
            provider=self.name,
            thinking=thinking_trace,
            searched=searched,
            timed_out=False,
        )
