from application.date_service import DateService
from domain.exceptions import DateValidationError, SourceFetchError


class ConsoleApp:
    """Консольный интерфейс работы с сервисом дат ДД.ММ.ГГГГ."""

    def __init__(self, service: DateService) -> None:
        self.service = service

    def run(self) -> None:
        while True:
            print("\n=== ПРОВЕРКА И ПОИСК ДАТ (ДД.ММ.ГГГГ) ===")
            print("1. Проверить одну дату (пользовательский ввод)")
            print("2. Найти даты в произвольном тексте")
            print("3. Найти даты в файле")
            print("4. Найти даты на веб-странице по URL")
            print("0. Выход")
            choice = input("Выберите действие: ").strip()

            try:
                if choice == "1":
                    self._check_single_date()
                elif choice == "2":
                    self._search_in_text()
                elif choice == "3":
                    self._search_in_file()
                elif choice == "4":
                    self._search_in_url()
                elif choice == "0":
                    print("До свидания!")
                    return
                else:
                    print("Неизвестная команда")
            except (DateValidationError, SourceFetchError) as err:
                print(f"Ошибка: {err}")
            except (EOFError, KeyboardInterrupt):
                print("\nВыход")
                return

    def _check_single_date(self) -> None:
        raw_date = input("Введите дату в формате ДД.ММ.ГГГГ: ")
        if self.service.validate_date(raw_date):
            print("Дата корректна.")
        else:
            print("Дата некорректна или не соответствует формату ДД.ММ.ГГГГ.")

    def _search_in_text(self) -> None:
        text = input("Введите текст для поиска дат: ")
        self._print_found_dates(self.service.find_valid_dates(text))

    def _search_in_file(self) -> None:
        file_path = input("Укажите путь к файлу: ").strip()
        self._print_found_dates(self.service.find_in_source(file_path))

    def _search_in_url(self) -> None:
        url = input("Введите URL страницы: ").strip()
        self._print_found_dates(self.service.find_in_source(url))

    @staticmethod
    def _print_found_dates(dates: list[str]) -> None:
        if not dates:
            print("Корректные даты в формате ДД.ММ.ГГГГ не найдены.")
            return
        print(f"Найдено дат ({len(dates)}):")
        for item in dates:
            print(f"  - {item}")
