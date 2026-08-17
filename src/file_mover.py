from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

LOGGER = logging.getLogger(__name__)
MONTHS_ES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


@dataclass
class MoveSummary:
    moved: int = 0
    skipped: int = 0
    errors: int = 0


@dataclass(frozen=True)
class WorkWindow:
    start: datetime
    end: datetime


def work_window_for(run_date: date) -> WorkWindow:
    previous_day = run_date - timedelta(days=1)
    return WorkWindow(
        start=datetime.combine(previous_day, time(19, 0)),
        end=datetime.combine(run_date, time(6, 59, 59, 999999)),
    )


def dated_destination(backup_folder: Path, run_date: date) -> Path:
    return backup_folder / MONTHS_ES[run_date.month - 1] / f"{run_date.day:02d}"


def latest_source_activity(source_folder: Path, backup_folder: Path) -> datetime | None:
    latest: datetime | None = None
    backup_resolved = backup_folder.resolve(strict=False)

    for item in source_folder.iterdir():
        if item.resolve(strict=False) == backup_resolved:
            continue
        try:
            modified = datetime.fromtimestamp(item.stat().st_mtime)
        except OSError as exc:
            LOGGER.error("No se pudo leer la fecha de %s: %s", item, exc)
            continue
        if latest is None or modified > latest:
            latest = modified

    return latest


def source_is_idle(
    source_folder: Path,
    backup_folder: Path,
    now: datetime,
    idle_minutes: int = 120,
) -> bool:
    latest = latest_source_activity(source_folder, backup_folder)
    if latest is None:
        return True
    return now - latest >= timedelta(minutes=idle_minutes)


def candidate_indesign_files(source_folder: Path, backup_folder: Path, run_date: date) -> list[Path]:
    window = work_window_for(run_date)
    backup_resolved = backup_folder.resolve(strict=False)
    candidates: list[Path] = []

    for item in source_folder.iterdir():
        if item.resolve(strict=False) == backup_resolved:
            continue
        if not item.is_file() or item.suffix.casefold() != ".indd":
            continue
        try:
            modified = datetime.fromtimestamp(item.stat().st_mtime)
        except OSError as exc:
            LOGGER.error("No se pudo inspeccionar %s: %s", item, exc)
            continue
        if window.start <= modified <= window.end:
            candidates.append(item)

    return sorted(candidates, key=lambda path: path.name.casefold())


def safe_destination(destination_folder: Path, name: str) -> Path:
    target = destination_folder / name
    if not target.exists():
        return target

    path = Path(name)
    stem, suffix = path.stem, path.suffix
    counter = 1
    while True:
        candidate = destination_folder / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def process_backup(
    source_folder: Path,
    backup_folder: Path,
    run_date: date,
    *,
    dry_run: bool = False,
    now: datetime | None = None,
    idle_minutes: int = 120,
) -> MoveSummary:
    summary = MoveSummary()

    if not source_folder.exists() or not source_folder.is_dir():
        raise FileNotFoundError(f"La carpeta de origen no existe: {source_folder}")

    now = now or datetime.now().astimezone().replace(tzinfo=None)
    backup_folder.mkdir(parents=True, exist_ok=True)

    if not source_is_idle(source_folder, backup_folder, now, idle_minutes):
        LOGGER.info("Omisión: la carpeta de origen aún tuvo actividad en los últimos %d minutos", idle_minutes)
        summary.skipped += 1
        return summary

    destination = dated_destination(backup_folder, run_date)
    candidates = candidate_indesign_files(source_folder, backup_folder, run_date)

    if not candidates:
        LOGGER.info("Sin archivos .indd elegibles para %s", run_date.strftime("%d-%m-%Y"))
        return summary

    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)

    for source in candidates:
        try:
            target = safe_destination(destination, source.name)
            if dry_run:
                LOGGER.info("DRY-RUN: %s -> %s", source, target)
                summary.skipped += 1
                continue

            shutil.move(str(source), str(target))
            LOGGER.info("Movido: %s -> %s", source, target)
            summary.moved += 1
        except Exception as exc:
            LOGGER.error("Error moviendo %s: %s", source, exc)
            summary.errors += 1

    return summary
