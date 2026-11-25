from datetime import datetime
import re

from domain.exceptions import DateValidationError
from domain.models import DateMatch
from domain.repository import DateSourceRepository


class DateService:

    CANDIDATE_PATTERN = re.compile(
        r"(?<!\d)(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})(?!\d)"
    )
    STRICT_FORMAT_PATTERN = re.compile(
        r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(\d{4})$"
    )

    def __init__(self, source_repo: DateSourceRepository | None = None) -> None:
        self._source_repo = source_repo

    def validate_date(self, date_str: str) -> bool:
        """Проверяет, является ли строка корректной датой в формате ДД.ММ.ГГГГ."""
        if not isinstance(date_str, str):
            raise DateValidationError("Дата должна быть строкой", "date")

        cleaned = date_str.strip()
        if not cleaned:
            raise DateValidationError("Строка с датой не может быть пустой", "date")

        if not self.STRICT_FORMAT_PATTERN.fullmatch(cleaned):
            return False

        return self._is_real_calendar_date(cleaned)

    def find_valid_dates(self, text: str) -> list[str]:
        """Находит в тексте все синтаксически и календарно корректные даты ДД.ММ.ГГГГ."""
        if not isinstance(text, str):
            raise DateValidationError("Текст должен быть строкой", "text")

        found: list[str] = []
        for match in self.CANDIDATE_PATTERN.finditer(text):
            candidate = match.group(0)
            if self._is_real_calendar_date(candidate):
                found.append(candidate)
        return found

    def find_in_source(self, source: str) -> list[str]:
        """Загружает данные из файла или URL через репозиторий и ищет корректные даты."""
        if self._source_repo is None:
            raise DateValidationError("Источник данных не настроен", "source_repo")
        content = self._source_repo.load_content(source)
        return self.find_valid_dates(content)

    def scan_text(self, text: str) -> list[DateMatch]:
        """Возвращает подробный список найденных шаблонов ДД.ММ.ГГГГ с оценкой корректности."""
        if not isinstance(text, str):
            raise DateValidationError("Текст должен быть строкой", "text")

        results: list[DateMatch] = []
        for match in self.CANDIDATE_PATTERN.finditer(text):
            candidate = match.group(0)
            if self._is_real_calendar_date(candidate):
                results.append(DateMatch(value=candidate, is_valid=True, reason="Корректная дата"))
            else:
                results.append(
                    DateMatch(
                        value=candidate,
                        is_valid=False,
                        reason="Некорректный день, месяц или високосный год",
                    )
                )
        return results

    @staticmethod
    def _is_real_calendar_date(date_str: str) -> bool:
        """Проверяет реальное существование даты по григорианскому календарю."""
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False
