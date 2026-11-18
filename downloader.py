"""Загрузка данных по URL и замер времени одного запроса.

Содержит абстракцию Downloader (на неё опирается раннер) и её реализацию
HttpDownloader на базе requests. Благодаря абстракции реализацию можно
подменить (например, мок в тестах) без правок остального кода.
"""
import logging
import time
from abc import ABC, abstractmethod

import requests

from models import RequestResult

logger = logging.getLogger(__name__)

# Размер порции при чтении тела ответа, байты
DEFAULT_CHUNK_SIZE = 64 * 1024

# Запрещаем отдавать ответ из кеша прокси/CDN, чтобы не завышать скорость
_NO_CACHE_HEADERS = {"Cache-Control": "no-cache"}


class DownloadError(Exception):
    """Ошибка загрузки: сеть, таймаут или неуспешный HTTP-статус."""


class Downloader(ABC):
    """Абстракция загрузчика: выполняет один запрос и возвращает его результат."""

    @abstractmethod
    def download(self, url: str) -> RequestResult:
        """Скачать url целиком и вернуть время и размер.

        Raises:
            DownloadError: если запрос не удалось выполнить.
        """


class HttpDownloader(Downloader):
    """Загрузчик по HTTP(S) на requests.

    Все запросы идут через один requests.Session, поэтому соединение
    переиспользуется: первый запрос включает DNS/TCP/TLS, последующие — нет.
    """

    def __init__(
        self,
        timeout_s: float,
        session: requests.Session | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        """
        Args:
            timeout_s: таймаут сокета (соединение и ожидание данных), секунды.
                Это не общий лимит на запрос: каждая операция ограничена отдельно.
            session: готовая сессия; если не передана, создаётся своя и закрывается в close().
            chunk_size: размер порции чтения тела, байты.
        """
        self._timeout_s = timeout_s
        self._chunk_size = chunk_size
        self._owns_session = session is None
        self._session = session or requests.Session()

    def download(self, url: str) -> RequestResult:
        """Скачать url целиком, дождавшись полного тела ответа."""
        logger.debug("Старт запроса: %s", url)
        # Монотонные часы: не зависят от перевода системного времени
        started = time.perf_counter()
        total_bytes = 0
        try:
            with self._session.get(
                url, stream=True, timeout=self._timeout_s, headers=_NO_CACHE_HEADERS
            ) as response:
                response.raise_for_status()
                logger.debug("Заголовки ответа: %s", dict(response.headers))
                # Читаем тело порциями до конца, считая байты
                for chunk in response.iter_content(chunk_size=self._chunk_size):
                    total_bytes += len(chunk)
                    logger.debug("Получена порция: %d байт", len(chunk))
        except requests.RequestException as exc:
            raise DownloadError(f"Не удалось скачать {url}: {exc}") from exc
        duration = time.perf_counter() - started

        result = RequestResult(duration_s=duration, size_bytes=total_bytes)
        logger.info("Запрос выполнен: %.3f с, %d байт", result.duration_s, result.size_bytes)
        return result

    def close(self) -> None:
        """Закрыть сессию, если она создана этим загрузчиком."""
        if self._owns_session:
            self._session.close()

    def __enter__(self) -> "HttpDownloader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
