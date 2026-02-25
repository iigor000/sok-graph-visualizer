"""Setup configuration for the SOK Graph Visualization API."""

from setuptools import setup, find_packages

setup(
    name="graph-api",
    version="0.1.0",
    description="API library for Graph Visualization Platform",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0",
    ]
)
