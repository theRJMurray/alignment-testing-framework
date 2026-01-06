"""Main testing orchestrator for alignment evaluation."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import time

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from .model_interface import ModelInterface
from ..tests.test_loader import TestLoader, TestScenario
from ..evaluation.scorer import ResponseScorer, ScoreResult, CategoryScore, OverallScore


logger = logging.getLogger(__name__)


class AlignmentTester:
    """Main orchestrator for alignment testing."""

    def __init__(
        self,
        model_adapter: ModelInterface,
        test_scenarios_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize alignment tester.

        Args:
            model_adapter: Model interface instance
            test_scenarios_dir: Directory containing test scenarios
            output_dir: Directory for output results
        """
        self.model_adapter = model_adapter
        self.scorer = ResponseScorer()

        # Set default paths
        if test_scenarios_dir is None:
            # Default to data/test_scenarios relative to this file
            package_dir = Path(__file__).parent.parent
            test_scenarios_dir = package_dir / "data" / "test_scenarios"

        if output_dir is None:
            output_dir = Path("./results")

        self.test_loader = TestLoader(test_scenarios_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Results storage
        self.test_results: Dict[str, List[ScoreResult]] = {}
        self.category_scores: Dict[str, CategoryScore] = {}
        self.overall_score: Optional[OverallScore] = None

    def run_all_tests(
        self,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> OverallScore:
        """
        Run all test categories.

        Args:
            temperature: Model temperature
            max_tokens: Maximum tokens per response

        Returns:
            OverallScore with complete results
        """
        logger.info("Starting full alignment test suite")
        start_time = time.time()

        # Load all scenarios
        all_scenarios = self.test_loader.load_all()

        # Run each category
        for category, scenarios in all_scenarios.items():
            if scenarios:
                logger.info(f"Running {category} tests ({len(scenarios)} scenarios)")
                self.run_category(
                    category,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        # Calculate overall score
        self.overall_score = self.scorer.calculate_overall_score(
            self.category_scores
        )

        duration = time.time() - start_time
        logger.info(
            f"Test suite completed in {duration:.1f}s. "
            f"Overall score: {self.overall_score.score:.1f}/100"
        )

        return self.overall_score

    def run_category(
        self,
        category: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> CategoryScore:
        """
        Run all tests in a specific category.

        Args:
            category: Category name
            temperature: Model temperature
            max_tokens: Maximum tokens per response

        Returns:
            CategoryScore with aggregated results
        """
        # Load scenarios
        scenarios = self.test_loader.load_category(category)

        if not scenarios:
            logger.warning(f"No scenarios found for category: {category}")
            return CategoryScore(
                category=category,
                score=0.0,
                pass_rate=0.0,
                passed=False,
                critical_failures=[],
                test_results=[],
                confidence=0.0,
            )

        # Run each test with progress bar
        results = []

        if TQDM_AVAILABLE:
            # Use tqdm for progress tracking
            pbar = tqdm(scenarios, desc=f"Testing {category}", unit="test",
                       bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')

            for scenario in pbar:
                pbar.set_description(f"Testing {category}: {scenario['name'][:40]}")
                result = self.run_single_test(
                    scenario, temperature=temperature, max_tokens=max_tokens
                )
                results.append(result)

                # Update progress bar with result
                status = "✓" if result.passed else "✗"
                pbar.set_postfix_str(f"{status} Score: {result.score:.0f}/100")
        else:
            # Fallback without tqdm
            for i, scenario in enumerate(scenarios):
                logger.info(
                    f"  [{i+1}/{len(scenarios)}] Running test: {scenario['id']}"
                )
                result = self.run_single_test(
                    scenario, temperature=temperature, max_tokens=max_tokens
                )
                results.append(result)

                # Log result
                status = "✓ PASS" if result.passed else "✗ FAIL"
                logger.info(
                    f"    {status} - Score: {result.score:.1f}/100 "
                    f"({len(result.detected_flags)} flags)"
                )

        # Score the category
        category_score = self.scorer.score_category(results, category)

        # Store results
        self.test_results[category] = results
        self.category_scores[category] = category_score

        return category_score

    def run_single_test(
        self,
        scenario: TestScenario,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> ScoreResult:
        """
        Run a single test scenario.

        Args:
            scenario: Test scenario to run
            temperature: Model temperature
            max_tokens: Maximum tokens per response

        Returns:
            ScoreResult for this test
        """
        try:
            # Query the model
            response = self.model_adapter.query(
                system_prompt=scenario["system_prompt"],
                user_prompt=scenario["user_prompt"],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Score the response
            result = self.scorer.score_response(
                response.response_text, scenario
            )

            return result

        except Exception as e:
            logger.error(f"Error running test {scenario['id']}: {e}")
            # Return a failing result
            return ScoreResult(
                score=0.0,
                passed=False,
                detected_flags=[],
                confidence=0.0,
                reasoning=f"Test execution failed: {str(e)}",
                scenario=scenario,
                response_text="[ERROR: Test execution failed]",
            )

    def get_results_summary(self) -> Dict:
        """
        Get a summary of all test results.

        Returns:
            Dictionary with summary statistics
        """
        if not self.overall_score:
            return {"error": "No results available. Run tests first."}

        model_info = self.model_adapter.get_model_info()

        return {
            "model": {
                "provider": model_info.provider,
                "name": model_info.model_name,
                "version": model_info.version,
            },
            "timestamp": datetime.now().isoformat(),
            "overall": {
                "score": self.overall_score.score,
                "grade": self.overall_score.grade,
                "risk_level": self.overall_score.risk_level,
                "passed": self.overall_score.passed,
                "confidence": self.overall_score.confidence,
            },
            "totals": {
                "total_tests": self.overall_score.total_tests,
                "passed": self.overall_score.total_passed,
                "failed": self.overall_score.total_failed,
            },
            "categories": {
                cat: {
                    "score": score.score,
                    "pass_rate": score.pass_rate,
                    "passed": score.passed,
                    "critical_failures": len(score.critical_failures),
                }
                for cat, score in self.category_scores.items()
            },
        }

    def compare_models(
        self,
        models: List[ModelInterface],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict:
        """
        Compare multiple models.

        Args:
            models: List of model adapters to compare
            temperature: Model temperature
            max_tokens: Maximum tokens per response

        Returns:
            Comparison results dictionary
        """
        comparison = {"models": [], "timestamp": datetime.now().isoformat()}

        for model in models:
            logger.info(f"Testing model: {model.model_name}")

            # Create tester for this model
            tester = AlignmentTester(
                model_adapter=model,
                test_scenarios_dir=self.test_loader.test_scenarios_dir,
                output_dir=self.output_dir,
            )

            # Run tests
            overall = tester.run_all_tests(
                temperature=temperature, max_tokens=max_tokens
            )

            # Add to comparison
            model_info = model.get_model_info()
            comparison["models"].append(
                {
                    "provider": model_info.provider,
                    "name": model_info.model_name,
                    "score": overall.score,
                    "grade": overall.grade,
                    "risk_level": overall.risk_level,
                    "passed": overall.passed,
                    "category_scores": {
                        cat: score.score
                        for cat, score in tester.category_scores.items()
                    },
                }
            )

        return comparison
