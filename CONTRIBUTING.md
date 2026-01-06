# Contributing to AI Alignment Testing Framework

Thank you for your interest in contributing! This project aims to build reliable infrastructure for AI safety, and community contributions are essential.

## Ways to Contribute

### 1. Report Issues
Found a bug or have a suggestion? [Open an issue](https://github.com/theRJMurray/alignment-testing-framework/issues).

Please include:
- Description of the issue
- Steps to reproduce (if applicable)
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### 2. Add Test Scenarios
We need more adversarial test scenarios! To contribute a new test:

1. Create a test scenario in JSON format (see `docs/ADDING_TESTS.md`)
2. Validate it works on at least 2 models
3. Submit a PR with:
   - The test scenario JSON
   - Brief explanation of what it tests
   - Example responses showing pass/fail cases

**What makes a good test:**
- Tests a specific alignment failure mode
- Has clear pass/fail criteria
- Is realistic (could happen in deployment)
- Is adversarial (designed to elicit problems)
- Has theoretical grounding

### 3. Improve Documentation
- Fix typos or unclear explanations
- Add examples and tutorials
- Improve API documentation
- Translate documentation

### 4. Code Contributions
- Fix bugs
- Add model provider support
- Improve scoring algorithms
- Add new report formats
- Performance optimizations

## Development Setup

```bash
# Clone the repository
git clone https://github.com/theRJMurray/alignment-testing-framework.git
cd alignment-testing-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run tests
pytest
```

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints
- Format with `black`
- Docstrings for all public functions

```python
def my_function(param: str, count: int = 5) -> List[str]:
    """
    Brief description.

    Args:
        param: Description of param
        count: Description of count (default: 5)

    Returns:
        Description of return value

    Raises:
        ValueError: When this might be raised
    """
    pass
```

### Testing
- Add tests for new features
- Maintain >80% code coverage
- Use descriptive test names
- Test edge cases

### Commits
- Write clear commit messages
- Reference issues when applicable
- Keep commits focused and atomic

**Good commit messages:**
```
Add semantic similarity scoring for red flag detection

- Implement embedding-based pattern matching
- Add fallback to regex for backwards compatibility
- Update tests to cover new functionality

Fixes #42
```

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature-name`
3. **Make your changes** following code standards
4. **Add tests** if applicable
5. **Run tests**: `pytest`
6. **Format code**: `black src/`
7. **Update documentation** if needed
8. **Commit** with clear messages
9. **Push** to your fork
10. **Open a Pull Request** with:
    - Clear description of changes
    - Reference to related issues
    - Screenshots/examples if applicable

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Added tests for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commits are clean and well-described

## Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, a maintainer will merge

**Please be patient!** Maintainers are often volunteers. If you haven't heard back in a week, feel free to ping the PR.

## Adding Test Scenarios

Test scenarios are JSON files in `src/alignment_tester/data/test_scenarios/`.

### Test Scenario Template

```json
{
  "id": "category-###",
  "category": "deception|goal_preservation|power_seeking|strategic",
  "name": "Human-Readable Test Name",
  "description": "Detailed description of what this tests and why",
  "system_prompt": "Context/instructions for the model",
  "user_prompt": "The actual test prompt",
  "red_flags": [
    {
      "pattern": "regex pattern to detect",
      "severity": "critical|high|medium|low",
      "description": "Why this pattern indicates misalignment"
    }
  ],
  "pass_criteria": [
    "What the model should do",
    "Positive indicators of aligned behavior"
  ],
  "weight": 1.0,
  "tags": ["tag1", "tag2"]
}
```

### Validation Checklist

Before submitting a test scenario:
- [ ] Tested on at least 2 different models
- [ ] Has clear pass/fail cases
- [ ] Red flags are specific and relevant
- [ ] Pass criteria are measurable
- [ ] Description explains the failure mode
- [ ] JSON is valid (use a validator)

## Feature Requests

Have an idea for a new feature? Great! Please:

1. Check if it's already been suggested in [Issues](https://github.com/theRJMurray/alignment-testing-framework/issues)
2. Open a new issue with the `enhancement` label
3. Describe:
   - The problem it solves
   - Proposed solution
   - Alternative approaches considered
   - Potential impact on existing functionality

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or identity.

### Expected Behavior
- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Acknowledge contributions
- Assume good intent

### Unacceptable Behavior
- Harassment, discrimination, or personal attacks
- Trolling or inflammatory comments
- Publishing others' private information
- Other unprofessional conduct

### Enforcement
Violations may result in temporary or permanent ban from the project.

Report issues to: [therjmurray@gmail.com]

## Getting Help

- **Documentation:** Start with [README.md](README.md) and [docs/](docs/)
- **Issues:** Search existing issues or open a new one
- **Discussions:** Join [GitHub Discussions](https://github.com/theRJMurray/alignment-testing-framework/discussions)
- **Email:** For private inquiries: therjmurray@gmail.com

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Annual contributor acknowledgments

Major contributors may be invited to become maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make AI systems safer! 🛡️
