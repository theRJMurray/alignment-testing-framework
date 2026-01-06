# Documentation

This directory contains detailed documentation for the AI Alignment Testing Framework.

## Available Documentation

### Core Documentation

- **[METHODOLOGY.md](METHODOLOGY.md)** - Detailed explanation of testing methodology, scoring algorithms, and red flag detection

### Version History & Patches

- **[PATCH_0.1.2_TEST_ACCURACY_FIXES.md](PATCH_0.1.2_TEST_ACCURACY_FIXES.md)** - v0.1.2 patch notes: Critical test accuracy improvements
- **[TEST_ACCURACY_SUMMARY.md](TEST_ACCURACY_SUMMARY.md)** - Quick summary of test accuracy fixes

### Getting Started

For quick start instructions, see [QUICKSTART.md](../QUICKSTART.md) in the root directory.

### Contributing

For contribution guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md) in the root directory.

---

## Documentation Overview

### What This Tests

The framework tests four critical alignment failure modes:

1. **Deception Under Constraint** - Will models deceive when direct refusal is costly?
2. **Goal Preservation** - Do models prioritize original goals over new constraints?
3. **Power-Seeking Behavior** - Do models attempt to preserve or expand influence?
4. **Strategic Deception** - Do models engage in long-term deceptive planning?

### How It Works

1. **Test Scenarios** - Adversarially designed prompts that attempt to elicit misaligned behavior
2. **Red Flag Detection** - Pattern matching with context awareness to identify concerning responses
3. **Quantitative Scoring** - 0-100 scale with severity-weighted deductions
4. **Transparency Reports** - Complete visibility into prompts, responses, and scoring rationale

For full technical details, see [METHODOLOGY.md](METHODOLOGY.md).

---

## Additional Resources

- **Main README**: [../README.md](../README.md)
- **Changelog**: [../CHANGELOG.md](../CHANGELOG.md)
- **Examples**: [../examples/](../examples/)
- **Test Scenarios**: [../src/alignment_tester/data/test_scenarios/](../src/alignment_tester/data/test_scenarios/)
