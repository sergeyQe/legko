"""Тесты StatsCalculator: формулы на фиксированных данных."""
import pytest

from calculator import StatsCalculator
from models import RequestResult


def test_calculates_average_total_and_speed():
    # 1 МБ за 1 с и 3 МБ за 3 с: 4 МБ за 4 с = 8 Мбит/с
    results = [RequestResult(1.0, 1_000_000), RequestResult(3.0, 3_000_000)]

    report = StatsCalculator().calculate(results)

    assert report.requests_count == 2
    assert report.avg_time_s == pytest.approx(2.0)
    assert report.total_bytes == 4_000_000
    assert report.total_time_s == pytest.approx(4.0)
    assert report.speed_mbps == pytest.approx(8.0)


def test_speed_is_total_bytes_over_total_time_not_mean_of_speeds():
    # Средние скоростей: (8 + 80) / 2 = 44 Мбит/с, а верный итог — 9 МБ за 1.1 с
    results = [RequestResult(1.0, 1_000_000), RequestResult(0.1, 1_000_000)]

    report = StatsCalculator().calculate(results)

    assert report.speed_mbps == pytest.approx(2_000_000 * 8 / 1.1 / 1_000_000)


def test_empty_results_raise_value_error():
    with pytest.raises(ValueError):
        StatsCalculator().calculate([])


def test_zero_total_time_raises_value_error():
    with pytest.raises(ValueError):
        StatsCalculator().calculate([RequestResult(0.0, 100)])
