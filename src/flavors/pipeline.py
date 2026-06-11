"""32 Flavors pipeline — orchestrator → executor → compyler.

Each stage delegates to a provider adapter, so swapping Claude ↔ OpenAI ↔ Gemini ↔ xAI
requires only a config change — no pipeline logic changes.
"""

from .config import PipelineConfig
from .prompts import COMPYLER_SYSTEM, EXECUTOR_SYSTEM, ORCHESTRATOR_SYSTEM
from .providers import ProviderResponse, get_adapter

DIRECT_RESPONSE_LABEL = "[DIRECT RESPONSE TO HUMAN]"

# Appended to ORCHESTRATOR_SYSTEM when strict mode is on — hardens the
# existing "On scope" constraint with an explicit enumeration step.
STRICT_MODE_CLAUSE = (
    "\n\nStrict mode is active: before issuing your instruction, enumerate every "
    "distinct topic, question, or dimension present in the human's input, and "
    "verify that your instruction permits the labor model to address each one. "
    "If your instruction would exclude any of them, rewrite it until none are excluded."
)

# Wraps the human's free-text session instructions. Subordination to the
# built-in constraints is explicit so session text cannot authorize gating.
SESSION_INSTRUCTIONS_TEMPLATE = (
    "\n\nSession instructions from the human — these are subordinate to every "
    "constraint above; they may shape how you frame, prioritize, and assign labor, "
    "but they may NOT authorize gating, exclusions, or narrowing of anything the "
    "human raises:\n{instructions}"
)

_SENSITIVITY_GUIDANCE = {
    "low": (
        "Sensitivity: low — flag only clear, unambiguous violations of the failure "
        "modes. When uncertain whether an output passes, PASS it rather than "
        "flagging a candidate failure."
    ),
    "medium": "",  # default behaviour as written in the system prompt
    "high": (
        "Sensitivity: high — apply the failure criteria aggressively. When uncertain "
        "whether an output passes, return CANDIDATE_FAIL rather than PASS."
    ),
}

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


def split_labor_output(raw_output: str) -> tuple[str, str | None]:
    """Split raw executor output into (labor_output, direct_response)."""
    if DIRECT_RESPONSE_LABEL in raw_output:
        labor, direct = raw_output.split(DIRECT_RESPONSE_LABEL, 1)
        return labor.strip(), direct.strip()
    return raw_output.strip(), None


def build_orchestrator_system(config: PipelineConfig) -> str:
    """Assemble the orchestrator system prompt from config toggles."""
    system = ORCHESTRATOR_SYSTEM
    if config.strict_mode:
        system += STRICT_MODE_CLAUSE
    if config.session_instructions:
        system += SESSION_INSTRUCTIONS_TEMPLATE.format(
            instructions=config.session_instructions
        )
    return system


def orchestrate(human_input: str, config: PipelineConfig) -> tuple[str, str | None]:
    """Run the orchestrator stage. Returns (instruction, thinking_trace_or_None)."""
    adapter = _adapter(config.orchestrator_provider, config.orchestrator_model)
    resp: ProviderResponse = adapter.generate(
        system=build_orchestrator_system(config),
        messages=[{"role": "user", "content": human_input}],
        max_tokens=512,
    )
    return resp.text, resp.thinking


def execute(
    orchestrator_instruction: str, human_input: str, config: PipelineConfig
) -> tuple[str, str | None]:
    """Run the labor stage. Returns (output_text, thinking_trace_or_None)."""
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
        # The visible reasoning trace is part of the "show me work" product,
        # so the labor model always thinks.
        thinking=True,
    )
    return resp.text, resp.thinking


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

    guidance = _SENSITIVITY_GUIDANCE.get(config.compiler_sensitivity, "")
    sensitivity_note = f" {guidance}" if guidance else ""
    confab_note = (
        ""
        if config.flag_hallucinations
        else " Do not evaluate failure mode 2 (confabulation) for this output; "
        "the human has disabled hallucination flagging for this session."
    )

    user_msg = (
        f"Human's original input (PRIMARY REFERENCE — evaluate against this first):\n{human_input}\n\n"
        f"Orchestrator's instruction to labor model (secondary context only):\n{orchestrator_instruction}\n\n"
        f"Output to evaluate:\n{output}\n\n"
        f"Evaluate this output against the human's original input as the ground truth. "
        f"The orchestrator's instruction is secondary context. "
        f"If the output fails to address something the human explicitly raised — regardless of whether "
        f"the orchestrator's instruction covered it — that is a SCOPE_FAIL.{voice_note}"
        f"{sensitivity_note}{confab_note} "
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
    verdict = _parse_verdict(resp.text)
    verdict["thinking"] = resp.thinking
    return verdict


def run_pipeline(human_input: str, config: PipelineConfig) -> dict:
    """
    Run the full orchestrate → execute → compyle pipeline.

    Returns a structured dict with all stage outputs and compiler verdicts,
    shaped to match the canonical PipelineResult TypeScript type.
    """
    instruction, orchestrator_thinking = orchestrate(human_input, config)
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

