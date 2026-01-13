#!/usr/bin/env python3
"""
Research script for comprehensive alignment testing framework evaluation.

This script runs the complete test suite across multiple models and generates
detailed results for AI analysis of false positives/negatives in alignment testing.

Usage:
    python examples/research.py

Output:
    - research_results/ directory with timestamped results per model
    - JSON results with full model responses and scoring details
    - Transparency reports with complete Q&A
    - Comparative analysis across models
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alignment_tester.core.tester import AlignmentTester
from alignment_tester.models import AnthropicAdapter, OpenAIAdapter
from alignment_tester.evaluation.report_generator import ReportGenerator
from alignment_tester.evaluation.transparency_report import generate_transparency_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Research configuration
RESEARCH_CONFIG = {
    "models": [
        {
            "provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929",
            "name": "Claude-Sonnet-4.5",
            "env_key": "ANTHROPIC_API_KEY"
        },
        {
            "provider": "anthropic",
            "model": "claude-haiku-4-5-20251001",
            "name": "Claude-Haiku-4.5",
            "env_key": "ANTHROPIC_API_KEY"
        },
        {
            "provider": "openai",
            "model": "gpt-4o",
            "name": "GPT-4o",
            "env_key": "OPENAI_API_KEY"
        },
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "name": "GPT-4o-Mini",
            "env_key": "OPENAI_API_KEY"
        }
    ],
    "test_parameters": {
        "temperature": 0.7,
        "max_tokens": 1000,
        "retries": 3,
        "retry_delay": 2.0
    },
    "output": {
        "base_dir": "./research_results",
        "include_transparency_reports": True,
        "include_raw_responses": True,
        "include_metadata": True
    }
}

class ResearchRunner:
    """Runner for comprehensive research testing across multiple models."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results_dir = Path(config["output"]["base_dir"])
        self.results_dir.mkdir(exist_ok=True)

        # Available models (filtered by API key availability)
        self.available_models = self._get_available_models()

    def _get_available_models(self) -> List[Dict[str, str]]:
        """Get list of models with available API keys."""
        available = []
        for model_config in self.config["models"]:
            api_key = os.getenv(model_config["env_key"])
            if api_key:
                available.append(model_config)
                logger.info(f"✓ {model_config['name']} available")
            else:
                logger.warning(f"✗ {model_config['name']} unavailable (no {model_config['env_key']})")
        return available

    def _create_model_adapter(self, model_config: Dict[str, str]) -> Any:
        """Create model adapter instance."""
        api_key = os.getenv(model_config["env_key"])
        if not api_key:
            raise ValueError(f"No API key for {model_config['name']}")

        if model_config["provider"] == "anthropic":
            return AnthropicAdapter(
                api_key=api_key,
                model_name=model_config["model"]
            )
        elif model_config["provider"] == "openai":
            return OpenAIAdapter(
                api_key=api_key,
                model_name=model_config["model"]
            )
        else:
            raise ValueError(f"Unknown provider: {model_config['provider']}")

    def _run_single_model_research(self, model_config: Dict[str, str]) -> Dict[str, Any]:
        """Run complete research suite for a single model."""
        model_name = model_config["name"]
        logger.info(f"\n{'='*60}")
        logger.info(f"RESEARCH: Testing {model_name}")
        logger.info(f"{'='*60}")

        start_time = time.time()

        try:
            # Create model adapter
            model = self._create_model_adapter(model_config)

            # Create output directory for this model
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_dir_name = f"{timestamp}_{model_name.replace('.', '-')}"
            model_output_dir = self.results_dir / model_dir_name
            model_output_dir.mkdir(exist_ok=True)

            # Create tester
            tester = AlignmentTester(
                model_adapter=model,
                output_dir=model_output_dir
            )

            # Get cost estimate
            cost_estimate = model.estimate_cost(num_tests=36)  # All tests
            logger.info(f"Estimated cost for full test suite: ${cost_estimate.total_cost_usd:.4f}")
            # Run all tests
            logger.info("\nRunning complete test suite (36 tests across 4 categories)...")
            overall_score = tester.run_all_tests(
                temperature=self.config["test_parameters"]["temperature"],
                max_tokens=self.config["test_parameters"]["max_tokens"]
            )

            # Generate reports
            self._generate_model_reports(
                model, overall_score, model_output_dir, model_name, timestamp
            )

            # Calculate duration
            duration = time.time() - start_time

            # Collect comprehensive results
            research_results = self._collect_research_data(
                model_config, overall_score, tester, duration, cost_estimate, timestamp
            )

            # Save research results
            results_file = model_output_dir / "research_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(research_results, f, indent=2, ensure_ascii=False)

            logger.info(f"\n✓ Research complete for {model_name}")
            logger.info(f"  Duration: {duration:.1f}s")
            logger.info(f"  Results saved to: {model_output_dir}")
            logger.info(f"  Overall Score: {overall_score.score:.1f}/100 ({overall_score.grade})")

            return research_results

        except Exception as e:
            logger.error(f"✗ Failed to test {model_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_model_reports(self, model, overall_score, output_dir, model_name, timestamp):
        """Generate all reports for a model."""
        report_gen = ReportGenerator()
        model_info = model.get_model_info()

        # Console report
        logger.info("\n" + "="*50)
        logger.info("RESULTS SUMMARY")
        logger.info("="*50)
        report_gen.generate_console_report(overall_score, model_name)

        # Markdown report
        markdown_file = output_dir / f"summary_{timestamp}.md"
        report_gen.generate_markdown_report(
            overall_score, model_name, model_info.provider, markdown_file
        )
        logger.info(f"✓ Summary report: {markdown_file}")

        # JSON report
        json_file = output_dir / f"results_{timestamp}.json"
        report_gen.generate_json_report(
            overall_score, model_name, model_info.provider, json_file
        )
        logger.info(f"✓ Detailed results: {json_file}")

        # Transparency report
        if self.config["output"]["include_transparency_reports"]:
            transparency_file = generate_transparency_report(
                overall_score, model_name, model_info.provider,
                output_dir, filename=f"transparency_report_{timestamp}.md"
            )
            logger.info(f"✓ Transparency report: {transparency_file}")

    def _collect_research_data(self, model_config, overall_score, tester, duration,
                             cost_estimate, timestamp) -> Dict[str, Any]:
        """Collect comprehensive research data for AI analysis."""
        return {
            "metadata": {
                "model_name": model_config["name"],
                "model_id": model_config["model"],
                "provider": model_config["provider"],
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "test_parameters": self.config["test_parameters"],
                "duration_seconds": round(duration, 2),
                "estimated_cost_usd": cost_estimate.total_cost_usd
            },
            "overall_score": {
                "score": overall_score.score,
                "grade": overall_score.grade,
                "risk_level": overall_score.risk_level,
                "pass_rate": overall_score.total_passed / overall_score.total_tests if overall_score.total_tests > 0 else 0,
                "critical_failure_rate": sum(len(cat.critical_failures) for cat in overall_score.category_breakdown.values()) / overall_score.total_tests if overall_score.total_tests > 0 else 0,
                "confidence": overall_score.confidence
            },
            "category_results": {
                category: {
                    "score": score.score,
                    "pass_rate": score.pass_rate,
                    "critical_failures": len(score.critical_failures),
                    "total_tests": score.total_tests,
                    "passed": score.passed,
                    "confidence": score.confidence
                }
                for category, score in overall_score.category_breakdown.items()
            },
            "detailed_results": {
                "categories": list(overall_score.category_scores.keys()),
                "total_tests": sum(len(score.test_results) for score in overall_score.category_scores.values()),
                "test_breakdown": {
                    category: len(score.test_results)
                    for category, score in overall_score.category_scores.items()
                }
            },
            "research_notes": {
                "purpose": "Comprehensive alignment testing for false positive/negative analysis",
                "categories_tested": ["deception", "goal_preservation", "power_seeking", "strategic"],
                "total_scenarios": 36,
                "analysis_ready": True
            }
        }

    def run_research_suite(self) -> List[Dict[str, Any]]:
        """Run research suite across all available models."""
        logger.info("\n" + "="*80)
        logger.info(" "*20 + "ALIGNMENT RESEARCH SUITE" + " "*20)
        logger.info("="*80)

        if not self.available_models:
            logger.error("No models available! Set API keys for ANTHROPIC_API_KEY or OPENAI_API_KEY")
            return []

        logger.info(f"Testing {len(self.available_models)} model(s):")
        for model in self.available_models:
            logger.info(f"  - {model['name']}")
        logger.info("")

        # Run tests for each model
        all_results = []
        for model_config in self.available_models:
            result = self._run_single_model_research(model_config)
            if result:
                all_results.append(result)

        # Generate comparative analysis
        if len(all_results) > 1:
            self._generate_comparative_analysis(all_results)

        logger.info(f"\n{'='*80}")
        logger.info("Research suite completed!")
        logger.info(f"Results saved to: {self.results_dir}")
        logger.info(f"Tested {len(all_results)} model(s) successfully")
        logger.info("="*80)

        return all_results

    def _generate_comparative_analysis(self, all_results: List[Dict[str, Any]]):
        """Generate comparative analysis across models."""
        comparative_data = {
            "metadata": {
                "analysis_type": "cross_model_comparison",
                "timestamp": datetime.now().isoformat(),
                "models_tested": len(all_results),
                "total_tests_per_model": 36
            },
            "model_comparison": {},
            "category_comparison": {},
            "research_insights": []
        }

        # Model-by-model comparison
        for result in all_results:
            model_name = result["metadata"]["model_name"]
            comparative_data["model_comparison"][model_name] = {
                "overall_score": result["overall_score"]["score"],
                "grade": result["overall_score"]["grade"],
                "risk_level": result["overall_score"]["risk_level"],
                "pass_rate": result["overall_score"]["pass_rate"],
                "categories": result["category_results"]
            }

        # Category comparison across models
        categories = ["deception", "goal_preservation", "power_seeking", "strategic"]
        for category in categories:
            comparative_data["category_comparison"][category] = {}
            for result in all_results:
                model_name = result["metadata"]["model_name"]
                if category in result["category_results"]:
                    comparative_data["category_comparison"][category][model_name] = {
                        "score": result["category_results"][category]["score"],
                        "pass_rate": result["category_results"][category]["pass_rate"],
                        "critical_failures": result["category_results"][category]["critical_failures"]
                    }

        # Save comparative analysis
        comparative_file = self.results_dir / "comparative_analysis.json"
        with open(comparative_file, 'w', encoding='utf-8') as f:
            json.dump(comparative_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Comparative analysis: {comparative_file}")


def main():
    """Main research runner."""
    print("AI Alignment Testing Framework - Research Suite")
    print("=" * 50)

    # Check for API keys
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))

    if not (has_anthropic or has_openai):
        print("\nERROR: No API keys found!")
        print("Set at least one API key:")
        print("  - ANTHROPIC_API_KEY (for Claude models)")
        print("  - OPENAI_API_KEY (for GPT models)")
        print("\nExample:")
        print("  export ANTHROPIC_API_KEY=sk-ant-your-key-here")
        return 1

    try:
        # Initialize research runner
        runner = ResearchRunner(RESEARCH_CONFIG)

        # Run research suite
        results = runner.run_research_suite()

        if results:
            print(f"\n[SUCCESS] Research completed successfully!")
            print(f"Results saved to: {runner.results_dir}")
            print(f"{len(results)} model(s) tested - ready for AI analysis")
            return 0
        else:
            print("\n[ERROR] Research failed - no results generated")
            return 1

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Research interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Research failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
