"""
Setup script for the crypto trading bot.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crypto-trading-bot",
    version="1.0.0",
    author="Crypto Bot Development Team",
    description="A professional cryptocurrency trading bot with multiple strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Amir923923/crypto-bot-deveolpment-",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
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
        "ccxt>=4.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "ta>=0.11.0",
        "sqlalchemy>=2.0.0",
        "loguru>=0.7.0",
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-asyncio>=0.21.0",
        "backtrader>=1.9.78",
        "pyyaml>=6.0",
        "aiohttp>=3.9.4",
    ],
    entry_points={
        "console_scripts": [
            "crypto-bot=main:main",
        ],
    },
)
