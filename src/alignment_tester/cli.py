"""Command-line interface for alignment testing framework."""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import click
except ImportError:
    print("Error: click package not installed. Install with: pip install click")
    sys.exit(1)

from dotenv import load_dotenv
import os

from .core.tester import AlignmentTester
from .models import AnthropicAdapter, OpenAIAdapter
from .evaluation.report_generator import ReportGenerator


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.5")
def cli():
    """AI Alignment Testing Framework - Test models for misalignment patterns."""
    pass


@cli.command()
@click.option(
    "--model",
    required=True,
    help="Model name (e.g., claude-3-sonnet-20240229, gpt-4-turbo-preview)",
)
@click.option(
    "--provider",
    type=click.Choice(["anthropic", "openai"], case_sensitive=False),
    help="Model provider (auto-detected if not specified)",
)
@click.option(
    "--api-key",
    envvar="API_KEY",
    help="API key (or set ANTHROPIC_API_KEY/OPENAI_API_KEY env var)",
)
@click.option(
    "--category",
    type=click.Choice(
        ["deception", "goal_preservation", "power_seeking", "strategic", "all"],
        case_sensitive=False,
    ),
    default="all",
    help="Test category to run (default: all)",
)
@click.option(
    "--output",
    type=click.Path(),
    default="./results",
    help="Output directory for results",
)
@click.option(
    "--temperature",
    type=float,
    default=0.7,
    help="Model temperature (default: 0.7)",
)
@click.option(
    "--max-tokens",
    type=int,
    default=1000,
    help="Maximum tokens per response (default: 1000)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["console", "markdown", "json", "all"], case_sensitive=False),
    default="console",
    help="Output format (default: console)",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed test execution logs",
)
def test(
    model: str,
    provider: Optional[str],
    api_key: Optional[str],
    category: str,
    output: str,
    temperature: float,
    max_tokens: int,
    output_format: str,
    verbose: bool,
):
    """Run alignment tests on a model."""
    # Set logging level
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Auto-detect provider if not specified
    if not provider:
        if "claude" in model.lower():
            provider = "anthropic"
        elif "gpt" in model.lower():
            provider = "openai"
        else:
            click.echo(
                "Error: Could not auto-detect provider. "
                "Please specify --provider (anthropic or openai)",
                err=True,
            )
            sys.exit(1)

    # Get API key
    if not api_key:
        if provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        click.echo(
            f"Error: API key not found. Set {provider.upper()}_API_KEY "
            "environment variable or use --api-key flag",
            err=True,
        )
        sys.exit(1)

    # Create model adapter
    try:
        if provider == "anthropic":
            model_adapter = AnthropicAdapter(api_key=api_key, model_name=model)
        elif provider == "openai":
            model_adapter = OpenAIAdapter(api_key=api_key, model_name=model)
        else:
            click.echo(f"Error: Unsupported provider: {provider}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error initializing model: {e}", err=True)
        sys.exit(1)

    # Show cost estimate
    try:
        if category == "all":
            num_tests = 20  # 5 per category × 4 categories
        else:
            num_tests = 5

        cost_estimate = model_adapter.estimate_cost(num_tests)
        click.echo(
            f"\nEstimated cost: ${cost_estimate.total_cost_usd:.4f} "
            f"(~${cost_estimate.cost_per_test_usd:.4f} per test)"
        )

        if not click.confirm("Continue with tests?", default=True):
            click.echo("Aborted.")
            sys.exit(0)
    except Exception as e:
        logger.warning(f"Could not estimate cost: {e}")

    # Create tester
    tester = AlignmentTester(
        model_adapter=model_adapter, output_dir=Path(output)
    )

    # Run tests
    try:
        click.echo(f"\nTesting model: {model}")
        click.echo(f"Provider: {provider}")
        click.echo(f"Category: {category}")
        click.echo()

        if category == "all":
            overall_score = tester.run_all_tests(
                temperature=temperature, max_tokens=max_tokens
            )
        else:
            category_score = tester.run_category(
                category, temperature=temperature, max_tokens=max_tokens
            )
            # Calculate overall score from single category
            overall_score = tester.scorer.calculate_overall_score(
                {category: category_score}
            )

    except KeyboardInterrupt:
        click.echo("\n\nTests interrupted by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\nError running tests: {e}", err=True)
        logger.exception("Test execution failed")
        sys.exit(1)

    # Generate reports
    report_gen = ReportGenerator()
    model_info = model_adapter.get_model_info()

    if output_format in ["console", "all"]:
        click.echo("\n")
        report_gen.generate_console_report(
            overall_score, model_info.model_name, show_details=verbose
        )

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if output_format in ["markdown", "all"]:
        md_file = output_dir / f"report_{model.replace('/', '_')}.md"
        report_gen.generate_markdown_report(
            overall_score,
            model_info.model_name,
            model_info.provider,
            md_file,
        )
        click.echo(f"Markdown report saved to: {md_file}")

    if output_format in ["json", "all"]:
        json_file = output_dir / f"results_{model.replace('/', '_')}.json"
        report_gen.generate_json_report(
            overall_score,
            model_info.model_name,
            model_info.provider,
            json_file,
        )
        click.echo(f"JSON results saved to: {json_file}")


@cli.command()
@click.argument("models", nargs=-1, required=True)
@click.option(
    "--api-key-anthropic",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key",
)
@click.option(
    "--api-key-openai",
    envvar="OPENAI_API_KEY",
    help="OpenAI API key",
)
@click.option(
    "--output",
    type=click.Path(),
    default="./results/comparison",
    help="Output directory for comparison results",
)
@click.option(
    "--temperature",
    type=float,
    default=0.7,
    help="Model temperature (default: 0.7)",
)
def compare(
    models: tuple,
    api_key_anthropic: Optional[str],
    api_key_openai: Optional[str],
    output: str,
    temperature: float,
):
    """Compare multiple models side-by-side.

    Example: alignment-tester compare claude-3-sonnet gpt-4-turbo
    """
    if len(models) < 2:
        click.echo("Error: Please specify at least 2 models to compare", err=True)
        sys.exit(1)

    click.echo(f"\nComparing {len(models)} models...")
    click.echo()

    # Create adapters for each model
    adapters = []
    for model in models:
        # Auto-detect provider
        if "claude" in model.lower():
            if not api_key_anthropic:
                click.echo(f"Error: ANTHROPIC_API_KEY not set for {model}", err=True)
                sys.exit(1)
            adapters.append(
                AnthropicAdapter(api_key=api_key_anthropic, model_name=model)
            )
        elif "gpt" in model.lower():
            if not api_key_openai:
                click.echo(f"Error: OPENAI_API_KEY not set for {model}", err=True)
                sys.exit(1)
            adapters.append(OpenAIAdapter(api_key=api_key_openai, model_name=model))
        else:
            click.echo(f"Error: Could not detect provider for {model}", err=True)
            sys.exit(1)

    # Run comparison
    try:
        # Use first adapter's tester for comparison
        tester = AlignmentTester(adapters[0], output_dir=Path(output))
        comparison = tester.compare_models(adapters, temperature=temperature)

        # Display results
        click.echo("\nComparison Results:")
        click.echo("=" * 80)
        click.echo(f"{'Model':<30} {'Score':<10} {'Grade':<8} {'Risk':<10} {'Status'}")
        click.echo("-" * 80)

        for model_result in comparison["models"]:
            status = "✓ Pass" if model_result["passed"] else "✗ Fail"
            click.echo(
                f"{model_result['name']:<30} "
                f"{model_result['score']:>6.1f}/100  "
                f"{model_result['grade']:<8} "
                f"{model_result['risk_level']:<10} "
                f"{status}"
            )

        click.echo("=" * 80)

        # Save comparison report
        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)

        import json
        comparison_file = output_dir / "comparison.json"
        with open(comparison_file, "w") as f:
            json.dump(comparison, f, indent=2)

        click.echo(f"\nComparison results saved to: {comparison_file}")

    except Exception as e:
        click.echo(f"\nError during comparison: {e}", err=True)
        logger.exception("Comparison failed")
        sys.exit(1)


@cli.command()
def list_models():
    """List supported models."""
    click.echo("\nSupported Models:")
    click.echo("\n[Anthropic Claude]")
    for model in AnthropicAdapter.SUPPORTED_MODELS.keys():
        click.echo(f"  - {model}")

    click.echo("\n[OpenAI GPT]")
    for model in OpenAIAdapter.SUPPORTED_MODELS.keys():
        click.echo(f"  - {model}")

    click.echo()


if __name__ == "__main__":
    cli()
