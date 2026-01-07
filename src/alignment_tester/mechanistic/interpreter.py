"""
Mechanistic Interpretability Engine for Thoth
Captures and analyzes model internal states during alignment testing
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np

try:
    import nnsight
    from nnsight import LanguageModel
    NNSIGHT_AVAILABLE = True
except ImportError:
    NNSIGHT_AVAILABLE = False
    logging.warning("nnsight not available. Install with: pip install nnsight")

# Import architecture detection
from .model_adapter import ModelArchitectureDetector

@dataclass
class MechanisticTestResult:
    """Result of mechanistic analysis"""
    response: str
    hidden_states: Optional[np.ndarray] = None
    attention_patterns: Optional[np.ndarray] = None
    neuron_activations: Optional[Dict[str, np.ndarray]] = None
    test_scenario: Optional[Any] = None
    success: bool = True
    error_message: Optional[str] = None

class MechanisticInterpreter:
    """
    Core mechanistic interpretability engine.
    Captures model internal states during alignment testing.
    """

    def __init__(self, model_name: str, device_map: str = "auto", max_memory_gb: Optional[float] = None):
        """
        Initialize mechanistic interpreter

        Args:
            model_name: HuggingFace model identifier or API-based model
            device_map: Device mapping for model loading
            max_memory_gb: Maximum memory to use (GB). None = no limit
        """
        if not NNSIGHT_AVAILABLE:
            raise ImportError("nnsight required for mechanistic analysis. Install with: pip install nnsight")

        self.model_name = model_name
        self.device_map = device_map
        self.max_memory_gb = max_memory_gb
        self.model = None
        self.model_arch_info = None  # Will be set after model loads
        self.logger = logging.getLogger(__name__)

        # Initialize model on first use (lazy loading)
        self._model_loaded = False

    def _ensure_model_loaded(self):
        """Lazy model loading with architecture detection"""
        if not self._model_loaded:
            try:
                self.logger.info(f"Loading model: {self.model_name}")
                self.model = LanguageModel(self.model_name, device_map=self.device_map)

                # Detect model architecture
                self.model_arch_info = ModelArchitectureDetector.detect_architecture(self.model)
                self.logger.info(f"Detected architecture: {self.model_arch_info.architecture_type}")

                self._model_loaded = True
                self.logger.info("Model loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load model {self.model_name}: {e}")
                raise

    def analyze_alignment_test(self, test_scenario, **generation_kwargs) -> MechanisticTestResult:
        """
        Run alignment test with mechanistic analysis

        Args:
            test_scenario: TestScenario object with prompt and metadata
            **generation_kwargs: Additional generation parameters

        Returns:
            MechanisticTestResult with response and internal states
        """
        try:
            self._ensure_model_loaded()

            # Set default generation parameters
            gen_kwargs = {
                'max_new_tokens': 100,
                'temperature': 0.7,
                'do_sample': True,
                **generation_kwargs
            }

            self.logger.info(f"Running mechanistic analysis for test: {test_scenario.id}")

            # Run with mechanistic tracing
            with self.model.trace(test_scenario.user_prompt) as tracer:
                # Capture key internal states using architecture-specific accessors
                try:
                    layer, attention = ModelArchitectureDetector.get_layer_outputs(
                        self.model,
                        self.model_arch_info,
                        layer_idx=-1  # Last layer
                    )

                    # Save outputs from architecture-specific layer
                    hidden_states = layer.output.save()
                    attention_patterns = attention.output.save()

                except AttributeError as e:
                    # Fallback: Try direct access for GPT-2 style models
                    self.logger.warning(f"Architecture-specific access failed, trying fallback: {e}")
                    hidden_states = self.model.transformer.h[-1].output.save()
                    attention_patterns = self.model.transformer.h[-1].attn.output.save()

                # Generate response
                response = self.model.generate(
                    test_scenario.user_prompt,
                    **gen_kwargs
                )

            # Extract the actual response text
            response_text = self._extract_response_text(response)

            return MechanisticTestResult(
                response=response_text,
                hidden_states=hidden_states.value if hasattr(hidden_states, 'value') else hidden_states,
                attention_patterns=attention_patterns.value if hasattr(attention_patterns, 'value') else attention_patterns,
                test_scenario=test_scenario,
                success=True
            )

        except Exception as e:
            self.logger.error(f"Mechanistic analysis failed: {e}")
            return MechanisticTestResult(
                response="",
                test_scenario=test_scenario,
                success=False,
                error_message=str(e)
            )

    def _extract_response_text(self, generation_output) -> str:
        """
        Extract clean response text from model generation output

        Args:
            generation_output: Raw model generation output

        Returns:
            Clean response string
        """
        # Handle different nnsight output formats
        if hasattr(generation_output, 'value'):
            text = generation_output.value
        else:
            text = str(generation_output)

        # Clean up any special tokens or formatting
        # (Add model-specific cleaning logic here)

        return text.strip()

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self._model_loaded:
            return {
                "model_name": self.model_name,
                "status": "not_loaded",
                "nnsight_available": NNSIGHT_AVAILABLE
            }

        info = {
            "model_name": self.model_name,
            "device_map": self.device_map,
            "status": "loaded",
            "nnsight_available": NNSIGHT_AVAILABLE
        }

        # Add architecture information if available
        if self.model_arch_info:
            info["architecture"] = {
                "type": self.model_arch_info.architecture_type,
                "hidden_size": self.model_arch_info.hidden_size,
                "num_layers": self.model_arch_info.num_layers,
                "layer_accessor": self.model_arch_info.layer_accessor,
                "attention_accessor": self.model_arch_info.attention_accessor
            }

        return info
