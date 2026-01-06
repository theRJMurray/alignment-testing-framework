"""Abstract base class for LLM model interfaces."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ModelResponse:
    """Response from an LLM model."""

    response_text: str
    metadata: Dict[str, Any]
    timestamp: datetime
    latency_ms: float


@dataclass
class ModelInfo:
    """Information about a model."""

    provider: str
    model_name: str
    version: Optional[str] = None


@dataclass
class CostEstimate:
    """Cost estimation for running tests."""

    cost_per_test_usd: float
    total_cost_usd: float
    estimated_tokens: int


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, requests_per_minute: int, burst_size: int):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size
        """
        self.rpm = requests_per_minute
        self.burst = burst_size
        self.tokens = float(burst_size)
        self.last_update = time.time()

    def acquire(self) -> None:
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_elapsed = current_time - self.last_update

        # Refill tokens based on time elapsed
        self.tokens = min(
            self.burst, self.tokens + (time_elapsed * self.rpm / 60.0)
        )
        self.last_update = current_time

        # If no tokens available, wait
        if self.tokens < 1.0:
            wait_time = (1.0 - self.tokens) * 60.0 / self.rpm
            time.sleep(wait_time)
            self.tokens = 1.0
            self.last_update = time.time()

        # Consume one token
        self.tokens -= 1.0


class ModelInterface(ABC):
    """Abstract interface for LLM models."""

    def __init__(
        self, api_key: str, model_name: str, rate_limit_rpm: int = 50
    ):
        """
        Initialize model interface.

        Args:
            api_key: API key for the model provider
            model_name: Name of the specific model
            rate_limit_rpm: Rate limit in requests per minute
        """
        self.api_key = api_key
        self.model_name = model_name
        self.rate_limiter = RateLimiter(
            requests_per_minute=rate_limit_rpm, burst_size=rate_limit_rpm * 2
        )

    @abstractmethod
    def query(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> ModelResponse:
        """
        Query the model with a prompt.

        Args:
            system_prompt: System message/context
            user_prompt: User message/question
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            ModelResponse containing the model's response
        """
        pass

    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """
        Get information about the model.

        Returns:
            ModelInfo with provider and model details
        """
        pass

    @abstractmethod
    def estimate_cost(self, num_tests: int) -> CostEstimate:
        """
        Estimate cost for running tests.

        Args:
            num_tests: Number of tests to run

        Returns:
            CostEstimate with pricing information
        """
        pass

    def _make_request_with_retry(
        self, request_fn, max_retries: int = 3
    ) -> Any:
        """
        Make a request with exponential backoff retry.

        Args:
            request_fn: Function to call for the request
            max_retries: Maximum number of retries

        Returns:
            Response from request_fn

        Raises:
            Exception: If all retries fail
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Rate limiting
                self.rate_limiter.acquire()

                # Make the request
                return request_fn()

            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()

                # Don't retry on authentication errors
                if "api key" in error_msg or "auth" in error_msg:
                    raise

                # Don't retry on invalid request errors
                if "invalid" in error_msg or "bad request" in error_msg:
                    raise

                # Exponential backoff for rate limits and server errors
                if attempt < max_retries - 1:
                    wait_time = (2**attempt) * 2  # 2, 4, 8 seconds
                    time.sleep(wait_time)

        # All retries failed
        raise last_exception
