"""Расчёт итоговых метрик по результатам запросов.

Чистая логика без ввода-вывода и логирования — легко тестируется.
"""
from models import RequestResult, SpeedReport

# Бит в байте и бит в мегабите (1 Мбит = 10^6 бит)
BITS_IN_BYTE = 8
BITS_IN_MEGABIT = 1_000_000


class StatsCalculator:
    """Считает среднее время, общий объём и скорость скачивания."""

    def calculate(self, results: list[RequestResult]) -> SpeedReport:
        """Собрать отчёт по списку результатов.

        Скорость = суммарные байты / суммарное время (в Мбит/с). Это точнее, чем
        среднее арифметическое скоростей отдельных запросов.

        Raises:
            ValueError: если список пуст или суммарное время не положительно.
        """
        # Без результатов считать нечего
        if not results:
            raise ValueError("Список результатов пуст: нечего считать")

        # Суммируем время и объём по всем запросам
        total_time = sum(r.duration_s for r in results)
        total_bytes = sum(r.size_bytes for r in results)
        if total_time <= 0:
            raise ValueError("Суммарное время должно быть положительным")

        # Среднее время и скорость в Мбит/с
        avg_time = total_time / len(results)
        speed_mbps = total_bytes * BITS_IN_BYTE / total_time / BITS_IN_MEGABIT

        return SpeedReport(
            requests_count=len(results),
            avg_time_s=avg_time,
            total_bytes=total_bytes,
            total_time_s=total_time,
            speed_mbps=speed_mbps,
        )
