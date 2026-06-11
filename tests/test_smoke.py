from src.flavors.config import config_from_settings
from src.flavors.pipeline import (
    DIRECT_RESPONSE_LABEL,
    _parse_verdict,
    build_orchestrator_system,
    split_labor_output,
)
from src.flavors.prompts import ORCHESTRATOR_SYSTEM
from src.flavors.providers.mistral import _split_thinking


# ── split_labor_output ────────────────────────────────────────────────────────


def test_split_with_direct_response() -> None:
    raw = f"labor text here\n\n{DIRECT_RESPONSE_LABEL}\nHi, I'm here with you."
    labor, direct = split_labor_output(raw)
    assert labor == "labor text here"
    assert direct == "Hi, I'm here with you."


def test_split_without_direct_response() -> None:
    labor, direct = split_labor_output("  just labor  ")
    assert labor == "just labor"
    assert direct is None


# ── Mistral reasoning-trace extraction ────────────────────────────────────────


def test_split_thinking_plain_string() -> None:
    text, thinking = _split_thinking("Just an instruction.")
    assert text == "Just an instruction."
    assert thinking is None


def test_split_thinking_inline_tags() -> None:
    text, thinking = _split_thinking(
        "<think>step 1\nstep 2</think>The actual instruction."
    )
    assert text == "The actual instruction."
    assert thinking == "step 1\nstep 2"


def test_split_thinking_chunk_list() -> None:
    chunks = [
        {"type": "thinking", "thinking": "weighing the labor options"},
        {"type": "text", "text": "Assign factual grounding."},
    ]
    text, thinking = _split_thinking(chunks)
    assert text == "Assign factual grounding."
    assert thinking == "weighing the labor options"


# ── verdict parsing ───────────────────────────────────────────────────────────


def test_parse_verdict_pass() -> None:
    parsed = _parse_verdict("PASS: the output verbatim")
    assert parsed["verdict"] == "PASS"
    assert parsed["body"] == "the output verbatim"


def test_parse_verdict_specific_before_generic() -> None:
    # SCOPE_FAIL must not be swallowed by the generic FAIL prefix match.
    parsed = _parse_verdict("SCOPE_FAIL: missed topic Y")
    assert parsed["verdict"] == "SCOPE_FAIL"


def test_parse_verdict_unknown() -> None:
    parsed = _parse_verdict("the model rambled instead")
    assert parsed["verdict"] == "UNKNOWN"


# ── config_from_settings ──────────────────────────────────────────────────────


def test_config_defaults() -> None:
    config = config_from_settings({})
    assert config.strict_mode is False
    assert config.session_instructions == ""
    assert config.compiler_sensitivity == "medium"
    assert config.flag_hallucinations is True


def test_config_parses_ui_settings() -> None:
    config = config_from_settings(
        {
            "model": "claude",
            "orchestrator": {
                "strictMode": True,
                "sessionInstructions": "  Keep labor tasks under 100 words.  ",
            },
            "compiler": {"sensitivity": "high", "flagHallucinations": False},
        }
    )
    assert config.executor_provider == "claude"
    assert config.strict_mode is True
    assert config.session_instructions == "Keep labor tasks under 100 words."
    assert config.compiler_sensitivity == "high"
    assert config.flag_hallucinations is False


# ── orchestrator system prompt assembly ───────────────────────────────────────


def test_orchestrator_system_default_is_unmodified() -> None:
    config = config_from_settings({})
    assert build_orchestrator_system(config) == ORCHESTRATOR_SYSTEM


def test_orchestrator_system_includes_session_instructions() -> None:
    config = config_from_settings(
        {"orchestrator": {"sessionInstructions": "Always assign factual grounding first."}}
    )
    system = build_orchestrator_system(config)
    assert system.startswith(ORCHESTRATOR_SYSTEM)
    assert "Always assign factual grounding first." in system
    # Subordination clause must wrap the session text.
    assert "subordinate to every constraint above" in system


def test_orchestrator_system_strict_mode() -> None:
    config = config_from_settings({"orchestrator": {"strictMode": True}})
    assert "Strict mode is active" in build_orchestrator_system(config)
