"""Тесты HttpDownloader на локальном HTTP-сервере (без внешней сети)."""
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from downloader import DownloadError, HttpDownloader

BODY = b"x" * 200_000


class _Handler(BaseHTTPRequestHandler):
    """Отдаёт тело по /ok и 404 на всё остальное."""

    def do_GET(self):
        if self.path == "/ok":
            self.send_response(200)
            self.send_header("Content-Length", str(len(BODY)))
            self.end_headers()
            self.wfile.write(BODY)
        else:
            self.send_error(404)

    def log_message(self, *args):
        # Не засоряем вывод тестов логом сервера
        pass


@pytest.fixture
def server_url():
    """Поднять сервер на свободном порту и остановить после теста."""
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def test_downloads_full_body_and_measures_time(server_url):
    with HttpDownloader(timeout_s=5, chunk_size=4096) as downloader:
        result = downloader.download(f"{server_url}/ok")

    assert result.size_bytes == len(BODY)
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
