from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

from config import load_settings
from file_mover import process_backup


def parse_date(value: str):
    try:
        return datetime.strptime(value, "%d-%m-%Y").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("La fecha debe usar DD-MM-AAAA") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Organiza respaldos InDesign de una jornada nocturna.")
    parser.add_argument("--dry-run", action="store_true", help="Simula la ejecución sin mover archivos.")
    parser.add_argument("--date", type=parse_date, help="Fecha de cierre en formato DD-MM-AAAA.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        settings = load_settings()
    except ValueError as exc:
        print(f"Error de configuración: {exc}", file=sys.stderr)
        return 2

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    run_date = args.date or datetime.now().astimezone().date()

    try:
        summary = process_backup(
            settings.source_folder,
            settings.backup_folder,
            run_date,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as exc:
        logging.error("%s", exc)
        return 2
    except Exception:
        logging.exception("Error fatal inesperado")
        return 3

    logging.info(
        "Resumen | movidos=%d omitidos=%d errores=%d",
        summary.moved,
        summary.skipped,
        summary.errors,
    )
    return 1 if summary.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
