from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    source_folder: Path
    backup_folder: Path
    log_level: int


def load_settings(env_file: str | Path | None = None) -> Settings:
    load_dotenv(dotenv_path=env_file)

    source = os.getenv("SOURCE_FOLDER")
    backup = os.getenv("BACKUP_FOLDER")
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()

    if not source:
        raise ValueError("SOURCE_FOLDER no está configurado")
    if not backup:
        raise ValueError("BACKUP_FOLDER no está configurado")

    level = getattr(logging, level_name, None)
    if not isinstance(level, int):
        raise ValueError(f"LOG_LEVEL inválido: {level_name}")

    return Settings(Path(source).expanduser(), Path(backup).expanduser(), level)
