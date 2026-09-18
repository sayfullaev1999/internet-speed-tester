import unittest
from unittest.mock import patch

from speed_test import RequestResult, summarize


class SummarizeTests(unittest.TestCase):
    def test_average_time_and_speed(self):
        results = [
            RequestResult(duration=1.0, bytes_downloaded=1_000_000),
            RequestResult(duration=2.0, bytes_downloaded=3_000_000),
        ]

        with patch("builtins.print") as mock_print:
            summarize(results)

        printed = "\n".join(call.args[0] for call in mock_print.call_args_list)
        self.assertIn("Всего скачано: 4.00 МБ", printed)
        self.assertIn("Среднее время запроса: 1.50 с", printed)
        self.assertIn("Средняя скорость скачивания: 1.33 МБ/с", printed)


if __name__ == "__main__":
    unittest.main()
