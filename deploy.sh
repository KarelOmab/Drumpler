#!/bin/bash
# Activate the virtual environment
source venv/bin/activate

# Clean up previous build artifacts
rm -rf build dist *.egg-info

# Install or update build tools
python3 -m pip install --upgrade build twine

# Build the package
python3 -m build

# Upload the package to PyPI
python3 -m twine upload dist/*
