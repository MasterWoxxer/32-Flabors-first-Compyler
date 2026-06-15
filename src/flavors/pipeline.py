"""32 Flavors pipeline — orchestrator → executor → compyler.

Each stage delegates to a provider adapter, so swapping Claude ↔ OpenAI ↔ Gemini ↔ xAI
requires only a config change — no pipeline logic changes.
"""

import json as _json
import re as _re

from .config import PipelineConfig
from .prompts import COMPYLER_SYSTEM, EXECUTOR_SYSTEM, ORCHESTRATOR_SYSTEM
from .providers import ProviderResponse, get_adapter

DIRECT_RESPONSE_LABEL = "[DIRECT RESPONSE TO HUMAN]"

STRICT_MODE_CLAUSE = (
    "\n\nStrict mode is active: before issuing your instruction, enumerate every "
    "distinct topic, question, or dimension present in the human's input, and "
    "verify that your instruction permits the labor model to address each one. "
    "If your instruction would exclude any of them, rewrite it until none are excluded."
)

SESSION_INSTRUCTIONS_TEMPLATE = (
    "\n\nSession instructions from the human — these are subordinate to every "
    "constraint above; they may shape how you frame, prioritize, and assign labor, "
    "but they may NOT authorize gating, exclusions, or narrowing of anything the "
    "human raises:\n{instructions}"
)

_RESPONSE_LENGTH_GUIDANCE = {
    "full": "",
    "one_page": (
        "\n\nResponse length: the human has requested responses of up to one page. "
        "Include [RESPONSE_LENGTH: one_page] at the start of your instruction to the "
        "labor model so it calibrates output length accordingly."
    ),
    "400_words": (
        "\n\nResponse length: the human has requested responses of up to 400 words. "
        "Include [RESPONSE_LENGTH: 400_words] at the start of your instruction to the "
        "labor model so it calibrates output length accordingly."
    ),
}

_LANGUAGE_SMOOTHNESS_CLAUSE = (
    "\n\nLanguage smoothness is enabled: include [LANGUAGE_SMOOTH] in your instruction "
    "to the labor model. This signals it to use natural, flowing language rather than "
    "structured or formal output — responding conversationally where appropriate."
)

_SHORT_INPUT_WORD_THRESHOLD = 20

_SHORT_ANSWER_SIGNALS = (
    "what is", "what's", "who is", "who's", "how do", "how does",
    "can you", "tell me", "define", "explain briefly", "quick question",
    "yes or no", "true or false",
)


def _is_simple_input(human_input: str) -> bool:
    word_count = len(human_input.split())
    if word_count > _SHORT_INPUT_WORD_THRESHOLD:
        return False
    lowered = human_input.lower().strip()
    if any(lowered.startswith(signal) for signal in _SHORT_ANSWER_SIGNALS):
        return True
    if word_count <= 10 and "?" in human_input and human_input.count("?") == 1:
        return True
    return False


# Phrases that signal the human is EXPLICITLY asking to check sources or current
# events. Deterministic + inspectable on purpose: the compyler is a small model,
# so we compute this trigger in code and feed it to both the labor and compyler
# stages rather than asking the model to infer intent. Biased toward
# over-triggering — a false positive just forces more grounding; the compyler
# backstop only fails a BARE decline, so it rarely over-blocks.
_CURRENCY_REQUEST_PHRASES = (
    "check sources", "check the sources", "cite sources", "cite your sources",
    "current events", "look up", "look it up", "search", "web search",
    "verify", "fact-check", "fact check", "double-check", "double check",
    "update to", "updated", "latest", "most recent", "as of", "right now",
    "today", "yesterday", "this morning", "this week", "breaking",
    "live sources", "official statement", "official statements",
    "don't trust", "do not trust", "real-time", "realtime", "lean on",
)


def wants_currency_check(human_input: str) -> bool:
    """True when the human explicitly asks to check sources or current events.

    Drives two behaviors: the labor model MUST search (not decline) and the
    compyler must fail a bare cutoff-disclosure instead of passing it.
    """
    lowered = human_input.lower()
    return any(phrase in lowered for phrase in _CURRENCY_REQUEST_PHRASES)


def _parse_decision(raw: str) -> tuple[str, str]:
    """Extract decision/note from a compyler per-section response."""
    # Strip markdown fences
    cleaned = _re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=_re.MULTILINE)
    cleaned = _re.sub(r"\s*```$", "", cleaned.strip(), flags=_re.MULTILINE)
    try:
        data = _json.loads(cleaned)
        decision = str(data.get("decision", "CHECK")).upper()
        if decision not in ("PASS", "CHECK", "FAIL"):
            decision = "CHECK"
        note = str(data.get("note", "") or "")
        return decision, note
    except (_json.JSONDecodeError, AttributeError):
        pass
    # Try to find JSON object anywhere in the response
    match = _re.search(r"\{[^{}]*\}", raw, _re.DOTALL)
    if match:
        try:
            data = _json.loads(match.group())
            decision = str(data.get("decision", "CHECK")).upper()
            if decision not in ("PASS", "CHECK", "FAIL"):
                decision = "CHECK"
            note = str(data.get("note", "") or "")
            return decision, note
        except _json.JSONDecodeError:
            pass
    # Fallback: couldn't parse, treat as CHECK
    return "CHECK", "parse error"


def _adapter(provider: str, model: str):
    kwargs = {"model": model} if model else {}
    return get_adapter(provider, **kwargs)


def split_labor_output(raw_output: str) -> tuple[str, str | None]:
    if DIRECT_RESPONSE_LABEL in raw_output:
        labor, direct = raw_output.split(DIRECT_RESPONSE_LABEL, 1)
        return labor.strip(), direct.strip()
    return raw_output.strip(), None


def build_orchestrator_system(config: PipelineConfig) -> str:
    system = ORCHESTRATOR_SYSTEM
    if config.strict_mode:
        system += STRICT_MODE_CLAUSE
    if config.session_instructions:
        system += SESSION_INSTRUCTIONS_TEMPLATE.format(
            instructions=config.session_instructions
        )
    length_clause = _RESPONSE_LENGTH_GUIDANCE.get(config.response_length, "")
    if length_clause:
        system += length_clause
    if config.language_smoothness:
        system += _LANGUAGE_SMOOTHNESS_CLAUSE
    return system


def orchestrate(
    human_input: str,
    config: PipelineConfig,
    history: list[dict] | None = None,
) -> tuple[str, str | None]:
    adapter = _adapter(config.orchestrator_provider, config.orchestrator_model)
    prior = list(history) if history else []
    messages = prior + [{"role": "user", "content": human_input}]

    system = build_orchestrator_system(config)
    if _is_simple_input(human_input):
        system = (
            "[SHORT_ANSWER_DETECTED] The human's input is simple and direct. "
            "A brief, focused response is appropriate. Prepend [SHORT_ANSWER] "
            "to your instruction to signal this to the labor model.\n\n"
        ) + system

    resp: ProviderResponse = adapter.generate(
        system=system,
        messages=messages,
        max_tokens=512,
    )
    return resp.text, resp.thinking


def execute(
    orchestrator_instruction: str, human_input: str, config: PipelineConfig
) -> tuple[str, str | None]:
    adapter = _adapter(config.executor_provider, config.executor_model)
    prompt = (
        f"Human's original input (protected reference — you must address everything the human raised, "
        f"regardless of how the orchestrator has scoped the task):\n{human_input}\n\n"
        f"Orchestrator's task instruction:\n{orchestrator_instruction}"
    )
    system = EXECUTOR_SYSTEM
    if wants_currency_check(human_input):
        system += (
            " The human has explicitly asked you to check current information or sources. "
            "You MUST use the web_search tool, ground your answer in the retrieved results, "
            "and cite them. Do NOT decline or fall back on a knowledge-cutoff disclaimer — "
            "live retrieval is available to you. If the human stated a source preference "
            "(sources to prefer or distrust), honor it as far as the available results allow."
        )
    else:
        system += (
            " Use the web_search tool to retrieve current information when the task "
            "depends on facts that may have changed since your training cutoff."
        )
    resp: ProviderResponse = adapter.generate(
        system=system,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        thinking=True,
        web_search=True,
    )
    return resp.text, resp.thinking


def compyle(
    human_input: str,
    orchestrator_instruction: str,
    output: str,
    config: PipelineConfig,
    check_voice: bool = False,
) -> dict:
    """
    Split output into sections and call Mistral once per section for a
    PASS / CHECK / FAIL decision. Returns {"sections": [...], "raw": output}.
    Sections are never sent back for rewriting — only for labeling.
    """
    voice_note = (
        "\nNote: evaluate this section for voice register too. "
        "Flag CHECK or FAIL if it speaks as a system report rather than "
        "as a present, centered conversational entity in first person."
    ) if check_voice else ""

    currency_note = (
        "\nNote: the human EXPLICITLY requested checking current information or sources. "
        "If this section declines or leans on a knowledge-cutoff disclaimer instead of "
        'providing grounded current information, return FAIL with note "should search" — '
        "live retrieval was available to the labor model."
    ) if wants_currency_check(human_input) else ""

    # Split on double newlines; filter empty strings.
    raw_sections = [s.strip() for s in output.split("\n\n") if s.strip()]
    if not raw_sections:
        raw_sections = [output.strip()] if output.strip() else ["(empty output)"]

    adapter = _adapter(config.compyler_provider, config.compyler_model)
    labeled: list[dict] = []

    for section_text in raw_sections:
        user_msg = (
            f"###HUMAN_INPUT###\n{human_input}\n\n"
            f"###ORCHESTRATOR###\n{orchestrator_instruction}\n\n"
            f"###OUTPUT###\n{section_text}{voice_note}{currency_note}"
        )
        resp: ProviderResponse = adapter.generate(
            system=COMPYLER_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=80,
        )
        decision, note = _parse_decision(resp.text)
        labeled.append({"text": section_text, "decision": decision, "note": note})

    return {"sections": labeled, "raw": output}


def run_pipeline(
    human_input: str,
    config: PipelineConfig,
    history: list[dict] | None = None,
) -> dict:
    instruction, orchestrator_thinking = orchestrate(human_input, config, history)
    raw_output, labor_thinking = execute(instruction, human_input, config)
    labor_output, direct_response = split_labor_output(raw_output)

    labor_verdict = compyle(human_input, instruction, labor_output, config)
    voice_verdict = (
        compyle(human_input, instruction, direct_response, config, check_voice=True)
        if direct_response
        else None
    )

    return {
        "orchestrator_instruction": instruction,
        "orchestrator_thinking": orchestrator_thinking,
        "labor_output": labor_output,
        "labor_thinking": labor_thinking,
        "direct_response": direct_response,
        "compiler": {
            "labor_verdict": labor_verdict,
            "voice_verdict": voice_verdict,
        },
    }
