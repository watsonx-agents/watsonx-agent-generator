#!/bin/bash

# Script to create and set up a Python virtual environment,
# install Poetry if necessary, and configure Git for IBM software.
# The Git configuration step verifies that a global email is set
# that ends with '@ibm.com'. Otherwise, it prompts the user for a valid IBM email.

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

# --- Git Setup Section ---
echo "🔧 Configuring Git defaults..."

# Check the current global Git user.email.
git_global_email=$(git config --global user.email 2>/dev/null)
if [ -n "$git_global_email" ]; then
    echo "Found global Git email: $git_global_email"
    # Verify that the email ends with '@ibm.com'
    if [[ "$git_global_email" == *@ibm.com ]]; then
        echo "✅ Global Git email is valid (ends with @ibm.com)."
    else
        echo "❌ Error: Global Git email '$git_global_email' is not a valid IBM email."
        echo "Please update your global Git configuration to use an email ending with '@ibm.com'."
        deactivate
        exit 1
    fi
else
    echo "No global Git user.email is set."
    read -p "Please enter your IBM email (must end with @ibm.com): " input_email
    if [[ "$input_email" == *@ibm.com ]]; then
        echo "Setting global Git user.email to $input_email."
        git config --global user.email "$input_email"
    else
        echo "❌ Error: Provided email is not a valid IBM email. Exiting installation."
        deactivate
        exit 1
    fi
fi

# Check the current global Git user.name.
git_global_username=$(git config --global user.name 2>/dev/null)
if [ -z "$git_global_username" ]; then
    echo "No global Git user.name is set."
    read -p "Please enter your IBM Git user.name (e.g., 'IBM Platform CIC') or press Enter to use the default: " input_username
    if [ -z "$input_username" ]; then
        input_username="IBM Platform CIC"
    fi
    git config --global user.name "$input_username"
fi

echo "✅ Git configured with: user.name='$(git config --global user.name)', user.email='$(git config --global user.email)'"
# --- End Git Setup Section ---

echo "🎉 Environment setup with Poetry is complete."
echo "ℹ️ You can now use 'source .venv/bin/activate' to activate the environment manually."
