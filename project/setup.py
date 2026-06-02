from setuptools import setup, find_packages

setup(
    name="max-ai",
    version="0.1.0",
    package_dir={"": "../src"},
    packages=find_packages(where=["../src"], include=["max_ai", "max_ai.*"]),
    install_requires=[
        "requests",
        "python-dotenv",
        "click",
        "cohere",
        "mistralai",
        "beautifulsoup4",
        "rich",
        "aiohttp",
        "PyPDF2>=3.0.0",
        "python-docx>=0.8.11",
        "python-pptx>=0.6.23",
        "openpyxl>=3.1.0",
        "xlrd>=1.2.0",
        "youtube-transcript-api>=0.6.0",
        "yt-dlp",
        "PyYAML",
    ],
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