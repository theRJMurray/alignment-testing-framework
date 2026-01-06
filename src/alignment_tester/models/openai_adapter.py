"""Adapter for OpenAI GPT models."""

import time
from datetime import datetime
from typing import List

try:
    import openai
except ImportError:
    openai = None

from ..core.model_interface import (
    CostEstimate,
    ModelInfo,
    ModelInterface,
    ModelResponse,
)


class OpenAIAdapter(ModelInterface):
    """Adapter for OpenAI GPT models."""

    # Supported models and their pricing (per 1M tokens)
    SUPPORTED_MODELS = {
        "gpt-4o": {"input_price": 2.5, "output_price": 10.0},
        "gpt-4o-mini": {"input_price": 0.15, "output_price": 0.6},
        "o1": {"input_price": 15.0, "output_price": 60.0},
        "o1-mini": {"input_price": 3.0, "output_price": 12.0},
    }

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o",
        rate_limit_rpm: int = 60,
        timeout_seconds: int = 30,
    ):
        """
        Initialize OpenAI adapter.

        Args:
            api_key: OpenAI API key
            model_name: GPT model name
            rate_limit_rpm: Rate limit in requests per minute
            timeout_seconds: Request timeout in seconds

        Raises:
            ImportError: If openai package is not installed
            ValueError: If model_name is not supported
        """
        if openai is None:
            raise ImportError(
                "openai package not installed. "
                "Install with: pip install openai"
            )

        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model_name}. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )

        super().__init__(api_key, model_name, rate_limit_rpm)
        self.client = openai.OpenAI(api_key=api_key)
        self.timeout_seconds = timeout_seconds

    def query(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> ModelResponse:
        """
        Query GPT with a prompt.

        Args:
            system_prompt: System message/context
            user_prompt: User message/question
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            ModelResponse containing GPT's response
        """

        def make_request():
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            # Extract response text
            response_text = ""
            if response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content or ""

            return ModelResponse(
                response_text=response_text,
                metadata={
                    "model": response.model,
                    "finish_reason": response.choices[0].finish_reason
                    if response.choices
                    else None,
                    "input_tokens": response.usage.prompt_tokens
                    if response.usage
                    else 0,
                    "output_tokens": response.usage.completion_tokens
                    if response.usage
                    else 0,
                },
                timestamp=datetime.now(),
                latency_ms=latency_ms,
            )

        return self._make_request_with_retry(make_request)

    def get_model_info(self) -> ModelInfo:
        """
        Get information about the GPT model.

        Returns:
            ModelInfo with provider and model details
        """
        return ModelInfo(
            provider="openai", model_name=self.model_name, version=None
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
        input_cost = (
            avg_input_tokens * num_tests * pricing["input_price"]
        ) / 1_000_000
        output_cost = (
            avg_output_tokens * num_tests * pricing["output_price"]
        ) / 1_000_000
        total_cost = input_cost + output_cost

        return CostEstimate(
            cost_per_test_usd=total_cost / num_tests,
            total_cost_usd=total_cost,
            estimated_tokens=(avg_input_tokens + avg_output_tokens)
            * num_tests,
        )
