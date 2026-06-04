from setuptools import setup, find_packages

# Чтение зависимостей из requirements.txt
def read_requirements():
    with open("../requirements.txt", "r", encoding="utf-8") as f:
        return f.read().splitlines()

setup(
    name="max-ai",
    version="0.1.0",
    package_dir={"": "../src"},
    packages=find_packages(where=["../src"], include=["max_ai", "max_ai.*"]),
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "max-ai=max_ai.cli:main",
        ],
    },
    author="Your Name",
    author_email="your@example.com",
    description="A console AI agent using Cohere and Mistral",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/max-ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)