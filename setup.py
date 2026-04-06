"""
Setup configuration for Oil & Gas Production Repo
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="oil-gas-production",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python project for analyzing oil and gas production data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pcarun606-cyber/Oil-gas-production-repo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "scikit-learn>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "jupyter>=1.0.0",
        ]
    },
)
