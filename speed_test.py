#!/usr/bin/env python3
"""Измеритель скорости интернета: последовательно скачивает файл по URL N раз
и печатает среднее время запроса, объём скачанных данных и скорость в МБ/с.
"""

import argparse
import sys
import time
from dataclasses import dataclass

import requests

CHUNK_SIZE = 64 * 1024  # 64 КБ
BYTES_IN_MB = 1_000_000  # 1 МБ = 10^6 байт


@dataclass
class RequestResult:
    duration: float  # секунды
    bytes_downloaded: int


def download_once(url: str, timeout: float) -> RequestResult:
    start = time.perf_counter()
    bytes_downloaded = 0
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            bytes_downloaded += len(chunk)
    duration = time.perf_counter() - start
    return RequestResult(duration=duration, bytes_downloaded=bytes_downloaded)


def run_speed_test(url: str, count: int, timeout: float) -> list[RequestResult]:
    results = []
    for i in range(1, count + 1):
        result = download_once(url, timeout)
        speed_mbps = (result.bytes_downloaded / BYTES_IN_MB) / result.duration if result.duration > 0 else 0.0
        print(
            f"Запрос {i}/{count}: {result.bytes_downloaded / BYTES_IN_MB:.2f} МБ "
            f"за {result.duration:.2f} с ({speed_mbps:.2f} МБ/с)"
        )
        results.append(result)
    return results


def summarize(results: list[RequestResult]) -> None:
    total_bytes = sum(r.bytes_downloaded for r in results)
    total_time = sum(r.duration for r in results)
    avg_time = total_time / len(results)
    avg_speed_mbps = (total_bytes / BYTES_IN_MB) / total_time if total_time > 0 else 0.0

    print("\n--- Итог ---")
    print(f"Всего скачано: {total_bytes / BYTES_IN_MB:.2f} МБ")
    print(f"Среднее время запроса: {avg_time:.2f} с")
    print(f"Средняя скорость скачивания: {avg_speed_mbps:.2f} МБ/с")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Измеряет скорость интернета последовательными запросами к указанному URL."
    )
    parser.add_argument("url", help="Адрес файла (например, большой картинки) для скачивания")
    parser.add_argument("--count", type=int, default=10, help="Количество запросов (по умолчанию 10)")
    parser.add_argument("--timeout", type=float, default=30.0, help="Таймаут одного запроса в секундах")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        results = run_speed_test(args.url, args.count, args.timeout)
    except requests.RequestException as exc:
        print(f"Ошибка запроса: {exc}", file=sys.stderr)
        return 1
    summarize(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
