"""
Setup script for OpenClaw + Claude Code 配置工具
"""

from setuptools import setup, find_packages

with open("README_v2.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="openclaw-claude-config",
    version="2.0.0",
    author="OpenClaw Claude Config Team",
    author_email="contact@example.com",
    description="A unified configuration tool for Claude Code and OpenClaw",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/openclaw-claude-config",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "openclaw-claude-config=openclaw_claude_config:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)