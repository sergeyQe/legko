"""Разбор аргументов командной строки."""
import argparse
from dataclasses import dataclass
from urllib.parse import urlparse

# Значения по умолчанию по ТЗ: 10 запросов, таймаут 30 секунд
DEFAULT_COUNT = 10
DEFAULT_TIMEOUT_S = 30.0


@dataclass(frozen=True)
class Settings:
    """Настройки запуска, полученные из командной строки.

    Attributes:
        url: адрес, к которому стучимся.
        count: количество последовательных запросов.
        timeout_s: таймаут сокета на запрос, секунды.
        verbosity: уровень подробности логов: 0 — только предупреждения, 1 — INFO, 2 — DEBUG.
    """

    url: str
    count: int
    timeout_s: float
    verbosity: int


def _url(value: str) -> str:
    """Проверить, что значение — http/https URL с хостом."""
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise argparse.ArgumentTypeError(f"ожидается http(s)-адрес, получено: {value!r}")
    return value


def _positive_int(value: str) -> int:
    """Целое число не меньше 1."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"ожидается целое число, получено: {value!r}") from None
    if number < 1:
        raise argparse.ArgumentTypeError("значение должно быть не меньше 1")
    return number


def _positive_float(value: str) -> float:
    """Число больше нуля."""
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"ожидается число, получено: {value!r}") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("значение должно быть больше 0")
    return number


def build_parser() -> argparse.ArgumentParser:
    """Собрать парсер аргументов."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Замер скорости скачивания: последовательные запросы к одному адресу.",
    )
    parser.add_argument("url", type=_url, help="адрес для запросов, например ссылка на тяжёлую картинку")
    parser.add_argument(
        "--count", type=_positive_int, default=DEFAULT_COUNT,
        help=f"количество запросов (по умолчанию {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--timeout", type=_positive_float, default=DEFAULT_TIMEOUT_S,
        help=f"таймаут сокета на запрос, секунды (по умолчанию {DEFAULT_TIMEOUT_S:g})",
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0,
        help="подробные логи в stderr: -v — INFO, -vv — DEBUG",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> Settings:
    """Разобрать аргументы; при ошибке argparse завершает процесс с кодом 2."""
    args = build_parser().parse_args(argv)
    return Settings(url=args.url, count=args.count, timeout_s=args.timeout, verbosity=args.verbose)
