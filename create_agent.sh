#!/bin/bash

# Get the absolute path of the script's directory (project root).
script_dir=$(realpath "$(dirname "$0")")

# Change the current directory to the project root.
cd "$script_dir" || {
    echo "❌ Error: Could not change directory to '$script_dir'"
    exit 1
}

# Path to the virtual environment (located in project root)
VENV_PATH="$script_dir/.venv"

# Check if the virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Error: Virtual environment not found at '$VENV_PATH'. Please run install.sh first."
    exit 1
fi

# Activate the virtual environment
echo "✅ Activating virtual environment from $VENV_PATH..."
source "$VENV_PATH/bin/activate"

# Ensure .env file exists; copy from agent_creator/.env_template if missing.
if [ ! -f ".env" ]; then
    if [ -f "agent_creator/.env_template" ]; then
        echo "ℹ️ .env not found. Copying from agent_creator/.env_template..."
        cp agent_creator/.env_template .env
    else
        echo "❌ Error: .env and .env_template not found. Cannot continue without environment configuration."
        deactivate
        exit 1
    fi
fi

# Check if poetry.lock exists in the project root.
if [ ! -f "poetry.lock" ]; then
    echo "📦 poetry.lock not found. Running 'poetry install'..."
    poetry install
    if [ $? -ne 0 ]; then
        echo "❌ Error: 'poetry install' failed."
        deactivate
        exit 1
    fi
fi

# Run the main Python script using Poetry from its correct relative path.
echo "🚀 Running 'poetry run python agent_creator/main.py'..."
poetry run python agent_creator/main.py

if [ $? -ne 0 ]; then
    echo "❌ Error: 'poetry run python agent_creator/main.py' failed."
    deactivate
    exit 1
fi

# Deactivate environment after script completes.
deactivate

echo "✅ Script execution complete."
