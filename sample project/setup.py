"""
Setup script for Sample API - CI/CD Pipeline Testing Project
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = []
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                # Remove version constraints for setup.py
                package = line.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0]
                if package:
                    requirements.append(line)
        return requirements

# Read README for long description
def read_readme():
    """Read README file for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Sample API for CI/CD Pipeline Testing"

setup(
    # Package metadata
    name="sample-api-cicd",
    version="1.0.0",
    description="A complete FastAPI sample application for testing CI/CD pipelines",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    
    # Author information
    author="DevOps Team",
    author_email="devops@example.com",
    
    # Package discovery
    packages=find_packages(),
    package_dir={"": "."},
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Package classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
    ],
    
    # Keywords for PyPI
    keywords="fastapi api rest cicd pipeline testing sample",
    
    # Entry points for command line scripts
    entry_points={
        "console_scripts": [
            "run-sample-api=src.main:main",
        ],
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    
    # Project URLs
    project_urls={
        "Documentation": "https://github.com/example/sample-api-cicd",
        "Source": "https://github.com/example/sample-api-cicd",
        "Tracker": "https://github.com/example/sample-api-cicd/issues",
    },
)