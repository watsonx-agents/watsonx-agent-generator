#!/bin/bash

# Script to create and set up a Python virtual environment,
# The Git configuration step verifies that a global email is set

# Define the virtual environment directory.
VENV_DIR=".venv"

# Check if the virtual environment already exists.
if [ -d "$VENV_DIR" ]; then
    echo "$VENV_DIR already exists. Loading the virtual environment..."
else
    echo "Creating virtual environment ($VENV_DIR)..."
    python -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment. Please ensure Python 3 is properly installed."
        exit 1
    fi
fi

# Activate the virtual environment.
echo "✅ Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip to the latest version within the activated environment.
echo "⬆️ Upgrading pip in the virtual environment..."
pip install --upgrade pip

# Check if Poetry is installed. If not, install it.
if ! command -v poetry >/dev/null 2>&1; then
    echo "✨ Poetry not found. Installing Poetry in the virtual environment..."
    pip install poetry
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install Poetry within the virtual environment."
        deactivate
        exit 1
    fi
else
    echo "✅ Poetry is already installed. (Version: $(poetry --version))"
fi

# Upgrade Poetry to the latest version.
echo "⬆️ Upgrading Poetry to the latest version..."
pip install --upgrade poetry
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to upgrade Poetry within the virtual environment."
    deactivate
    exit 1
fi

# Verify that Poetry is accessible.
if ! command -v poetry >/dev/null 2>&1; then
    echo "❌ Error: Poetry installation failed. Please check your environment."
    deactivate
    exit 1
fi

# Install dependencies from requirements.txt if it exists.
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies from requirements.txt using pip..."
    pip install -r requirements.txt
else
    echo "📄 requirements.txt not found. Skipping pip dependency installation."
fi

echo "🎉 Environment setup with Poetry is complete."
echo "ℹ️ You can now use 'source .venv/bin/activate' to activate the environment manually."
