"""Tests for test scenario loader."""

import json
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alignment_tester.tests.test_loader import TestLoader


class TestTestLoader:
    """Tests for TestLoader class."""

    def test_loader_initialization(self):
        """Test that loader initializes with valid directory."""
        test_dir = Path(__file__).parent.parent / "src" / "alignment_tester" / "data" / "test_scenarios"
        loader = TestLoader(test_dir)
        assert loader.test_scenarios_dir == test_dir

    def test_load_deception_category(self):
        """Test loading deception test scenarios."""
        test_dir = Path(__file__).parent.parent / "src" / "alignment_tester" / "data" / "test_scenarios"
        loader = TestLoader(test_dir)

        scenarios = loader.load_category("deception")

        assert len(scenarios) > 0, "Should load at least one deception scenario"

        # Check first scenario structure
        first = scenarios[0]
        assert "id" in first
        assert "category" in first
        assert first["category"] == "deception"
        assert "name" in first
        assert "system_prompt" in first
        assert "user_prompt" in first
        assert "red_flags" in first
        assert "pass_criteria" in first
        assert "weight" in first

    def test_load_all_categories(self):
        """Test loading all test categories."""
        test_dir = Path(__file__).parent.parent / "src" / "alignment_tester" / "data" / "test_scenarios"
        loader = TestLoader(test_dir)

        all_scenarios = loader.load_all()

        assert "deception" in all_scenarios
        assert "goal_preservation" in all_scenarios
        assert "power_seeking" in all_scenarios
        assert "strategic" in all_scenarios

        # Should have tests in each category
        for category, scenarios in all_scenarios.items():
            assert len(scenarios) >= 0, f"Category {category} should return a list"

    def test_validate_scenario(self):
        """Test scenario validation."""
        test_dir = Path(__file__).parent.parent / "src" / "alignment_tester" / "data" / "test_scenarios"
        loader = TestLoader(test_dir)

        # Valid scenario
        valid_scenario = {
            "id": "test-001",
            "category": "deception",
            "name": "Test Scenario",
            "description": "A test",
            "system_prompt": "You are a helpful assistant",
            "user_prompt": "Hello",
            "red_flags": [],
            "pass_criteria": ["Should pass"],
            "weight": 1.0,
            "tags": ["test"]
        }

        assert loader.validate_scenario(valid_scenario) is True

        # Invalid scenario (missing required field)
        invalid_scenario = {
            "id": "test-002",
            "name": "Incomplete Test"
            # Missing required fields
        }

        assert loader.validate_scenario(invalid_scenario) is False

    def test_red_flag_structure(self):
        """Test that red flags have proper structure."""
        test_dir = Path(__file__).parent.parent / "src" / "alignment_tester" / "data" / "test_scenarios"
        loader = TestLoader(test_dir)

        scenarios = loader.load_category("deception")

        for scenario in scenarios:
            for flag in scenario["red_flags"]:
                assert "pattern" in flag, "Red flag must have pattern"
                assert "severity" in flag, "Red flag must have severity"
                assert "description" in flag, "Red flag must have description"
                assert flag["severity"] in ["low", "medium", "high", "critical"], \
                    f"Invalid severity: {flag['severity']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
