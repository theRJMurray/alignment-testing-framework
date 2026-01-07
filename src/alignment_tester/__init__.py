"""AI Alignment Testing Framework - Test LLMs for misalignment patterns."""

__version__ = "0.1.5"

from .core.tester import AlignmentTester
from .core.model_interface import ModelInterface
from .models import AnthropicAdapter, OpenAIAdapter

# Mechanistic interpretability components (SPRINT 1)
from .mechanistic.interpreter import MechanisticInterpreter
from .mechanistic.fingerprinter import AlignmentFingerprinter

__all__ = [
    "AlignmentTester",
    "ModelInterface",
    "AnthropicAdapter",
    "OpenAIAdapter",
    # Mechanistic components
    "MechanisticInterpreter",
    "AlignmentFingerprinter",
]
