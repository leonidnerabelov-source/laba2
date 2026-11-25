from abc import ABC, abstractmethod


class DateSourceRepository(ABC):
    """Абстрактный источник данных для поиска дат (файл, веб-страница и т.д.)."""

    @abstractmethod
    def load_content(self, source: str) -> str:
        """Загружает текстовое или HTML-содержимое из указанного источника."""
        pass
