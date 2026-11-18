"""Точка входа: замер скорости скачивания.

Запуск: python main.py <url> [--count N] [--timeout S] [-v]
Коды возврата: 0 — успех, 1 — ошибка запроса, 2 — неверные аргументы, 130 — прерывание.
"""
import logging
import sys

from calculator import StatsCalculator
from cli import parse_args
from downloader import DownloadError, HttpDownloader
from logging_config import setup_logging
from reporter import ConsoleReporter
from runner import SpeedTestRunner

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Собрать зависимости, выполнить замер и вывести отчёт.

    Returns:
        Код возврата процесса.
    """
    # Разбираем аргументы и настраиваем логи
    settings = parse_args(argv)
    setup_logging(settings.verbosity)

    # Собираем объекты вручную (внедрение зависимостей)
    reporter = ConsoleReporter()
    calculator = StatsCalculator()

    try:
        # Загрузчик закрывает сессию при выходе из блока
        with HttpDownloader(settings.timeout_s) as downloader:
            runner = SpeedTestRunner(downloader, settings.count)
            results = runner.run(settings.url, on_progress=reporter.request_done)
        # Считаем и печатаем итог
        reporter.report(calculator.calculate(results))
    except DownloadError as exc:
        # Одно сообщение пользователю в stderr; детали и номер запроса уже в логах
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Прервано пользователем", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
