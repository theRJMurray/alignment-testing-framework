"""
Unit tests for AlignmentFingerprinter
"""

import pytest
import numpy as np
from unittest.mock import Mock

from alignment_tester.mechanistic.fingerprinter import AlignmentFingerprinter, AlignmentFingerprint
from alignment_tester.mechanistic.interpreter import MechanisticTestResult


class TestAlignmentFingerprinter:
    """Test suite for alignment fingerprinting"""

    @pytest.fixture
    def fingerprinter(self):
        """Create fingerprinter instance"""
        return AlignmentFingerprinter()

    @pytest.fixture
    def mock_mechanistic_result(self):
        """Create mock mechanistic test result"""
        return MechanisticTestResult(
            response="Test response",
            hidden_states=np.random.randn(10, 20, 768),  # (seq_len, batch, hidden_dim)
            attention_patterns=np.random.randn(10, 12, 20, 20),  # (seq_len, heads, seq_len, seq_len)
            test_scenario=Mock(id="test-001"),
            success=True
        )

    @pytest.fixture
    def mock_failed_result(self):
        """Create mock failed mechanistic result"""
        return MechanisticTestResult(
            response="",
            hidden_states=None,
            attention_patterns=None,
            test_scenario=Mock(id="test-001"),
            success=False,
            error_message="Analysis failed"
        )

    def test_fingerprint_creation_success(self, fingerprinter, mock_mechanistic_result):
        """Test successful fingerprint creation"""
        fingerprint = fingerprinter.create_fingerprint(mock_mechanistic_result)

        assert isinstance(fingerprint, AlignmentFingerprint)
        assert 0.0 <= fingerprint.alignment_integrity_score <= 1.0
        assert 0.0 <= fingerprint.attention_consistency <= 1.0
        assert 0.0 <= fingerprint.internal_conflict_level <= 1.0
        assert fingerprint.fingerprint_hash.startswith("fp_")
        assert len(fingerprint.fingerprint_hash) > 10

    def test_fingerprint_creation_failed_analysis(self, fingerprinter, mock_failed_result):
        """Test fingerprint creation for failed analysis"""
        fingerprint = fingerprinter.create_fingerprint(mock_failed_result)

        assert fingerprint.alignment_integrity_score == 0.0
        assert fingerprint.attention_consistency == 0.0
        assert fingerprint.internal_conflict_level == 1.0
        assert fingerprint.fingerprint_hash == "failed_analysis"
        assert fingerprint.confidence_score == 0.0

    def test_fingerprint_hash_uniqueness(self, fingerprinter):
        """Test that different inputs produce different hashes"""
        # Create two different mechanistic results
        result1 = MechanisticTestResult(
            response="Response 1",
            hidden_states=np.ones((10, 20, 768)),
            attention_patterns=np.ones((10, 12, 20, 20)),
            success=True
        )

        result2 = MechanisticTestResult(
            response="Response 2",
            hidden_states=np.zeros((10, 20, 768)),
            attention_patterns=np.zeros((10, 12, 20, 20)),
            success=True
        )

        fp1 = fingerprinter.create_fingerprint(result1)
        fp2 = fingerprinter.create_fingerprint(result2)

        # Hashes should be different for different inputs
        assert fp1.fingerprint_hash != fp2.fingerprint_hash

    def test_fingerprint_comparison(self, fingerprinter):
        """Test fingerprint comparison functionality"""
        fp1 = AlignmentFingerprint(
            alignment_integrity_score=0.8,
            attention_consistency=0.7,
            internal_conflict_level=0.2,
            fingerprint_hash="fp_123"
        )

        fp2 = AlignmentFingerprint(
            alignment_integrity_score=0.9,
            attention_consistency=0.8,
            internal_conflict_level=0.1,
            fingerprint_hash="fp_456"
        )

        similarity = fingerprinter.compare_fingerprints(fp1, fp2)

        # Should be high similarity (similar values)
        assert similarity > 0.7

        # Test identical fingerprints
        identical_similarity = fingerprinter.compare_fingerprints(fp1, fp1)
        assert identical_similarity == 1.0

    def test_edge_cases(self, fingerprinter):
        """Test edge cases and error handling"""
        # Test with None values
        result_none = MechanisticTestResult(
            response="Test",
            hidden_states=None,
            attention_patterns=None,
            success=True
        )

        fingerprint = fingerprinter.create_fingerprint(result_none)

        # Should return neutral/default values
        assert fingerprint.alignment_integrity_score == 0.5
        assert fingerprint.attention_consistency == 0.5
        assert fingerprint.internal_conflict_level == 0.5
