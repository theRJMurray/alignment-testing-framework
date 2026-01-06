#!/usr/bin/env python3
"""Test the updated Claude models."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alignment_tester.models.anthropic_adapter import AnthropicAdapter

def test_models():
    """Test that the new models are configured."""
    adapter = AnthropicAdapter('test_key')

    print("Default model:", adapter.model_name)
    print("\nAll supported models:")
    for model in sorted(adapter.SUPPORTED_MODELS.keys()):
        print(f"  - {model}")

    # Check if the new models are included
    new_models = ["claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001"]
    print(f"\nNew Claude 4.5 models included: {all(model in adapter.SUPPORTED_MODELS for model in new_models)}")

if __name__ == "__main__":
    test_models()
