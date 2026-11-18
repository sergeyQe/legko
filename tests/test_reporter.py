"""Тесты ConsoleReporter: формат вывода."""
from models import RequestResult, SpeedReport
from reporter import ConsoleReporter


def test_request_line_has_thousands_separators(capsys):
    ConsoleReporter().request_done(1, 10, RequestResult(0.8412, 2_450_112))

    assert capsys.readouterr().out.strip() == "Запрос 1/10: 0.84 с, 2 450 112 байт"


def test_report_prints_average_volume_and_speed(capsys):
    ConsoleReporter().report(SpeedReport(10, 0.81, 23_370_000, 8.1, 28.9))

    out = capsys.readouterr().out
    assert "Среднее время запроса : 0.81 с" in out
    assert "Общий объём           : 23.37 МБ" in out
    assert "Скорость скачивания   : 28.90 Мбит/с" in out
