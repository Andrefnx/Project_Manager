from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

import pytest

from src.file_mover import dated_destination, process_backup, safe_destination


def set_mtime(path: Path, value: datetime) -> None:
    timestamp = value.timestamp()
    os.utime(path, (timestamp, timestamp))


def test_moves_only_indd_from_night_shift(tmp_path: Path) -> None:
    source = tmp_path / "Paginas diario"
    backup = source / "respaldo"
    source.mkdir()

    eligible = source / "edicion.indd"
    ignored_pdf = source / "edicion.pdf"
    old_indd = source / "antiguo.indd"
    eligible.write_text("demo")
    ignored_pdf.write_text("demo")
    old_indd.write_text("demo")

    set_mtime(eligible, datetime(2026, 8, 17, 4, 0))
    set_mtime(ignored_pdf, datetime(2026, 8, 17, 4, 0))
    set_mtime(old_indd, datetime(2026, 8, 16, 18, 0))

    summary = process_backup(
        source,
        backup,
        date(2026, 8, 17),
        now=datetime(2026, 8, 17, 7, 0),
    )

    assert summary.moved == 1
    assert (backup / "agosto" / "17" / "edicion.indd").exists()
    assert ignored_pdf.exists()
    assert old_indd.exists()


def test_waits_for_two_hours_without_activity(tmp_path: Path) -> None:
    source = tmp_path / "source"
    backup = source / "respaldo"
    source.mkdir()
    file = source / "pagina.indd"
    file.write_text("demo")
    set_mtime(file, datetime(2026, 8, 17, 5, 30))

    summary = process_backup(
        source,
        backup,
        date(2026, 8, 17),
        now=datetime(2026, 8, 17, 7, 0),
    )

    assert summary.moved == 0
    assert summary.skipped == 1
    assert file.exists()


def test_dry_run_does_not_move_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    backup = source / "respaldo"
    source.mkdir()
    file = source / "pagina.indd"
    file.write_text("demo")
    set_mtime(file, datetime(2026, 8, 17, 4, 0))

    summary = process_backup(
        source,
        backup,
        date(2026, 8, 17),
        dry_run=True,
        now=datetime(2026, 8, 17, 7, 0),
    )

    assert summary.moved == 0
    assert summary.skipped == 1
    assert file.exists()
    assert not (backup / "agosto" / "17").exists()


def test_safe_destination_adds_suffix(tmp_path: Path) -> None:
    tmp_path.joinpath("pagina.indd").write_text("uno")
    tmp_path.joinpath("pagina (1).indd").write_text("dos")
    assert safe_destination(tmp_path, "pagina.indd").name == "pagina (2).indd"


def test_missing_source_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        process_backup(
            tmp_path / "missing",
            tmp_path / "backup",
            date(2026, 8, 17),
            now=datetime(2026, 8, 17, 7, 0),
        )


def test_destination_uses_spanish_month_and_close_day(tmp_path: Path) -> None:
    assert dated_destination(tmp_path, date(2026, 8, 17)) == tmp_path / "agosto" / "17"
