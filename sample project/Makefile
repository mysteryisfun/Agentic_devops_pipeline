# Makefile for Sample API - CI/CD Pipeline Testing Project
# This file provides common development and build tasks

# Variables
PYTHON := python
PIP := pip
UVICORN := uvicorn
PROJECT_NAME := sample-api-cicd
SRC_DIR := src
TESTS_DIR := tests

# Help target - default when just running 'make'
.PHONY: help
help:
	@echo "=== Sample API - CI/CD Pipeline Testing Project ==="
	@echo ""
	@echo "Available targets:"
	@echo "  help        - Show this help message"
	@echo "  install     - Install project dependencies"
	@echo "  build       - Build the project"
	@echo "  dev-install - Install in development mode"
	@echo "  run         - Run the FastAPI application"
	@echo "  test        - Run tests"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code with black"
	@echo "  clean       - Clean build artifacts"
	@echo "  deps        - Show installed dependencies"
	@echo ""

# Install dependencies
.PHONY: install
install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

# Build the project
.PHONY: build
build:
	@echo "Building project..."
	$(PYTHON) setup.py build
	@echo "Build completed successfully!"

# Install in development mode
.PHONY: dev-install
dev-install:
	@echo "Installing in development mode..."
	$(PIP) install -e .
	@echo "Development installation completed!"

# Run the FastAPI application
.PHONY: run
run:
	@echo "Starting FastAPI application..."
	$(PYTHON) -m $(SRC_DIR).main

# Run with uvicorn directly
.PHONY: serve
serve:
	@echo "Starting server with uvicorn..."
	$(UVICORN) $(SRC_DIR).main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	$(PYTHON) -m pytest $(TESTS_DIR) -v

# Run code linting
.PHONY: lint
lint:
	@echo "Running flake8 linting..."
	$(PYTHON) -m flake8 $(SRC_DIR) $(TESTS_DIR)

# Format code
.PHONY: format
format:
	@echo "Formatting code with black..."
	$(PYTHON) -m black $(SRC_DIR) $(TESTS_DIR)

# Check code formatting
.PHONY: format-check
format-check:
	@echo "Checking code formatting..."
	$(PYTHON) -m black --check $(SRC_DIR) $(TESTS_DIR)

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Clean completed!"

# Show installed dependencies
.PHONY: deps
deps:
	@echo "Installed dependencies:"
	$(PIP) list

# Install development dependencies
.PHONY: dev-deps
dev-deps:
	@echo "Installing development dependencies..."
	$(PIP) install pytest pytest-asyncio pytest-httpx black flake8

# Create requirements.txt from current environment
.PHONY: freeze
freeze:
	@echo "Creating requirements.txt from current environment..."
	$(PIP) freeze > requirements.txt

# Run all quality checks
.PHONY: check
check: lint format-check test
	@echo "All quality checks completed!"

# Quick development setup
.PHONY: setup
setup: install dev-deps
	@echo "Development environment setup completed!"

# Production build
.PHONY: prod-build
prod-build: clean install build
	@echo "Production build completed!"