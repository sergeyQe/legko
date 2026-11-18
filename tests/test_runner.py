"""Тесты SpeedTestRunner на подменном Downloader."""
import pytest

from downloader import DownloadError, Downloader
from models import RequestResult
from runner import SpeedTestRunner


class FakeDownloader(Downloader):
    """Загрузчик-заглушка: считает вызовы, может падать на заданном по счёту запросе."""

    def __init__(self, fail_at: int | None = None) -> None:
        self.calls = 0
        self._fail_at = fail_at

    def download(self, url: str) -> RequestResult:
        self.calls += 1
        if self.calls == self._fail_at:
            raise DownloadError("сбой")
        # Время и размер зависят от номера вызова, чтобы проверить порядок результатов
        return RequestResult(duration_s=float(self.calls), size_bytes=self.calls * 10)


def test_runs_exactly_n_requests_in_order():
    downloader = FakeDownloader()

    results = SpeedTestRunner(downloader, count=10).run("http://example.test")

    assert downloader.calls == 10
    assert [r.duration_s for r in results] == [float(i) for i in range(1, 11)]


def test_progress_callback_called_for_each_request():
    progress = []

    SpeedTestRunner(FakeDownloader(), count=3).run(
        "http://example.test", on_progress=lambda i, total, r: progress.append((i, total))
    )

    assert progress == [(1, 3), (2, 3), (3, 3)]


def test_aborts_on_download_error():
    downloader = FakeDownloader(fail_at=3)

    with pytest.raises(DownloadError):
        SpeedTestRunner(downloader, count=10).run("http://example.test")

    # После сбоя на 3-м запросе остальные не выполняются
    assert downloader.calls == 3


def test_count_below_one_is_rejected():
    with pytest.raises(ValueError):
        SpeedTestRunner(FakeDownloader(), count=0)
