"""Настройка логирования."""
import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(verbosity: int) -> None:
    """Настроить корневой логгер: вывод в stderr, чтобы не смешиваться с отчётом в stdout.

    Args:
        verbosity: 0 — WARNING, 1 — INFO, 2 и выше — DEBUG.
    """
    # Уровень выбираем по количеству флагов -v
    level = {0: logging.WARNING, 1: logging.INFO}.get(verbosity, logging.DEBUG)
    logging.basicConfig(level=level, format=LOG_FORMAT, stream=sys.stderr)
