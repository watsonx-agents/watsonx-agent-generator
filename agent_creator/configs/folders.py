from pathlib import Path

BASE_PATH: Path = Path(__file__).parent.parent.parent.resolve()
LOGS_FOLDER: Path = BASE_PATH / "logs"
ASSETS_FOLDER: Path = BASE_PATH / "assets"
DEFAULT_AGENT_BASE_PATH: Path = BASE_PATH.parent / "src" / "agents"
