import logging
import os
from datetime import datetime
from pathlib import Path
from sys import stdout
from threading import Lock

from {AGENT_NAME}.configs import DATE_FORMAT, DEFAULT_LOCALE, LOGGING_FORMAT, LOGS_FOLDER


def timetz(*args):
    return datetime.now(DEFAULT_LOCALE).timetuple()


def setup_logger(logger_name: str, log_file: str | Path, level=logging.DEBUG) -> logging.Logger:
    log_dir = log_file.parent if type(log_file) == Path else os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)

    l = logging.getLogger(logger_name)
    l.setLevel(level)
    formatter = logging.Formatter(LOGGING_FORMAT, DATE_FORMAT)
    formatter.converter = timetz

    fileHandler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fileHandler.setLevel(level)
    fileHandler.setFormatter(formatter)
    l.addHandler(fileHandler)

    handler = logging.StreamHandler(stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    l.addHandler(handler)

    l.info("-" * 100)
    return l


class Logger:
    _instances: dict[str, "Logger"] = {}
    _lock: Lock = Lock()
    name: str
    logger: logging.Logger

    def __new__(cls, name: str = "application", level=logging.DEBUG):
        with cls._lock:
            if not cls._instances.get(name):
                logger = super(Logger, cls).__new__(cls)
                logger.logger = setup_logger(name, LOGS_FOLDER / f"{name}.log", level)
                cls._instances[name] = logger

        return cls._instances[name]

    def __init__(self, name: str = "application", level=logging.DEBUG):
        self.name = name


if __name__ == "__main__":
    logger = Logger(name="application")
    logger.logger.info("This is a trial")