from pathlib import Path
import requests

from domain.exceptions import SourceFetchError
from domain.repository import DateSourceRepository


class WebAndFileSourceRepository(DateSourceRepository):
    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def load_content(self, source: str) -> str:
        cleaned = source.strip()
        if cleaned.startswith(("http://", "https://")):
            return self._load_from_url(cleaned)
        return self._load_from_file(cleaned)

    def _load_from_file(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise SourceFetchError(f"Файл не найден: {path}")
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SourceFetchError(f"Ошибка чтения файла {path}: {exc}") from exc

    def _load_from_url(self, url: str) -> str:
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={"User-Agent": "Mozilla/5.0 (DateLab2Bot/1.0)"},
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding or "utf-8"
            return response.text
        except requests.RequestException as exc:
            raise SourceFetchError(f"Ошибка загрузки страницы {url}: {exc}") from exc
