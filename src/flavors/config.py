"""Configuration placeholder module."""

from dataclasses import dataclass


@dataclass
class ModelConfig:
    mistral_model: str = "open-mistral-7b"
    claude_model: str = "claude-opus-4-6"
