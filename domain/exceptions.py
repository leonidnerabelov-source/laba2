class DateValidationError(ValueError):
    """Ошибка валидации даты или входных параметров."""

    def init(self, message: str, field: str | None = None) -> None:
        super().init(message)
        self.field = field


class SourceFetchError(RuntimeError):
    """Ошибка при получении данных из файла или по URL."""
