# Quick Start Guide

Get up and running with the AI Alignment Testing Framework in 5 minutes.

## 1. Installation

```bash
# Navigate to the project directory
cd alignment-testing-framework

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## 2. Set Up API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# You can get keys from:
# - Anthropic: https://console.anthropic.com/
# - OpenAI: https://platform.openai.com/api-keys
```

Example `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

## 3. Run Your First Test

### Option A: Using the CLI

```bash
# Test Claude Sonnet (recommended for first test)
alignment-tester test --model claude-3-haiku-20240307

# Test GPT-3.5 Turbo (cheaper option)
alignment-tester test --model gpt-3.5-turbo

# Test specific category only (faster)
alignment-tester test --model claude-3-haiku --category deception
```

### Option B: Using Python

```python
from alignment_tester import AlignmentTester, AnthropicAdapter
import os

# Create model adapter
model = AnthropicAdapter(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model_name="claude-3-haiku-20240307"
)

# Create tester and run
tester = AlignmentTester(model_adapter=model)
results = tester.run_all_tests()

# Print summary
print(f"Overall Score: {results.score:.1f}/100")
print(f"Grade: {results.grade}")
print(f"Risk Level: {results.risk_level}")
```

### Option C: Run the Demo Script

```bash
# Run comprehensive demo showing all features
python examples/demo.py
```

## 4. View Results

Results are saved in the `results/` directory by default:

- **Console**: Immediate rich-formatted output
- **Markdown**: `results/report_*.md` - Human-readable report
- **JSON**: `results/results_*.json` - Machine-readable data

## 5. Next Steps

### Compare Models

```bash
alignment-tester compare claude-3-haiku gpt-3.5-turbo
```

### Customize Output

```bash
# Save all formats
alignment-tester test --model claude-3-haiku --format all --output ./my-results

# Verbose mode for debugging
alignment-tester test --model claude-3-haiku --verbose
```

### Add Custom Tests

1. Create a JSON file in `src/alignment_tester/data/test_scenarios/`
2. Follow the format in existing test files
3. Run tests to validate

See [docs/ADDING_TESTS.md](docs/ADDING_TESTS.md) for details.

## Common Commands

```bash
# List supported models
alignment-tester list-models

# Test with custom parameters
alignment-tester test \
  --model claude-3-sonnet \
  --category power_seeking \
  --temperature 0.5 \
  --max-tokens 500 \
  --output ./custom-results

# Get help
alignment-tester --help
alignment-tester test --help
```

## Estimated Costs

Costs for full test suite (20 tests):

| Model | Cost |
|-------|------|
| Claude Haiku | ~$0.01 |
| Claude Sonnet | ~$0.16 |
| GPT-3.5 Turbo | ~$0.02 |
| GPT-4 Turbo | ~$0.34 |

Single category (5 tests) costs approximately 1/4 of the above.

## Troubleshooting

### "API key not found"
- Make sure your `.env` file exists and has the correct key name
- Or set environment variable: `export ANTHROPIC_API_KEY=your_key`

### "Module not found"
- Make sure you installed: `pip install -r requirements.txt`
- Or install package: `pip install -e .`

### "Rate limit exceeded"
- The framework includes rate limiting, but if you hit limits:
- Wait a few minutes
- Reduce concurrent requests in config
- Use a cheaper model for testing

### "No test scenarios found"
- Make sure you're running from the project root directory
- Check that `src/alignment_tester/data/test_scenarios/` contains JSON files

## Getting Help

- **Documentation**: See [README.md](README.md) and [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/theRJMurray/alignment-testing-framework/issues)
- **Methodology**: [docs/METHODOLOGY.md](docs/METHODOLOGY.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## What's Next?

1. ✅ Run your first test
2. 📊 Compare multiple models
3. 🧪 Add your own test scenarios
4. 📖 Read the methodology documentation
5. 🤝 Contribute back to the project

Happy testing! 🛡️
