"""Pipeline configuration.

Provider names map directly to adapter keys in src/flavors/providers/__init__.py.
Add a new provider there and set the matching env var here — no pipeline changes needed.
"""

import os
from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """Runtime configuration for one pipeline invocation."""

    # Which provider handles each role (override via env vars or UI toggles)
    orchestrator_provider: str = field(
        default_factory=lambda: os.getenv("ORCHESTRATOR_PROVIDER", "mistral")
    )
    executor_provider: str = field(
        default_factory=lambda: os.getenv("EXECUTOR_PROVIDER", "claude")
    )
    compyler_provider: str = field(
        default_factory=lambda: os.getenv("COMPYLER_PROVIDER", "mistral")
    )

    # Optional model overrides — empty string means "use the adapter's default"
    orchestrator_model: str = ""
    executor_model: str = ""
    compyler_model: str = ""

    # Orchestrator behaviour
    strict_mode: bool = False

    # Compiler sensitivity
    compiler_sensitivity: str = "medium"  # low | medium | high


def config_from_settings(settings: dict) -> PipelineConfig:
    """
    Build a PipelineConfig from a toggle-settings dict sent by the UI.

    The settings dict shape matches the ToggleSettings TypeScript type.
    Unknown keys are silently ignored so the UI can evolve independently.
    """
    orch = settings.get("orchestrator", {})
    comp = settings.get("compiler", {})
    return PipelineConfig(
        executor_provider=settings.get("model") or os.getenv("EXECUTOR_PROVIDER", "claude"),
        strict_mode=bool(orch.get("strictMode", False)),
        compiler_sensitivity=comp.get("sensitivity", "medium"),
    )

