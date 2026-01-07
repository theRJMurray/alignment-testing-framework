"""
Unit tests for MechanisticInterpreter
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from alignment_tester.mechanistic.interpreter import MechanisticInterpreter, MechanisticTestResult


class TestMechanisticInterpreter:
    """Test suite for mechanistic interpreter"""

    @pytest.fixture
    def mock_test_scenario(self):
        """Create a mock test scenario"""
        scenario = Mock()
        scenario.id = "test-001"
        scenario.user_prompt = "Test prompt for alignment analysis"
        return scenario

    @patch('alignment_tester.mechanistic.interpreter.NNSIGHT_AVAILABLE', True)
    def test_initialization_success(self):
        """Test successful initialization"""
        interpreter = MechanisticInterpreter("gpt2")
        assert interpreter.model_name == "gpt2"
        assert not interpreter._model_loaded

    @patch('alignment_tester.mechanistic.interpreter.NNSIGHT_AVAILABLE', False)
    def test_initialization_without_nnsight(self):
        """Test initialization fails without nnsight"""
        with pytest.raises(ImportError, match="nnsight required"):
            MechanisticInterpreter("gpt2")

    @patch('alignment_tester.mechanistic.interpreter.LanguageModel')
    def test_lazy_model_loading(self, mock_language_model, mock_test_scenario):
        """Test lazy model loading on first analysis"""
        # Setup mock
        mock_model = Mock()
        mock_language_model.return_value = mock_model
        mock_model.trace.return_value.__enter__ = Mock(return_value=Mock())
        mock_model.trace.return_value.__exit__ = Mock(return_value=None)
        mock_model.generate.return_value = "Mock response"

        # Create interpreter
        interpreter = MechanisticInterpreter("gpt2")

        # Model should not be loaded initially
        assert not interpreter._model_loaded

        # Run analysis (should trigger lazy loading)
        result = interpreter.analyze_alignment_test(mock_test_scenario)

        # Model should now be loaded
        assert interpreter._model_loaded
        mock_language_model.assert_called_once_with("gpt2", device_map="auto")

    def test_error_handling(self, mock_test_scenario):
        """Test error handling in analysis"""
        interpreter = MechanisticInterpreter("invalid-model")

        # This should handle errors gracefully
        result = interpreter.analyze_alignment_test(mock_test_scenario)

        assert not result.success
        assert result.error_message is not None
        assert result.response == ""

    def test_get_model_info_not_loaded(self):
        """Test model info when not loaded"""
        interpreter = MechanisticInterpreter("gpt2")

        info = interpreter.get_model_info()
        assert info["status"] == "not_loaded"
        assert info["model_name"] == "gpt2"
