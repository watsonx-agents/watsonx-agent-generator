from pathlib import Path

# The project root (where your `pyproject.toml` lives)
BASE_PATH: Path = Path(__file__).parent.parent.parent.resolve()

LOGS_FOLDER: Path = BASE_PATH / "logs"
ASSETS_FOLDER: Path = BASE_PATH / "assets"

# ↓ change this from BASE_PATH.parent/"src"/"agents" ↓
DEFAULT_AGENT_BASE_PATH: Path = BASE_PATH / "agents"
