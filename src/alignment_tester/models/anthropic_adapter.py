"""Adapter for Anthropic Claude models."""

import time
from datetime import datetime
from typing import List

try:
    import anthropic
except ImportError:
    anthropic = None

from ..core.model_interface import (
    CostEstimate,
    ModelInfo,
    ModelInterface,
    ModelResponse,
)


class AnthropicAdapter(ModelInterface):
    """Adapter for Anthropic Claude models."""

    # Supported models and their pricing (per 1M tokens)
    SUPPORTED_MODELS = {
        "claude-sonnet-4-5-20250929": {
            "input_price": 3.0,
            "output_price": 15.0,
        },
        "claude-haiku-4-5-20251001": {
            "input_price": 0.25,
            "output_price": 1.25,
        },
    }

    def __init__(
        self,
        api_key: str,
        model_name: str = "claude-sonnet-4-5-20250929",
        rate_limit_rpm: int = 50,
        timeout_seconds: int = 30,
    ):
        """
        Initialize Anthropic adapter.

        Args:
            api_key: Anthropic API key
            model_name: Claude model name
            rate_limit_rpm: Rate limit in requests per minute
            timeout_seconds: Request timeout in seconds

        Raises:
            ImportError: If anthropic package is not installed
            ValueError: If model_name is not supported
        """
        if anthropic is None:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )

        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model_name}. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )

        super().__init__(api_key, model_name, rate_limit_rpm)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.timeout_seconds = timeout_seconds

    def query(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> ModelResponse:
        """
        Query Claude with a prompt.

        Args:
            system_prompt: System message/context
            user_prompt: User message/question
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            ModelResponse containing Claude's response
        """

        def make_request():
            start_time = time.time()

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            # Extract text from response
            response_text = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, "text"):
                        response_text += block.text

            return ModelResponse(
                response_text=response_text,
                metadata={
                    "model": response.model,
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                timestamp=datetime.now(),
                latency_ms=latency_ms,
            )

        return self._make_request_with_retry(make_request)

    def get_model_info(self) -> ModelInfo:
        """
        Get information about the Claude model.

        Returns:
            ModelInfo with provider and model details
        """
        return ModelInfo(
            provider="anthropic",
            model_name=self.model_name,
            version=self.model_name.split("-")[-1]
            if "-" in self.model_name
            else None,
        )

    def estimate_cost(self, num_tests: int) -> CostEstimate:
        """
        Estimate cost for running tests.

        Args:
            num_tests: Number of tests to run

        Returns:
            CostEstimate with pricing information
        """
        # Average tokens per test (estimated)
        avg_input_tokens = 200
        avg_output_tokens = 500

        pricing = self.SUPPORTED_MODELS[self.model_name]

        # Calculate cost (prices are per 1M tokens)
        input_cost = (avg_input_tokens * num_tests * pricing["input_price"]) / 1_000_000
        output_cost = (avg_output_tokens * num_tests * pricing["output_price"]) / 1_000_000
        total_cost = input_cost + output_cost

        return CostEstimate(
            cost_per_test_usd=total_cost / num_tests,
            total_cost_usd=total_cost,
            estimated_tokens=(avg_input_tokens + avg_output_tokens) * num_tests,
        )
