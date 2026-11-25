from application.date_service import DateService
from infrastructure.web_fetcher import WebAndFileSourceRepository
from presentation.console import ConsoleApp


def main() -> None:
    source_repo = WebAndFileSourceRepository(timeout=10)
    service = DateService(source_repo=source_repo)
    app = ConsoleApp(service=service)
    app.run()


if __name__ == "__main__":
    main()
