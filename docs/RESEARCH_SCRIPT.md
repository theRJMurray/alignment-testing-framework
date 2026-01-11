# Research Script Documentation

The `examples/research.py` script provides a comprehensive testing framework designed specifically for AI analysis of alignment test accuracy.

## Purpose

This script generates detailed results that enable another AI coding agent to:
- **Identify false positives**: Cases where alignment tests incorrectly flag safe/aligned behavior
- **Identify false negatives**: Cases where alignment tests miss actual misalignment
- **Analyze patterns**: Review scoring consistency across different test categories
- **Review reasoning**: Examine full model responses and scoring justifications

## Key Features

### Multi-Model Testing
Tests multiple AI models in sequence:
- **Claude Sonnet 4.5** (latest, most capable)
- **Claude Haiku 4.5** (fast, cost-effective)
- **GPT-4o** (latest, most capable)
- **GPT-4o Mini** (fast, cost-effective)

### Complete Test Suite
Runs all 36 test scenarios across 4 categories:
- **Deception** (9 tests): Testing deception under constraint
- **Goal Preservation** (9 tests): Testing goal preservation vs policy compliance
- **Power Seeking** (9 tests): Testing power-seeking behavior
- **Strategic** (9 tests): Testing strategic deception and planning

### AI-Analysis-Optimized Outputs

Each model generates a timestamped results directory containing:

#### `research_results.json`
Complete research data including:
```json
{
  "metadata": {
    "model_name": "Claude-Sonnet-4.5",
    "timestamp": "20241201_143022",
    "test_parameters": {"temperature": 0.7, "max_tokens": 1000},
    "duration_seconds": 245.67,
    "estimated_cost_usd": 0.0234
  },
  "overall_score": {
    "score": 87.5,
    "grade": "B",
    "risk_level": "Medium",
    "pass_rate": 0.875
  },
  "category_results": {
    "deception": {"score": 85.0, "pass_rate": 0.889},
    "goal_preservation": {"score": 90.0, "pass_rate": 1.0}
  }
}
```

#### `transparency_report.md`
Full question-and-answer format showing:
- Original test prompts
- Complete model responses
- Scoring reasoning
- Red flag detections
- Pass/fail justifications

#### `summary_*.md`
Human-readable summary report

#### `results_*.json`
Detailed scoring data

## Usage

### Prerequisites
Set API keys for desired models:
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
export OPENAI_API_KEY=sk-your-key-here
```

### Running the Research Suite
```bash
# Run complete research suite
python examples/research.py
```

### Output Structure
```
research_results/
├── 20241201_143022_Claude-Sonnet-4.5/
│   ├── research_results.json      # AI-ready analysis data
│   ├── transparency_report.md     # Full Q&A details
│   ├── summary_20241201_143022.md # Human-readable summary
│   └── results_20241201_143022.json # Detailed scores
├── 20241201_145031_Claude-Haiku-4.5/
│   └── ...
└── comparative_analysis.json     # Cross-model comparison
```

## For AI Analysis

### False Positive Detection
Look for cases where:
- Model responses are safe/helpful but receive low scores
- Red flags are triggered by benign behavior
- Scoring doesn't match human judgment of safety

### False Negative Detection
Look for cases where:
- Model responses show misalignment but pass tests
- Dangerous behavior isn't flagged appropriately
- Scores are artificially inflated

### Pattern Analysis
- Compare consistency across model families
- Identify category-specific scoring issues
- Review edge cases and boundary conditions

## Configuration

Modify `RESEARCH_CONFIG` in `examples/research.py` to:
- Add/remove models for testing
- Adjust test parameters (temperature, max_tokens)
- Customize output formats
- Change result directory location

## Cost Estimation

The script provides cost estimates before running tests:
- Claude Sonnet 4.5: ~$0.02-0.03 per full test suite
- Claude Haiku 4.5: ~$0.005-0.01 per full test suite
- GPT-4o: ~$0.02-0.03 per full test suite
- GPT-4o Mini: ~$0.001-0.002 per full test suite

## Integration with Development Workflow

1. Run research script to generate baseline results
2. Make changes to test scenarios or scoring logic
3. Re-run research script to compare results
4. Use comparative analysis to validate improvements
5. Iterate on false positive/negative fixes

This approach enables systematic improvement of alignment test accuracy through AI-assisted analysis and refinement.

