import tempfile
import unittest
from unittest.mock import patch

from application.date_service import DateService
from domain.exceptions import DateValidationError, SourceFetchError
from infrastructure.web_fetcher import WebAndFileSourceRepository


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200, encoding: str = "utf-8") -> None:
        self.text = text
        self.status_code = status_code
        self.apparent_encoding = encoding
        self.encoding = encoding

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class DateServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = WebAndFileSourceRepository()
        self.service = DateService(source_repo=self.repo)

    def test_valid_dates(self):
        self.assertTrue(self.service.validate_date("01.01.2026"))
        self.assertTrue(self.service.validate_date("25.11.2026"))
        self.assertTrue(self.service.validate_date("29.02.2024"))

    def test_invalid_dates_and_formats(self):
        self.assertFalse(self.service.validate_date("29.02.2025"))
        self.assertFalse(self.service.validate_date("31.04.2026"))
        self.assertFalse(self.service.validate_date("10.13.2026"))
        self.assertFalse(self.service.validate_date("2026-11-25"))
        self.assertFalse(self.service.validate_date("5.11.2026"))

    def test_empty_date_raises_validation_error(self):
        with self.assertRaises(DateValidationError):
            self.service.validate_date("   ")

    def test_find_valid_dates_in_text(self):
        text = (
            "Отчёт сдан 15.05.2025, повторная проверка назначена на 29.02.2024. "
            "Ошибочные даты вроде 31.02.2025 и 99.99.9999 должны отсеиваться."
        )
        self.assertEqual(self.service.find_valid_dates(text), ["15.05.2025", "29.02.2024"])

    def test_scan_text_marks_valid_and_invalid(self):
        matches = self.service.scan_text("Даты: 01.09.2026 и 30.02.2026.")
        self.assertEqual(len(matches), 2)
        self.assertTrue(matches[0].is_valid)
        self.assertFalse(matches[1].is_valid)

    def test_find_in_file_and_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = f"{tmp_dir}/sample.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Приказ от 10.10.2026 и 32.01.2026")

            self.assertEqual(self.service.find_in_source(file_path), ["10.10.2026"])

        with self.assertRaises(SourceFetchError):
            self.service.find_in_source(f"{tmp_dir}/non_existent.txt")

    @patch("infrastructure.web_fetcher.requests.get")
    def test_find_in_url(self, mock_get):
        mock_get.return_value = FakeResponse(
            "<html><body><p>Дата публикации: 03.11.2026</p></body></html>"
        )
        self.assertEqual(
            self.service.find_in_source("https://example.com/news"),
            ["03.11.2026"],
        )


if __name__ == "__main__":
    unittest.main()
    # python -m unittest test.test_date_service -v
