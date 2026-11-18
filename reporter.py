"""Вывод результатов замера.

Абстракция Reporter отделяет формат вывода от логики замера: чтобы добавить
JSON или запись в файл, достаточно написать новую реализацию (OCP).
"""
import sys
from abc import ABC, abstractmethod
from typing import TextIO

from models import RequestResult, SpeedReport

# Байт в мегабайте (1 МБ = 10^6 байт, как и 1 Мбит = 10^6 бит)
BYTES_IN_MEGABYTE = 1_000_000


class Reporter(ABC):
    """Абстракция вывода: прогресс по запросам и итоговый отчёт."""

    @abstractmethod
    def request_done(self, index: int, total: int, result: RequestResult) -> None:
        """Сообщить о завершении одного запроса."""

    @abstractmethod
    def report(self, report: SpeedReport) -> None:
        """Вывести итоговый отчёт."""


class ConsoleReporter(Reporter):
    """Печатает прогресс и итог в консоль (по умолчанию в stdout)."""

    def __init__(self, stream: TextIO | None = None) -> None:
        """
        Args:
            stream: поток вывода; по умолчанию sys.stdout (определяется в момент вызова).
        """
        self._stream = stream

    def request_done(self, index: int, total: int, result: RequestResult) -> None:
        """Напечатать строку по одному запросу."""
        self._print(
            f"Запрос {index}/{total}: {result.duration_s:.2f} с, "
            f"{self._format_int(result.size_bytes)} байт"
        )

    def report(self, report: SpeedReport) -> None:
        """Напечатать итог: среднее время, общий объём и скорость."""
        total_mb = report.total_bytes / BYTES_IN_MEGABYTE
        self._print("-" * 40)
        self._print(f"Среднее время запроса : {report.avg_time_s:.2f} с")
        self._print(f"Общий объём           : {total_mb:.2f} МБ")
        self._print(f"Скорость скачивания   : {report.speed_mbps:.2f} Мбит/с")

    def _print(self, text: str) -> None:
        """Вывести строку в выбранный поток."""
        print(text, file=self._stream or sys.stdout)

    @staticmethod
    def _format_int(value: int) -> str:
        """Число с пробелом как разделителем тысяч: 2450112 -> '2 450 112'."""
        return f"{value:,}".replace(",", " ")
