"""Интеграционный тест точки входа на локальном сервере с тестовой картинкой."""
from conftest import IMAGE_BYTES
from main import main


def test_full_run_prints_report_and_returns_zero(server_url, capsys):
    exit_code = main([f"{server_url}/image.jpg", "--count", "3"])

    out = capsys.readouterr().out
    assert exit_code == 0
    # Три строки по запросам с размером картинки
    size = f"{len(IMAGE_BYTES):,}".replace(",", " ")
    assert out.count(f"{size} байт") == 3
    # Итоговый отчёт на месте
    assert "Среднее время запроса" in out
    assert "Скорость скачивания" in out


def test_missing_resource_returns_one(server_url, capsys):
    exit_code = main([f"{server_url}/missing", "--count", "2"])

    assert exit_code == 1
    assert "Ошибка:" in capsys.readouterr().err
