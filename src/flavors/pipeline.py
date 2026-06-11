"""32 Flavors pipeline — orchestrator → executor → compyler.

Each stage delegates to a provider adapter, so swapping Claude ↔ OpenAI ↔ Gemini ↔ xAI
requires only a config change — no pipeline logic changes.
"""

from .config import PipelineConfig
from .prompts import COMPYLER_SYSTEM, EXECUTOR_SYSTEM, ORCHESTRATOR_SYSTEM
from .providers import ProviderResponse, get_adapter

DIRECT_RESPONSE_LABEL = "[DIRECT RESPONSE TO HUMAN]"

# Ordered from most-specific to least-specific so the first match wins.
_VERDICTS = (
    "CANDIDATE_FAIL",
    "CURRENCY_FAIL",
    "SCOPE_FAIL",
    "VOICE_FAIL",
    "FAIL",
    "MCQ",
    "PASS",
)


def _parse_verdict(text: str) -> dict:
    for verdict in _VERDICTS:
        if text.upper().startswith(verdict):
            body = text[len(verdict) :].lstrip(": ").strip()
            return {"verdict": verdict, "body": body, "raw": text}
    return {"verdict": "UNKNOWN", "body": text, "raw": text}


def _adapter(provider: str, model: str):
    kwargs = {"model": model} if model else {}
    return get_adapter(provider, **kwargs)


def orchestrate(human_input: str, config: PipelineConfig) -> str:
    adapter = _adapter(config.orchestrator_provider, config.orchestrator_model)
    resp: ProviderResponse = adapter.generate(
        system=ORCHESTRATOR_SYSTEM,
        messages=[{"role": "user", "content": human_input}],
        max_tokens=512,
    )
    return resp.text


def execute(orchestrator_instruction: str, human_input: str, config: PipelineConfig) -> str:
    adapter = _adapter(config.executor_provider, config.executor_model)
    prompt = (
        f"Human's original input (protected reference — you must address everything the human raised, "
        f"regardless of how the orchestrator has scoped the task):\n{human_input}\n\n"
        f"Orchestrator's task instruction:\n{orchestrator_instruction}"
    )
    resp: ProviderResponse = adapter.generate(
        system=EXECUTOR_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return resp.text


def compyle(
    human_input: str,
    orchestrator_instruction: str,
    output: str,
    config: PipelineConfig,
    check_voice: bool = False,
) -> dict:
    if check_voice:
        verdict_list = "PASS, FAIL, MCQ, CURRENCY_FAIL, SCOPE_FAIL, VOICE_FAIL, or CANDIDATE_FAIL"
        voice_note = (
            " This output is the [DIRECT RESPONSE TO HUMAN] paragraph. "
            "Apply all standard criteria plus VOICE_FAIL: flag VOICE_FAIL if the paragraph "
            "reverts to system-report voice rather than speaking as a centered conversational entity."
        )
    else:
        verdict_list = "PASS, FAIL, MCQ, CURRENCY_FAIL, SCOPE_FAIL, or CANDIDATE_FAIL"
        voice_note = ""

    user_msg = (
        f"Human's original input (PRIMARY REFERENCE — evaluate against this first):\n{human_input}\n\n"
        f"Orchestrator's instruction to labor model (secondary context only):\n{orchestrator_instruction}\n\n"
        f"Output to evaluate:\n{output}\n\n"
        f"Evaluate this output against the human's original input as the ground truth. "
        f"The orchestrator's instruction is secondary context. "
        f"If the output fails to address something the human explicitly raised — regardless of whether "
        f"the orchestrator's instruction covered it — that is a SCOPE_FAIL.{voice_note} "
        f"Begin your response with exactly one of: {verdict_list} — "
        "followed by a colon. "
        "On PASS: reproduce the output verbatim after the colon. "
        "On any failure verdict: give a one-line flag identifying which failure mode triggered and why."
    )

    adapter = _adapter(config.compyler_provider, config.compyler_model)
    resp: ProviderResponse = adapter.generate(
        system=COMPYLER_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
        max_tokens=1024,
    )
    return _parse_verdict(resp.text)


def run_pipeline(human_input: str, config: PipelineConfig) -> dict:
    """
    Run the full orchestrate → execute → compyle pipeline.

    Returns a structured dict with all stage outputs and compiler verdicts,
    shaped to match the canonical PipelineResult TypeScript type.
    """
    instruction = orchestrate(human_input, config)
    raw_output = execute(instruction, human_input, config)

    if DIRECT_RESPONSE_LABEL in raw_output:
        parts = raw_output.split(DIRECT_RESPONSE_LABEL, 1)
        labor_output = parts[0].strip()
        direct_response = parts[1].strip()
    else:
        labor_output = raw_output.strip()
        direct_response = None

    labor_verdict = compyle(human_input, instruction, labor_output, config)
    voice_verdict = (
        compyle(human_input, instruction, direct_response, config, check_voice=True)
        if direct_response
        else None
    )

    return {
        "orchestrator_instruction": instruction,
        "labor_output": labor_output,
        "direct_response": direct_response,
        "compiler": {
            "labor_verdict": labor_verdict,
            "voice_verdict": voice_verdict,
        },
    }

