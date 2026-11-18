"""Последовательное выполнение серии запросов."""
import logging
from collections.abc import Callable

from downloader import DownloadError, Downloader
from models import RequestResult

logger = logging.getLogger(__name__)

# Колбэк прогресса: (номер запроса, всего запросов, результат)
ProgressCallback = Callable[[int, int, RequestResult], None]


class SpeedTestRunner:
    """Выполняет N запросов строго по очереди через переданный Downloader.

    Зависит от абстракции Downloader, а не от конкретной реализации (DIP),
    и сам ничего не печатает — прогресс отдаётся через колбэк (SRP).
    """

    def __init__(self, downloader: Downloader, count: int) -> None:
        """
        Args:
            downloader: загрузчик, выполняющий один запрос.
            count: сколько запросов выполнить (не меньше 1).

        Raises:
            ValueError: если count меньше 1.
        """
        if count < 1:
            raise ValueError("Количество запросов должно быть не меньше 1")
        self._downloader = downloader
        self._count = count

    def run(self, url: str, on_progress: ProgressCallback | None = None) -> list[RequestResult]:
        """Выполнить серию запросов к url и вернуть результаты в порядке выполнения.

        Raises:
            DownloadError: при первой же ошибке запроса — замер прерывается.
        """
        logger.info("Старт замера (запросов: %d): %s", self._count, url)
        results: list[RequestResult] = []

        # Запросы идут строго последовательно: следующий — после полного ответа на предыдущий
        for index in range(1, self._count + 1):
            try:
                result = self._downloader.download(url)
            except DownloadError:
                logger.error("Запрос %d/%d не удался, замер прерван", index, self._count)
                raise
            results.append(result)
            # Сообщаем о прогрессе, если подписчик есть
            if on_progress is not None:
                on_progress(index, self._count, result)

        logger.info("Замер завершён (выполнено запросов: %d)", len(results))
        return results
