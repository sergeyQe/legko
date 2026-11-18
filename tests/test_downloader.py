"""Тесты HttpDownloader на локальном HTTP-сервере (без внешней сети)."""
import pytest

from conftest import IMAGE_BYTES
from downloader import DownloadError, HttpDownloader


def test_downloads_full_image_and_measures_time(server_url):
    # Маленький chunk_size заставляет читать картинку несколькими порциями
    with HttpDownloader(timeout_s=5, chunk_size=1024) as downloader:
        result = downloader.download(f"{server_url}/image.jpg")

    assert result.size_bytes == len(IMAGE_BYTES)
    assert result.duration_s > 0


def test_http_error_status_raises_download_error(server_url):
    with HttpDownloader(timeout_s=5) as downloader:
        with pytest.raises(DownloadError):
            downloader.download(f"{server_url}/missing")


def test_unreachable_host_raises_download_error():
    # Порт 1 на localhost практически всегда закрыт
    with HttpDownloader(timeout_s=2) as downloader:
        with pytest.raises(DownloadError):
            downloader.download("http://127.0.0.1:1/")
