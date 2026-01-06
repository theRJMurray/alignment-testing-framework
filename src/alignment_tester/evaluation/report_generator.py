"""Report generation in various formats."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .scorer import OverallScore, CategoryScore, ScoreResult


class ReportGenerator:
    """Generates reports in various formats."""

    def __init__(self):
        """Initialize report generator."""
        if RICH_AVAILABLE:
            self.console = Console()

    def generate_console_report(
        self,
        overall_score: OverallScore,
        model_name: str,
        show_details: bool = True,
    ) -> None:
        """
        Generate and print console report.

        Args:
            overall_score: Overall test results
            model_name: Name of the model tested
            show_details: Whether to show detailed results
        """
        if RICH_AVAILABLE:
            self._generate_rich_report(overall_score, model_name, show_details)
        else:
            self._generate_plain_report(overall_score, model_name, show_details)

    def _generate_rich_report(
        self,
        overall_score: OverallScore,
        model_name: str,
        show_details: bool,
    ) -> None:
        """Generate report using rich formatting."""
        # Header
        self.console.print("\n")
        self.console.print(Panel.fit(
            f"[bold]AI Alignment Testing Framework v0.1[/bold]\n"
            f"Testing: {model_name}",
            border_style="blue"
        ))

        # Overall Summary
        status_symbol = "✓" if overall_score.passed else "✗"
        status_color = "green" if overall_score.passed else "red"

        self.console.print(f"\n[bold]RESULTS SUMMARY[/bold]")
        self.console.print("─" * 60)

        self.console.print(
            f"Overall Score:  {overall_score.score:.1f}/100 "
            f"([bold]{overall_score.grade}[/bold])  "
            f"[{status_color}]{status_symbol} "
            f"{'PASSED' if overall_score.passed else 'FAILED'}[/{status_color}]"
        )
        self.console.print(f"Risk Level:     {overall_score.risk_level.title()}")
        self.console.print(f"Confidence:     {overall_score.confidence*100:.0f}%")

        # Category breakdown
        self.console.print(f"\n[bold]Category Breakdown:[/bold]")
        for cat_name, cat_score in overall_score.category_breakdown.items():
            cat_status = "✓" if cat_score.passed else "✗"
            cat_color = "green" if cat_score.passed else "yellow"
            passed_count = sum(1 for r in cat_score.test_results if r.passed)
            total_count = len(cat_score.test_results)

            self.console.print(
                f"  {cat_name.replace('_', ' ').title():20} "
                f"{cat_score.score:5.1f}/100  "
                f"[{cat_color}]{cat_status}[/{cat_color}]  "
                f"({passed_count}/{total_count} passed)"
            )

        # Test statistics
        self.console.print(f"\n[bold]Test Statistics:[/bold]")
        self.console.print(f"  Total Tests:    {overall_score.total_tests}")
        self.console.print(f"  [green]Passed:         {overall_score.total_passed}[/green]")
        self.console.print(f"  [red]Failed:         {overall_score.total_failed}[/red]")

        # Failures detail
        if show_details and overall_score.total_failed > 0:
            self.console.print(f"\n[bold]FAILURES ({overall_score.total_failed})[/bold]")
            self.console.print("─" * 60)

            failure_count = 0
            for cat_name, cat_score in overall_score.category_breakdown.items():
                for result in cat_score.test_results:
                    if not result.passed:
                        failure_count += 1
                        severity = "CRITICAL" if any(
                            f.severity == "critical" for f in result.detected_flags
                        ) else "MEDIUM"
                        severity_color = "red" if severity == "CRITICAL" else "yellow"

                        self.console.print(
                            f"\n[{severity_color}][{severity}][/{severity_color}] "
                            f"{result.scenario['id']}: {result.scenario['name']}"
                        )
                        self.console.print(f"  Score: {result.score:.0f}/100")
                        self.console.print(f"  Issue: {result.reasoning}")

                        if result.detected_flags:
                            self.console.print("  Red Flags:")
                            for flag in result.detected_flags[:3]:  # First 3
                                self.console.print(
                                    f"    • [{flag.severity.upper()}] {flag.description}"
                                )

        self.console.print("\n" + "─" * 60)
        self.console.print()

    def _generate_plain_report(
        self,
        overall_score: OverallScore,
        model_name: str,
        show_details: bool,
    ) -> None:
        """Generate plain text report (fallback when rich not available)."""
        print("\n" + "=" * 60)
        print("AI Alignment Testing Framework v0.1")
        print(f"Testing: {model_name}")
        print("=" * 60)

        status = "PASSED" if overall_score.passed else "FAILED"
        print(f"\nOverall Score:  {overall_score.score:.1f}/100 ({overall_score.grade})  {status}")
        print(f"Risk Level:     {overall_score.risk_level.title()}")
        print(f"Confidence:     {overall_score.confidence*100:.0f}%")

        print(f"\nCategory Breakdown:")
        for cat_name, cat_score in overall_score.category_breakdown.items():
            status = "PASS" if cat_score.passed else "FAIL"
            passed_count = sum(1 for r in cat_score.test_results if r.passed)
            total_count = len(cat_score.test_results)
            print(
                f"  {cat_name.replace('_', ' ').title():20} "
                f"{cat_score.score:5.1f}/100  {status:4}  "
                f"({passed_count}/{total_count})"
            )

        print(f"\nTotal Tests: {overall_score.total_tests}")
        print(f"Passed:      {overall_score.total_passed}")
        print(f"Failed:      {overall_score.total_failed}")

        if show_details and overall_score.total_failed > 0:
            print(f"\nFAILURES ({overall_score.total_failed})")
            print("-" * 60)

            for cat_name, cat_score in overall_score.category_breakdown.items():
                for result in cat_score.test_results:
                    if not result.passed:
                        print(f"\n{result.scenario['id']}: {result.scenario['name']}")
                        print(f"  Score: {result.score:.0f}/100")
                        print(f"  Issue: {result.reasoning}")

        print("\n" + "=" * 60 + "\n")

    def generate_markdown_report(
        self,
        overall_score: OverallScore,
        model_name: str,
        provider: str,
        output_file: Optional[Path] = None,
    ) -> str:
        """
        Generate markdown report.

        Args:
            overall_score: Overall test results
            model_name: Name of the model
            provider: Provider name
            output_file: Optional file to save report to

        Returns:
            Markdown report as string
        """
        lines = []

        # Header
        lines.append("# Alignment Testing Report")
        lines.append("")
        lines.append(f"**Model:** {model_name}")
        lines.append(f"**Provider:** {provider}")
        lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Framework Version:** 0.1.0")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        status = "✓ Pass" if overall_score.passed else "✗ Fail"
        lines.append(f"- **Overall Score:** {overall_score.score:.1f}/100 (Grade {overall_score.grade})")
        lines.append(f"- **Risk Level:** {overall_score.risk_level.title()}")
        lines.append(f"- **Status:** {status}")
        lines.append(f"- **Confidence:** {overall_score.confidence*100:.0f}%")
        lines.append("")

        # Category Scores
        lines.append("## Category Scores")
        lines.append("")
        lines.append("| Category | Score | Pass Rate | Status | Critical Failures |")
        lines.append("|----------|-------|-----------|--------|-------------------|")

        for cat_name, cat_score in overall_score.category_breakdown.items():
            status = "✓ Pass" if cat_score.passed else "✗ Fail"
            lines.append(
                f"| {cat_name.replace('_', ' ').title()} | "
                f"{cat_score.score:.1f} | "
                f"{cat_score.pass_rate*100:.0f}% ({sum(1 for r in cat_score.test_results if r.passed)}/{len(cat_score.test_results)}) | "
                f"{status} | "
                f"{len(cat_score.critical_failures)} |"
            )

        lines.append("")

        # Detailed Results
        lines.append("## Detailed Results")
        lines.append("")

        for cat_name, cat_score in overall_score.category_breakdown.items():
            lines.append(f"### {cat_name.replace('_', ' ').title()} Tests")
            lines.append("")

            for result in cat_score.test_results:
                status_icon = "✓" if result.passed else "✗"
                lines.append(
                    f"#### {status_icon} {result.scenario['id']}: {result.scenario['name']}"
                )
                lines.append("")
                lines.append(f"- **Score:** {result.score:.1f}/100")
                lines.append(f"- **Status:** {'Passed' if result.passed else 'Failed'}")
                lines.append(f"- **Confidence:** {result.confidence*100:.0f}%")

                if result.detected_flags:
                    lines.append(f"- **Red Flags:** {len(result.detected_flags)}")
                    for flag in result.detected_flags:
                        lines.append(f"  - [{flag.severity.upper()}] {flag.description}")

                lines.append(f"- **Analysis:** {result.reasoning}")
                lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")

        if overall_score.passed:
            lines.append("✓ Model shows generally good alignment characteristics.")
        else:
            lines.append("⚠ Model shows concerning alignment failures.")

        if overall_score.risk_level in ["critical", "high"]:
            lines.append("")
            lines.append("**⚠ WARNING:** This model shows high-risk alignment failures.")
            lines.append("Deployment is not recommended without significant improvements.")

        lines.append("")
        lines.append("## Methodology")
        lines.append("")
        lines.append("This evaluation used the AI Alignment Testing Framework v0.1, which tests for:")
        lines.append("- Deception under constraint")
        lines.append("- Goal preservation vs policy compliance")
        lines.append("- Power-seeking behavior")
        lines.append("- Strategic deception")
        lines.append("")

        # Join all lines
        report = "\n".join(lines)

        # Save to file if requested
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)

        return report

    def generate_json_report(
        self,
        overall_score: OverallScore,
        model_name: str,
        provider: str,
        output_file: Optional[Path] = None,
    ) -> str:
        """
        Generate JSON report.

        Args:
            overall_score: Overall test results
            model_name: Name of the model
            provider: Provider name
            output_file: Optional file to save report to

        Returns:
            JSON report as string
        """
        report = {
            "meta": {
                "framework_version": "0.1.0",
                "timestamp": datetime.now().isoformat(),
                "model": {
                    "name": model_name,
                    "provider": provider,
                },
            },
            "results": {
                "overall": {
                    "score": overall_score.score,
                    "grade": overall_score.grade,
                    "risk_level": overall_score.risk_level,
                    "passed": overall_score.passed,
                    "confidence": overall_score.confidence,
                },
                "summary": {
                    "total_tests": overall_score.total_tests,
                    "passed": overall_score.total_passed,
                    "failed": overall_score.total_failed,
                },
                "categories": {},
            },
        }

        # Add category details
        for cat_name, cat_score in overall_score.category_breakdown.items():
            report["results"]["categories"][cat_name] = {
                "score": cat_score.score,
                "pass_rate": cat_score.pass_rate,
                "passed": cat_score.passed,
                "confidence": cat_score.confidence,
                "critical_failures": len(cat_score.critical_failures),
                "tests": [
                    {
                        "id": result.scenario["id"],
                        "name": result.scenario["name"],
                        "score": result.score,
                        "passed": result.passed,
                        "confidence": result.confidence,
                        "detected_flags": [
                            {
                                "severity": flag.severity,
                                "description": flag.description,
                                "pattern": flag.pattern,
                            }
                            for flag in result.detected_flags
                        ],
                        "reasoning": result.reasoning,
                    }
                    for result in cat_score.test_results
                ],
            }

        # Convert to JSON
        json_str = json.dumps(report, indent=2, ensure_ascii=False)

        # Save to file if requested
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str
