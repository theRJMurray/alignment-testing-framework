"""Setup script for alignment-testing-framework."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="alignment-testing-framework",
    version="0.1.5",
    description="Automated adversarial testing framework for AI alignment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Safety Evaluation Platform",
    author_email="therjmurray@gmail.com",
    url="https://github.com/theRJMurray/alignment-testing-framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "alignment_tester": [
            "data/test_scenarios/*.json",
        ],
    },
    python_requires=">=3.10",
    install_requires=[
        "anthropic>=0.41.0",
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.7.0",
        "numpy>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "alignment-tester=alignment_tester.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai alignment safety testing adversarial llm",
)
