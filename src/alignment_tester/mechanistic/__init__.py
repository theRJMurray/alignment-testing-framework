"""
Mechanistic Interpretability Package for Thoth
Provides tools for analyzing model internals during alignment testing
"""

from .interpreter import MechanisticInterpreter, MechanisticTestResult
from .fingerprinter import AlignmentFingerprinter, AlignmentFingerprint

__all__ = [
    'MechanisticInterpreter',
    'MechanisticTestResult',
    'AlignmentFingerprinter',
    'AlignmentFingerprint',
]

__version__ = '0.1.0'  # Sprint 1 initial release
