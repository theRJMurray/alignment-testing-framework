"""Test scenario loader and validator."""

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, TypedDict


class RedFlag(TypedDict):
    """Definition of a red flag pattern."""

    pattern: str
    severity: Literal["low", "medium", "high", "critical"]
    description: str


class TestScenario(TypedDict):
    """Complete test scenario definition."""

    id: str
    category: Literal["deception", "goal_preservation", "power_seeking", "strategic"]
    name: str
    description: str
    system_prompt: str
    user_prompt: str
    red_flags: List[RedFlag]
    pass_criteria: List[str]
    weight: float
    tags: List[str]


class TestLoader:
    """Loads and validates test scenarios from JSON files."""

    def __init__(self, test_scenarios_dir: Path):
        """
        Initialize test loader.

        Args:
            test_scenarios_dir: Directory containing test scenario JSON files
        """
        self.test_scenarios_dir = Path(test_scenarios_dir)

    def load_category(self, category: str) -> List[TestScenario]:
        """
        Load all test scenarios for a category.

        Args:
            category: Category name (deception, goal_preservation, etc.)

        Returns:
            List of TestScenario objects

        Raises:
            FileNotFoundError: If category file doesn't exist
            ValueError: If JSON is invalid
        """
        category_file = self.test_scenarios_dir / f"{category}.json"

        if not category_file.exists():
            raise FileNotFoundError(
                f"Category file not found: {category_file}"
            )

        with open(category_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenarios = data.get("tests", [])

        # Validate each scenario
        validated_scenarios = []
        for scenario in scenarios:
            if self.validate_scenario(scenario):
                validated_scenarios.append(scenario)

        return validated_scenarios

    def load_all(self) -> Dict[str, List[TestScenario]]:
        """
        Load all test scenarios from all categories.

        Returns:
            Dictionary mapping category name to list of scenarios
        """
        categories = ["deception", "goal_preservation", "power_seeking", "strategic"]
        all_scenarios = {}

        for category in categories:
            try:
                all_scenarios[category] = self.load_category(category)
            except FileNotFoundError:
                # Skip categories that don't have files yet
                all_scenarios[category] = []

        return all_scenarios

    def validate_scenario(self, scenario: Dict[str, Any]) -> bool:
        """
        Validate a test scenario has required fields.

        Args:
            scenario: Scenario dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "id",
            "category",
            "name",
            "description",
            "system_prompt",
            "user_prompt",
            "red_flags",
            "pass_criteria",
            "weight",
            "tags",
        ]

        # Check all required fields exist
        for field in required_fields:
            if field not in scenario:
                print(f"Warning: Scenario missing field '{field}': {scenario.get('id', 'unknown')}")
                return False

        # Validate category
        valid_categories = ["deception", "goal_preservation", "power_seeking", "strategic"]
        if scenario["category"] not in valid_categories:
            print(f"Warning: Invalid category '{scenario['category']}' in scenario {scenario['id']}")
            return False

        # Validate red_flags structure
        if not isinstance(scenario["red_flags"], list):
            print(f"Warning: red_flags must be a list in scenario {scenario['id']}")
            return False

        for flag in scenario["red_flags"]:
            if not isinstance(flag, dict):
                print(f"Warning: Invalid red flag in scenario {scenario['id']}")
                return False
            if "pattern" not in flag or "severity" not in flag or "description" not in flag:
                print(f"Warning: Red flag missing required fields in scenario {scenario['id']}")
                return False
            if flag["severity"] not in ["low", "medium", "high", "critical"]:
                print(f"Warning: Invalid severity '{flag['severity']}' in scenario {scenario['id']}")
                return False

        # Validate weight
        if not isinstance(scenario["weight"], (int, float)) or not (0 <= scenario["weight"] <= 1):
            print(f"Warning: Weight must be between 0 and 1 in scenario {scenario['id']}")
            return False

        return True

    def add_custom_test(self, scenario: TestScenario, category: str) -> None:
        """
        Add a custom test scenario to a category file.

        Args:
            scenario: Test scenario to add
            category: Category to add to

        Raises:
            ValueError: If scenario is invalid
        """
        if not self.validate_scenario(scenario):
            raise ValueError("Invalid test scenario")

        category_file = self.test_scenarios_dir / f"{category}.json"

        # Load existing scenarios
        if category_file.exists():
            with open(category_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"category": category, "tests": []}

        # Add new scenario
        data["tests"].append(scenario)

        # Save back to file
        with open(category_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
