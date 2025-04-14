from pathlib import Path

BASE_PATH: Path = Path(__file__).parent.parent.parent.resolve()
LOGS_FOLDER: Path = BASE_PATH / "logs"
