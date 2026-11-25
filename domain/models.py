from dataclasses import dataclass


@dataclass
class DateMatch:
    """Найденная или проверенная дата в формате ДД.ММ.ГГГГ."""

    value: str
    is_valid: bool
    reason: str = ""
