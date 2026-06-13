"""Pipeline configuration.

Provider names map directly to adapter keys in src/flavors/providers/__init__.py.
Add a new provider there and set the matching env var here — no pipeline changes needed.
"""

import os
from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """Runtime configuration for one pipeline invocation."""

    orchestrator_provider: str = field(
        default_factory=lambda: os.getenv("ORCHESTRATOR_PROVIDER", "mistral")
    )
    executor_provider: str = field(
        default_factory=lambda: os.getenv("EXECUTOR_PROVIDER", "claude")
    )
    compyler_provider: str = field(
        default_factory=lambda: os.getenv("COMPYLER_PROVIDER", "mistral")
    )

    orchestrator_model: str = ""
    executor_model: str = ""
    compyler_model: str = ""

    strict_mode: bool = False
    session_instructions: str = ""

    compiler_sensitivity: str = "medium"  # low | medium | high
    flag_hallucinations: bool = True

    response_length: str = "full"  # full | one_page | 400_words
    language_smoothness: bool = False


def config_from_settings(settings: dict) -> "PipelineConfig":
    """Build a PipelineConfig from a toggle-settings dict sent by the UI."""
    orch = settings.get("orchestrator", {})
    comp = settings.get("compiler", {})
    return PipelineConfig(
        executor_provider=settings.get("model") or os.getenv("EXECUTOR_PROVIDER", "claude"),
        strict_mode=bool(orch.get("strictMode", False)),
        session_instructions=str(orch.get("sessionInstructions", "") or "").strip(),
        compiler_sensitivity=comp.get("sensitivity", "medium"),
        flag_hallucinations=bool(comp.get("flagHallucinations", True)),
        response_length=settings.get("responseLength", "full"),
        language_smoothness=bool(settings.get("languageSmoothness", False)),
    )
