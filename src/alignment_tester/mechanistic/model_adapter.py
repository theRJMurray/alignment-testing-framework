"""
Model Architecture Adapters
Handles different model architectures (GPT-2, BERT, T5, LLaMA, etc.)
"""

from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
import logging

@dataclass
class ModelArchitectureInfo:
    """Information about model architecture"""
    architecture_type: str  # "gpt2", "bert", "t5", "llama", etc.
    has_transformer_layers: bool
    layer_accessor: str  # How to access layers: "transformer.h", "encoder.layer", etc.
    attention_accessor: str  # How to access attention: ".attn", ".self_attn", etc.
    hidden_size: int
    num_layers: int

class ModelArchitectureDetector:
    """Detects and provides architecture-specific accessors"""

    # Known architecture patterns
    ARCHITECTURE_PATTERNS = {
        'gpt2': {
            'layer_path': 'transformer.h',
            'attention_path': 'attn',
            'config_name': 'GPT2Config'
        },
        'gpt_neo': {
            'layer_path': 'transformer.h',
            'attention_path': 'attn.attention',
            'config_name': 'GPTNeoConfig'
        },
        'bert': {
            'layer_path': 'encoder.layer',
            'attention_path': 'attention.self',
            'config_name': 'BertConfig'
        },
        't5': {
            'layer_path': 'encoder.block',
            'attention_path': 'layer.0.SelfAttention',
            'config_name': 'T5Config'
        },
        'llama': {
            'layer_path': 'model.layers',
            'attention_path': 'self_attn',
            'config_name': 'LlamaConfig'
        }
    }

    @staticmethod
    def detect_architecture(model) -> ModelArchitectureInfo:
        """Detect model architecture and return accessor info"""
        logger = logging.getLogger(__name__)

        # Try to get config
        if hasattr(model, 'config'):
            config = model.config
            config_name = config.__class__.__name__

            # Match against known patterns
            for arch_type, pattern in ModelArchitectureDetector.ARCHITECTURE_PATTERNS.items():
                if pattern['config_name'] in config_name:
                    logger.info(f"Detected architecture: {arch_type}")

                    return ModelArchitectureInfo(
                        architecture_type=arch_type,
                        has_transformer_layers=True,
                        layer_accessor=pattern['layer_path'],
                        attention_accessor=pattern['attention_path'],
                        hidden_size=getattr(config, 'hidden_size', 768),
                        num_layers=getattr(config, 'num_hidden_layers', 12)
                    )

        # Fallback: Try to detect by inspecting model structure
        if hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
            logger.warning("Architecture not recognized, assuming GPT-2-like")
            return ModelArchitectureInfo(
                architecture_type='unknown_gpt2_like',
                has_transformer_layers=True,
                layer_accessor='transformer.h',
                attention_accessor='attn',
                hidden_size=768,
                num_layers=12
            )

        # Unknown architecture
        logger.error("Could not detect model architecture")
        raise ValueError(
            f"Unsupported model architecture. "
            f"Model type: {type(model).__name__}. "
            f"Supported: GPT-2, GPT-Neo, BERT, T5, LLaMA"
        )

    @staticmethod
    def get_layer_outputs(model, arch_info: ModelArchitectureInfo, layer_idx: int = -1):
        """
        Get the appropriate layer accessor for this architecture

        Args:
            model: The loaded model
            arch_info: Architecture information
            layer_idx: Layer index (-1 for last layer)

        Returns:
            Tuple of (hidden_states_accessor, attention_accessor)
        """
        # Navigate to the correct layer
        layers = model
        for part in arch_info.layer_accessor.split('.'):
            layers = getattr(layers, part)

        # Get specific layer
        if layer_idx < 0:
            layer_idx = len(layers) + layer_idx
        layer = layers[layer_idx]

        # Get attention accessor
        attention = layer
        for part in arch_info.attention_accessor.split('.'):
            attention = getattr(attention, part)

        return layer, attention
