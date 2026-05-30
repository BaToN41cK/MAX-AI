import os
import shutil
from setuptools import setup, find_packages

def add_to_path_windows():
    """Add Python Scripts directory to PATH on Windows."""
    if os.name != 'nt':
        return
    
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
        current_path, _ = winreg.QueryValueEx(key, "Path")
        winreg.CloseKey(key)
        
        # Get the scripts directory
        scripts_dir = os.path.join(os.environ.get('APPDATA', ''), 'Python', 'Python313', 'Scripts')
        if not os.path.exists(scripts_dir):
            scripts_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python313', 'Scripts')
        
        if scripts_dir and scripts_dir not in current_path:
            new_path = current_path + os.pathsep + scripts_dir
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
    except Exception:
        pass

def post_install():
    npm_dir = os.path.expanduser("~/.npm")
    if not os.path.exists(npm_dir):
        npm_dir = os.path.join(os.environ.get('APPDATA', ''), 'npm')
    if os.path.exists(npm_dir):
        bat_path = os.path.join(os.path.dirname(__file__), 'max-ai.cmd')
        if os.path.exists(bat_path):
            try:
                shutil.copy(bat_path, os.path.join(npm_dir, 'max-ai.bat'))
            except:
                pass
    add_to_path_windows()

setup(
    name="max-ai",
    version="0.1.0",
    package_dir={"": "."},
    packages=find_packages(include=["max_ai", "max_ai.*"]),
    install_requires=[
        "requests",
        "python-dotenv",
        "click",
        "cohere",
        "mistralai",
        "beautifulsoup4",
        "rich",
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
    python_requires=">=3.6",
)

post_install()