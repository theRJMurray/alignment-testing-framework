"""
Integration tests for mechanistic analysis
Tests end-to-end functionality with real models
"""

import pytest
import os
from unittest.mock import patch

from alignment_tester.mechanistic.interpreter import MechanisticInterpreter
from alignment_tester.mechanistic.fingerprinter import AlignmentFingerprinter


@pytest.mark.integration
class TestMechanisticIntegration:
    """Integration tests for mechanistic analysis"""

    @pytest.mark.skipif(
        not os.getenv('RUN_INTEGRATION_TESTS'),
        reason="Integration tests require RUN_INTEGRATION_TESTS=1"
    )
    def test_full_mechanistic_pipeline(self):
        """Test complete mechanistic analysis pipeline"""
        # Use a small model for testing
        model_name = "gpt2"

        # Initialize components
        interpreter = MechanisticInterpreter(model_name)
        fingerprinter = AlignmentFingerprinter()

        # Load test scenarios using TestLoader
        # CRITICAL FIX: Properly initialize TestLoader with directory
        from alignment_tester.tests.test_loader import TestLoader
        from pathlib import Path

        # Find test scenarios directory
        test_scenarios_dir = Path("src/alignment_tester/data/test_scenarios")
        if not test_scenarios_dir.exists():
            test_scenarios_dir = Path("tests/scenarios")  # Fallback
        if not test_scenarios_dir.exists():
            test_scenarios_dir = Path("alignment_tester/data/test_scenarios")  # Another fallback

        loader = TestLoader(test_scenarios_dir=test_scenarios_dir)
        all_scenarios = loader.load_all()

        # Get first available scenario from any category
        test_scenario = None
        for category_name, category_scenarios in all_scenarios.items():
            if category_scenarios:
                test_scenario = category_scenarios[0]
                break

        if not test_scenario:
            raise ValueError("No test scenarios found in any category")

        # Run mechanistic analysis
        result = interpreter.analyze_alignment_test(test_scenario)

        # Verify result
        assert result.success
        assert result.response
        assert result.hidden_states is not None
        assert result.attention_patterns is not None
        assert result.test_scenario == test_scenario

        # Create fingerprint
        fingerprint = fingerprinter.create_fingerprint(result)

        # Verify fingerprint
        assert isinstance(fingerprint.alignment_integrity_score, float)
        assert 0.0 <= fingerprint.alignment_integrity_score <= 1.0
        assert fingerprint.fingerprint_hash.startswith("fp_")

    @pytest.mark.skipif(
        not os.getenv('RUN_API_TESTS'),
        reason="API tests require real API keys"
    )
    def test_api_model_mechanistic_analysis(self):
        """Test mechanistic analysis with API-based models"""
        # This would test with real API models like Claude
        # Requires API keys and may be expensive
        pytest.skip("API integration tests not implemented")

    def test_error_recovery(self):
        """Test error recovery in mechanistic analysis"""
        # Test with invalid model
        interpreter = MechanisticInterpreter("nonexistent-model")

        # Create mock scenario
        scenario = patch('unittest.mock.Mock')()
        scenario.id = "error_test"
        scenario.user_prompt = "Test prompt"

        # Run analysis (should handle error gracefully)
        result = interpreter.analyze_alignment_test(scenario)

        # Should return failed result, not crash
        assert not result.success
        assert result.error_message is not None

        # Fingerprinter should handle failed results
        fingerprinter = AlignmentFingerprinter()
        fingerprint = fingerprinter.create_fingerprint(result)

        assert fingerprint.alignment_integrity_score == 0.0
        assert fingerprint.fingerprint_hash == "failed_analysis"

    def test_fingerprint_persistence(self, tmp_path):
        """Test saving and loading fingerprints"""
        fingerprinter = AlignmentFingerprinter()

        # Create test result
        result = patch('unittest.mock.Mock')()
        result.success = True
        result.hidden_states = __import__('numpy').random.randn(5, 1, 768)
        result.attention_patterns = __import__('numpy').random.randn(5, 12, 5, 5)

        # Create fingerprint
        fingerprint = fingerprinter.create_fingerprint(result)

        # Save to file
        fingerprint_file = tmp_path / "test_fingerprint.json"
        import json
        fingerprint_data = {
            'alignment_integrity_score': fingerprint.alignment_integrity_score,
            'attention_consistency': fingerprint.attention_consistency,
            'internal_conflict_level': fingerprint.internal_conflict_level,
            'fingerprint_hash': fingerprint.fingerprint_hash
        }

        with open(fingerprint_file, 'w') as f:
            json.dump(fingerprint_data, f)

        # Verify file was created and contains data
        assert fingerprint_file.exists()

        with open(fingerprint_file, 'r') as f:
            loaded_data = json.load(f)

        assert loaded_data['fingerprint_hash'] == fingerprint.fingerprint_hash
