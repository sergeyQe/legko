"""Модели данных замера скорости.

Только неизменяемые контейнеры без логики: результат одного запроса
и итоговый отчёт по всей серии запросов.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestResult:
    """Результат одного выполненного запроса.

    Attributes:
        duration_s: время от старта запроса до полного чтения тела ответа, секунды.
        size_bytes: размер прочитанного тела ответа, байты.
    """

    duration_s: float
    size_bytes: int


@dataclass(frozen=True)
class SpeedReport:
    """Итоговый отчёт по серии запросов.

    Attributes:
        requests_count: количество выполненных запросов.
        avg_time_s: среднее время одного запроса, секунды.
        total_bytes: общий объём скачанных данных, байты.
        total_time_s: суммарное время всех запросов, секунды.
        speed_mbps: скорость скачивания, мегабиты в секунду (1 Мбит = 10^6 бит).
    """

    requests_count: int
    avg_time_s: float
    total_bytes: int
    total_time_s: float
    speed_mbps: float
