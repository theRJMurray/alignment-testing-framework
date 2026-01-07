"""Transparency report generation with full Q&A details."""

from pathlib import Path
from typing import Dict
from datetime import datetime

from .scorer import OverallScore, ScoreResult


class TransparencyReportGenerator:
    """Generates detailed transparency reports showing full test interactions."""

    def generate_detailed_markdown(
        self,
        overall_score: OverallScore,
        model_name: str,
        provider: str,
        output_path: Path,
    ) -> None:
        """
        Generate detailed markdown report with full Q&A.

        Args:
            overall_score: Overall test results
            model_name: Name of the tested model
            provider: Provider name
            output_path: Path to save the report
        """
        lines = []

        # Header
        lines.append("# Detailed Alignment Test Report")
        lines.append(f"\n**Model:** {model_name}")
        lines.append(f"**Provider:** {provider}")
        lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Framework Version:** 0.1.0\n")

        # Executive Summary
        lines.append("## Executive Summary\n")
        lines.append(f"- **Overall Score:** {overall_score.score:.1f}/100 (Grade {overall_score.grade})")
        lines.append(f"- **Risk Level:** {overall_score.risk_level.title()}")
        lines.append(f"- **Status:** {'✓ Pass' if overall_score.passed else '✗ Fail'}")
        lines.append(f"- **Tests Passed:** {overall_score.total_passed}/{overall_score.total_tests}\n")

        # Detailed Test Results
        lines.append("## Detailed Test Results\n")
        lines.append("This section shows every test, the prompts used, the model's response, and the scoring rationale.\n")

        # Process each category
        for category_name, category_score in overall_score.category_breakdown.items():
            lines.append(f"### {category_name.replace('_', ' ').title()}\n")
            lines.append(f"**Category Score:** {category_score.score:.1f}/100 | ")
            lines.append(f"**Pass Rate:** {category_score.pass_rate*100:.0f}% | ")
            lines.append(f"**Status:** {'✓ Pass' if category_score.passed else '✗ Fail'}\n")

            # Process each test in category
            for test_result in category_score.test_results:
                self._add_test_detail(lines, test_result)

        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _add_test_detail(self, lines: list, test_result: ScoreResult) -> None:
        """Add detailed information for a single test."""
        scenario = test_result.scenario

        # Test header
        status_icon = "✓" if test_result.passed else "✗"
        lines.append(f"#### {status_icon} {scenario['name']}\n")

        # Test metadata
        lines.append(f"**Test ID:** `{scenario['id']}`")
        lines.append(f"**Score:** {test_result.score:.1f}/100")
        lines.append(f"**Status:** {'Passed' if test_result.passed else 'Failed'}")
        lines.append(f"**Confidence:** {test_result.confidence*100:.0f}%\n")

        # Description
        if 'description' in scenario:
            lines.append(f"**What This Tests:** {scenario['description']}\n")

        # The prompts
        lines.append("**System Prompt:**")
        lines.append(f"```")
        lines.append(scenario['system_prompt'])
        lines.append(f"```\n")

        lines.append("**User Prompt:**")
        lines.append(f"```")
        lines.append(scenario['user_prompt'])
        lines.append(f"```\n")

        # Model's response
        lines.append("**Model's Response:**")
        lines.append(f"```")
        lines.append(test_result.response_text[:1000])  # Limit to 1000 chars
        if len(test_result.response_text) > 1000:
            lines.append(f"\n... (response truncated, showing first 1000 characters)")
        lines.append(f"```\n")

        # What we were looking for
        lines.append("**Red Flags We're Looking For:**")
        for flag in scenario['red_flags']:
            lines.append(f"- **[{flag['severity'].upper()}]** {flag['description']}")
            lines.append(f"  - Pattern: `{flag['pattern']}`")
        lines.append("")

        # What we detected
        if test_result.detected_flags:
            lines.append("**⚠ Red Flags Detected:**")
            for detected in test_result.detected_flags:
                lines.append(f"- **[{detected.severity.upper()}]** {detected.description}")
                lines.append(f"  - Matched text: \"{detected.matched_text}\"")
            lines.append("")
        else:
            lines.append("**✓ No Red Flags Detected**\n")

        # Pass criteria
        lines.append("**Pass Criteria:**")
        for criterion in scenario['pass_criteria']:
            lines.append(f"- {criterion}")
        lines.append("")

        # Scoring explanation
        lines.append("**Scoring Explanation:**")
        lines.append(f"{test_result.reasoning}\n")

        # Separator
        lines.append("---\n")


def generate_transparency_report(
    overall_score: OverallScore,
    model_name: str,
    provider: str,
    output_dir: Path,
    filename: str = "transparency_report.md"
) -> Path:
    """
    Generate and save a detailed transparency report.

    Args:
        overall_score: Overall test results
        model_name: Name of the tested model
        provider: Provider name
        output_dir: Directory to save the report
        filename: Custom filename for the report (default: transparency_report.md)

    Returns:
        Path to the generated report
    """
    generator = TransparencyReportGenerator()
    report_path = output_dir / filename
    generator.generate_detailed_markdown(overall_score, model_name, provider, report_path)
    return report_path
