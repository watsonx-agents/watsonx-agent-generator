from dataclasses import dataclass
from pathlib import Path


@dataclass
class Arguments:
    agent_name: str
    agent_path: str
    agent_port: int
    host_port: int
    author_name: str | None
    author_email: str | None


@dataclass
class ProjectFile:
    from_path: Path
    to_path: Path


@dataclass
class Dockerfile(ProjectFile):
    agent_name: str


@dataclass
class Compose(ProjectFile):
    agent_name: str
    host_port: int
    agent_port: int


@dataclass
class Readme(ProjectFile):
    agent_name: str
    agent_path: str
    host_port: int
    author_name: str | None
    author_email: str | None


@dataclass
class Env(ProjectFile):
    agent_port: int


@dataclass
class Poetry:
    base_path: Path | str
    agent_name: str
    author_name: str | None = None
    author_email: str | None = None

@dataclass
class Configs(ProjectFile):
    agent_name: str
