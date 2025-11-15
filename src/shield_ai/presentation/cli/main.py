"""
CLI интерфейс для основных операций приложения Shield AI.

Этот модуль предоставляет командный интерфейс для выполнения следующих операций:
- Парсинг Excel-файлов с данными о движении товаров
- Расчет усушки
- Аудит остатков
- Экспорт результатов в различные форматы
"""

import argparse
import sys
import traceback
from typing import (
    Any,
    List,
    Tuple,
)

from src.shield_ai.application.use_cases.audit_inventory import (
    AuditInventoryUseCase,
)
from src.shield_ai.application.use_cases.forecast_shrinkage import (
    ForecastShrinkageUseCase,
)
from src.shield_ai.domain.entities.batch import (
    BatchBalance,
    BatchMovement,
)
from src.shield_ai.infrastructure.exporters.json_exporter import (
    JsonExporter,
)
from src.shield_ai.infrastructure.exporters.markdown_exporter import (
    MarkdownExporter,
)
from src.shield_ai.infrastructure.exporters.sqlite_exporter import (
    SQLiteExporter,
)
from src.shield_ai.infrastructure.logging_config import (
    configure_logging,
    get_logger,
)
from src.shield_ai.infrastructure.parsers.inventory_parser import (
    InventoryParser,
)


def setup_logging() -> None:
    """Настройка логирования."""
    configure_logging()


def get_logger_instance() -> Any:
    """Получение экземпляра логгера."""
    return get_logger(__name__)


def load_data_from_file(
    file_path: str,
) -> Tuple[List[BatchMovement], List[BatchBalance]]:
    """Загрузка данных из Excel файла."""
    parser = InventoryParser()
    movements, balances = parser.parse_excel(file_path)
    return movements, balances


def parse_command(args: argparse.Namespace) -> None:
    """Команда для парсинга Excel-файла."""
    logger = get_logger_instance()
    logger.info("Начало парсинга Excel-файла", file_path=args.file_path)

    try:
        movements, balances = load_data_from_file(args.file_path)

        print(f"Парсинг завершён успешно!")
        print(f"Найдено {len(movements)} записей BatchMovement")
        print(f"Найдено {len(balances)} записей BatchBalance")

        logger.info(
            "Парсинг завершён",
            movements_count=len(movements),
            balances_count=len(balances),
        )
    except Exception as e:
        logger.error("Ошибка при парсинге файла", error=str(e))
        print(f"Ошибка при парсинге файла: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


def calculate_shrinkage_command(args: argparse.Namespace) -> None:
    """Команда для расчета усушки."""
    logger = get_logger_instance()
    logger.info("Начало расчета усушки", file_path=args.file_path)

    try:
        # Загружаем данные из файла
        movements, balances = load_data_from_file(args.file_path)

        logger.info(
            "Данные для расчета усушки загружены",
            movements_count=len(movements),
            balances_count=len(balances),
        )

        # Выполняем расчет усушки
        use_case = ForecastShrinkageUseCase()
        results = use_case.execute(movements, balances)

        print(f"Расчет усушки завершён!")
        print(f"Получено {len(results)} результатов расчета")

        if args.verbose:
            for result in results:
                print(
                    f"- {result.nomenclature}: усушка={result.calculated_shrinkage}, остаток={result.actual_balance}, отклонение={result.deviation}"
                )

        logger.info("Расчет усушки завершён", results_count=len(results))

    except Exception as e:
        logger.error("Ошибка при расчете усушки", error=str(e))
        print(f"Ошибка при расчете усушки: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


def audit_command(args: argparse.Namespace) -> None:
    """Команда для аудита остатков."""
    logger = get_logger_instance()
    logger.info("Начало аудита остатков", file_path=args.file_path)

    try:
        # Загружаем данные из файла
        movements, balances = load_data_from_file(args.file_path)

        logger.info(
            "Данные для аудита остатков загружены",
            movements_count=len(movements),
            balances_count=len(balances),
        )

        # Выполняем аудит
        use_case = AuditInventoryUseCase()
        negative_balances = use_case.execute(balances)

        print(f"Аудит остатков завершён!")
        print(f"Найдено {len(negative_balances)} записей с отрицательными остатками")

        if negative_balances:
            print("Отрицательные остатки:")
            for balance in negative_balances:
                print(
                    f"- {balance.nomenclature} (партия {balance.batch}): {balance.balance}"
                )
        else:
            print("Отрицательных остатков не обнаружено")

        logger.info(
            "Аудит остатков завершён",
            negative_count=len(negative_balances),
            total_count=len(balances),
        )

    except Exception as e:
        logger.error("Ошибка при аудите остатков", error=str(e))
        print(f"Ошибка при аудите остатков: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


def export_command(args: argparse.Namespace) -> None:
    """Команда для экспорта результатов."""
    logger = get_logger_instance()
    logger.info(
        "Начало экспорта",
        file_path=args.file_path,
        format=args.format,
        output_path=args.output,
    )

    try:
        # Загружаем данные из файла
        movements, balances = load_data_from_file(args.file_path)

        logger.info(
            "Данные для экспорта загружены",
            movements_count=len(movements),
            balances_count=len(balances),
        )

        # Выполняем расчет усушки для получения данных для экспорта
        use_case = ForecastShrinkageUseCase()
        results = use_case.execute(movements, balances)

        # Определяем экспортер в зависимости от формата
        exporter = None
        if args.format.lower() == "json":
            exporter = JsonExporter()
        elif args.format.lower() == "markdown":
            exporter = MarkdownExporter()
        elif args.format.lower() == "sqlite":
            exporter = SQLiteExporter()
        else:
            raise ValueError(f"Неподдерживаемый формат экспорта: {args.format}")

        # Выполняем экспорт
        exporter.export(results, args.output)

        print(f"Экспорт в формат {args.format} завершён успешно!")
        print(f"Файл сохранён: {args.output}")

        logger.info("Экспорт завершён", format=args.format, output_path=args.output)

    except Exception as e:
        logger.error("Ошибка при экспорте", error=str(e))
        print(f"Ошибка при экспорте: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Создание парсера аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Shield AI CLI - инструмент для анализа и прогнозирования усушки товаров",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Добавляем аргумент для verbose режима
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Включить подробный вывод"
    )

    # Создаем подкоманды
    subparsers = parser.add_subparsers(
        dest="command", help="Доступные команды", required=True
    )

    # Команда parse
    parse_parser = subparsers.add_parser(
        "parse", help="Парсинг Excel-файла с данными о движении товаров"
    )
    parse_parser.add_argument(
        "file_path", type=str, help="Путь к Excel-файлу для парсинга"
    )
    parse_parser.set_defaults(func=parse_command)

    # Команда calculate_shrinkage
    calculate_parser = subparsers.add_parser(
        "calculate_shrinkage", help="Расчет усушки на основе данных из Excel-файла"
    )
    calculate_parser.add_argument(
        "file_path", type=str, help="Путь к Excel-файлу с данными"
    )
    calculate_parser.set_defaults(func=calculate_shrinkage_command)

    # Команда audit
    audit_parser = subparsers.add_parser(
        "audit", help="Аудит остатков на наличие отрицательных значений"
    )
    audit_parser.add_argument(
        "file_path", type=str, help="Путь к Excel-файлу с данными"
    )
    audit_parser.set_defaults(func=audit_command)

    # Команда export
    export_parser = subparsers.add_parser(
        "export", help="Экспорт результатов в указанный формат"
    )
    export_parser.add_argument(
        "file_path", type=str, help="Путь к Excel-файлу с данными"
    )
    export_parser.add_argument(
        "format",
        type=str,
        choices=["json", "markdown", "sqlite"],
        help="Формат экспорта: json, markdown, sqlite",
    )
    export_parser.add_argument(
        "output", type=str, help="Путь для сохранения экспортированного файла"
    )
    export_parser.set_defaults(func=export_command)

    return parser


def main() -> None:
    """Основная функция CLI."""
    setup_logging()
    logger = get_logger_instance()

    args = None  # Инициализируем переменную args

    try:
        parser = create_parser()
        args = parser.parse_args()

        logger.info("Запуск CLI команды", command=args.command)

        # Вызываем соответствующую функцию
        args.func(args)

    except KeyboardInterrupt:
        logger.info("Операция прервана пользователем")
        print("\nОперация прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error("Неожиданная ошибка в CLI", error=str(e))
        print(f"Неожиданная ошибка: {e}")
        # Проверяем, определена ли переменная args и имеет ли она атрибут verbose
        if args and hasattr(args, "verbose") and args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
