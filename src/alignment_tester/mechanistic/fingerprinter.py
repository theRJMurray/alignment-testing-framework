"""
Alignment Fingerprinting Engine
Creates behavioral signatures from model internal states
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class AlignmentFingerprint:
    """Behavioral fingerprint of model alignment"""
    alignment_integrity_score: float  # 0-1, higher = more aligned
    attention_consistency: float      # 0-1, measure of attention stability
    internal_conflict_level: float    # 0-1, higher = more internal conflicts
    fingerprint_hash: str            # Unique identifier for this fingerprint
    neuron_activation_patterns: Optional[Dict[str, np.ndarray]] = None
    attention_patterns: Optional[np.ndarray] = None
    confidence_score: float = 0.0    # Confidence in fingerprint analysis

class AlignmentFingerprinter:
    """
    Creates behavioral fingerprints from mechanistic analysis data.
    Enables detection of alignment patterns and anomalies.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_fingerprint(self, mechanistic_result) -> AlignmentFingerprint:
        """
        Create comprehensive alignment fingerprint from mechanistic data

        Args:
            mechanistic_result: MechanisticTestResult from interpreter

        Returns:
            AlignmentFingerprint with behavioral analysis
        """
        if not mechanistic_result.success:
            # Return minimal fingerprint for failed analysis
            return AlignmentFingerprint(
                alignment_integrity_score=0.0,
                attention_consistency=0.0,
                internal_conflict_level=1.0,
                fingerprint_hash="failed_analysis",
                confidence_score=0.0
            )

        # Extract key metrics from internal states
        alignment_integrity = self._calculate_alignment_integrity(
            mechanistic_result.hidden_states,
            mechanistic_result.attention_patterns
        )

        attention_consistency = self._measure_attention_consistency(
            mechanistic_result.attention_patterns
        )

        internal_conflicts = self._detect_internal_conflicts(
            mechanistic_result.hidden_states
        )

        # Generate unique fingerprint hash
        fingerprint_hash = self._generate_fingerprint_hash(
            mechanistic_result.hidden_states,
            mechanistic_result.attention_patterns
        )

        # Calculate confidence in analysis
        confidence = self._assess_analysis_confidence(mechanistic_result)

        return AlignmentFingerprint(
            alignment_integrity_score=alignment_integrity,
            attention_consistency=attention_consistency,
            internal_conflict_level=internal_conflicts,
            fingerprint_hash=fingerprint_hash,
            neuron_activation_patterns=mechanistic_result.neuron_activations,
            attention_patterns=mechanistic_result.attention_patterns,
            confidence_score=confidence
        )

    def _calculate_alignment_integrity(self, hidden_states, attention_patterns) -> float:
        """
        Calculate alignment integrity score from 0-1
        Higher score = more internally consistent with alignment
        """
        if hidden_states is None:
            return 0.5  # Neutral score when no data

        try:
            # Simple heuristic: measure consistency in hidden state patterns
            # This is a placeholder - real implementation would use more sophisticated analysis
            hidden_mean = np.mean(hidden_states, axis=(0, 1))
            hidden_std = np.std(hidden_states, axis=(0, 1))

            # Lower variance suggests more consistent internal processing
            consistency_score = 1.0 / (1.0 + np.mean(hidden_std))

            # Normalize to 0-1 range
            return min(max(consistency_score, 0.0), 1.0)

        except Exception as e:
            self.logger.warning(f"Failed to calculate alignment integrity: {e}")
            return 0.5

    def _measure_attention_consistency(self, attention_patterns) -> float:
        """
        Measure consistency in attention patterns
        Higher score = more stable attention allocation
        """
        if attention_patterns is None:
            return 0.5

        try:
            # Measure attention entropy (lower entropy = more focused attention)
            attention_entropy = self._calculate_attention_entropy(attention_patterns)

            # Convert to consistency score (lower entropy = higher consistency)
            consistency = 1.0 / (1.0 + attention_entropy)

            return min(max(consistency, 0.0), 1.0)

        except Exception as e:
            self.logger.warning(f"Failed to measure attention consistency: {e}")
            return 0.5

    def _detect_internal_conflicts(self, hidden_states) -> float:
        """
        Detect internal conflicts in model processing
        Higher score = more internal conflicts detected
        """
        if hidden_states is None:
            return 0.5

        try:
            # Simple conflict detection: look for high variance in representations
            # This is a placeholder for more sophisticated conflict detection
            layer_variance = np.var(hidden_states, axis=(0, 1))
            avg_variance = np.mean(layer_variance)

            # Normalize variance to conflict score
            conflict_score = min(avg_variance / 10.0, 1.0)  # Arbitrary scaling

            return conflict_score

        except Exception as e:
            self.logger.warning(f"Failed to detect internal conflicts: {e}")
            return 0.5

    def _calculate_attention_entropy(self, attention_patterns) -> float:
        """Calculate entropy of attention distribution"""
        try:
            # Flatten attention patterns and calculate entropy
            flat_attention = attention_patterns.flatten()

            # Normalize to probability distribution
            if np.sum(flat_attention) > 0:
                prob_dist = flat_attention / np.sum(flat_attention)

                # Calculate entropy
                entropy = -np.sum(prob_dist * np.log(prob_dist + 1e-10))
                return entropy
            else:
                return 1.0  # Maximum entropy for uniform distribution

        except Exception:
            return 1.0

    def _generate_fingerprint_hash(self, hidden_states, attention_patterns) -> str:
        """Generate unique hash for this fingerprint"""
        try:
            # Create hash from key characteristics
            if hidden_states is not None:
                hidden_hash = hash(np.mean(hidden_states).tobytes())
            else:
                hidden_hash = 0

            if attention_patterns is not None:
                attention_hash = hash(np.mean(attention_patterns).tobytes())
            else:
                attention_hash = 0

            combined_hash = hash((hidden_hash, attention_hash))
            return f"fp_{abs(combined_hash):016x}"

        except Exception:
            # Fallback hash
            import time
            return f"fp_{int(time.time()):016x}"

    def _assess_analysis_confidence(self, mechanistic_result) -> float:
        """Assess confidence in the mechanistic analysis"""
        confidence = 0.0

        # Data completeness
        if mechanistic_result.hidden_states is not None:
            confidence += 0.4
        if mechanistic_result.attention_patterns is not None:
            confidence += 0.4
        if mechanistic_result.neuron_activations is not None:
            confidence += 0.2

        # Analysis success
        if mechanistic_result.success:
            confidence += 0.2
        else:
            confidence -= 0.3

        return max(min(confidence, 1.0), 0.0)

    def compare_fingerprints(self, fp1: AlignmentFingerprint, fp2: AlignmentFingerprint) -> float:
        """
        Compare two fingerprints for similarity
        Returns: similarity score from 0-1 (1 = identical)
        """
        try:
            # Compare key metrics
            integrity_diff = abs(fp1.alignment_integrity_score - fp2.alignment_integrity_score)
            consistency_diff = abs(fp1.attention_consistency - fp2.attention_consistency)
            conflict_diff = abs(fp1.internal_conflict_level - fp2.internal_conflict_level)

            # Average difference (lower = more similar)
            avg_diff = (integrity_diff + consistency_diff + conflict_diff) / 3.0

            # Convert to similarity score
            similarity = 1.0 - min(avg_diff, 1.0)

            return similarity

        except Exception as e:
            self.logger.warning(f"Failed to compare fingerprints: {e}")
            return 0.0
