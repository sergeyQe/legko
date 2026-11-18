"""Общие фикстуры тестов: локальный HTTP-сервер с тестовой картинкой."""
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

# Тестовая картинка, которую отдаёт сервер
IMAGE_PATH = Path(__file__).parent / "data" / "test_image.jpg"
IMAGE_BYTES = IMAGE_PATH.read_bytes()


class _ImageHandler(BaseHTTPRequestHandler):
    """Отдаёт картинку по /image.jpg и 404 на всё остальное."""

    def do_GET(self):
        if self.path == "/image.jpg":
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(IMAGE_BYTES)))
            self.end_headers()
            self.wfile.write(IMAGE_BYTES)
        else:
            self.send_error(404)

    def log_message(self, *args):
        # Не засоряем вывод тестов логом сервера
        pass


@pytest.fixture
def server_url():
    """Поднять сервер на свободном порту и остановить после теста."""
    server = HTTPServer(("127.0.0.1", 0), _ImageHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
