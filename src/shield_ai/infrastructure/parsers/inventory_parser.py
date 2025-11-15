"""
Модуль для парсинга Excel-отчётов о движении товаров.

Этот модуль предоставляет класс `InventoryParser` для преобразования
Excel-отчётов 1С о движении товаров в плоскую структуру pandas DataFrame.
"""

import logging
from datetime import (
    date,
)
from logging import (
    Logger,
)
from typing import (
    List,
    Optional,
    Tuple,
)

import pandas as pd

from src.shield_ai.domain.entities.batch import (
    BatchBalance,
    BatchMovement,
)
from src.shield_ai.domain.exceptions import (
    ParserException,
    ValidationException,
)
from src.shield_ai.infrastructure.logging_config import (
    get_logger,
)


class InventoryParser:
    """
    Парсер Excel-отчётов о движении товаров в плоскую таблицу.

    Класс реализует простой парсинг Excel-файлов с данными о движении товаров
    в плоскую структуру данных (pandas DataFrame).
    """

    def __init__(self, logger: Optional[Logger] = None):
        """
        Инициализация парсера.

        Args:
            logger (Optional[Logger]): Экземпляр логгера. Если не предоставлен, используется стандартный.
        """
        self.logger = logger or get_logger(__name__)

    def _find_column(
        self, available_columns: List[str], possible_names: List[str]
    ) -> Optional[str]:
        """
        Находит колонку в списке доступных колонок по возможным именам.

        Args:
            available_columns: Список доступных колонок в DataFrame
            possible_names: Список возможных имён колонки

        Returns:
            Название найденной колонки или None, если не найдена
        """
        return next((col for col in available_columns if col in possible_names), None)

    def _parse_date_value(self, date_raw) -> date:
        """
        Преобразует значение даты в объект date.

        Args:
            date_raw: Необработанное значение даты из Excel

        Returns:
            Объект date
        """
        if isinstance(date_raw, pd.Timestamp):
            return date_raw.date()
        elif isinstance(date_raw, date):
            return date_raw
        elif isinstance(date_raw, str):
            # Попробуем преобразовать строку в дату
            try:
                date_parsed = pd.to_datetime(date_raw)
                return date_parsed.date()
            except Exception as date_error:
                self.logger.warning(
                    f"Не удалось преобразовать дату '{date_raw}': {date_error}"
                )
                return date.today()  # fallback
        else:
            return date.today()  # fallback

    def _parse_quantity_value(self, qty_raw) -> float:
        """
        Преобразует значение количества в число с плавающей точкой.

        Args:
            qty_raw: Необработанное значение количества из Excel

        Returns:
            Число с плавающей точкой
        """
        try:
            return float(qty_raw)
        except (ValueError, TypeError):
            self.logger.warning(
                f"Не удалось преобразовать количество '{qty_raw}' в число, используем 0.0"
            )
            return 0.0  # fallback

    def _process_row(
        self,
        row,
        idx,
        nomenclature_col: Optional[str],
        batch_col: Optional[str],
        movement_type_col: Optional[str],
        warehouse_col: Optional[str],
        date_col: Optional[str],
        quantity_col: Optional[str],
    ) -> Tuple[BatchMovement, BatchBalance]:
        """
        Обрабатывает одну строку данных и создает объекты BatchMovement и BatchBalance.

        Args:
            row: Строка данных из DataFrame
            idx: Индекс строки для логирования ошибок (может быть любым хешируемым типом)
            nomenclature_col: Имя колонки номенклатуры
            batch_col: Имя колонки партии
            movement_type_col: Имя колонки типа движения
            warehouse_col: Имя колонки склада
            date_col: Имя колонки даты
            quantity_col: Имя колонки количества

        Returns:
            Кортеж из BatchMovement и BatchBalance
        """
        # Извлекаем значения из строки, используя найденные колонки
        nomenclature = (
            str(row[nomenclature_col])
            if nomenclature_col and nomenclature_col in row
            else ""
        )
        batch = str(row[batch_col]) if batch_col and batch_col in row else ""
        movement_type = (
            str(row[movement_type_col])
            if movement_type_col and movement_type_col in row
            else ""
        )
        warehouse = (
            str(row[warehouse_col]) if warehouse_col and warehouse_col in row else ""
        )

        # Обработка даты
        date_val = date.today()  # fallback по умолчанию
        if date_col and date_col in row:
            date_raw = row[date_col]
            date_val = self._parse_date_value(date_raw)

        # Обработка количества
        quantity = 0.0  # fallback по умолчанию
        if quantity_col and quantity_col in row:
            qty_raw = row[quantity_col]
            quantity = self._parse_quantity_value(qty_raw)

        # Создаем объект BatchMovement
        movement = BatchMovement(
            nomenclature=nomenclature,
            date=date_val,
            movement_type=movement_type,
            quantity=quantity,
            warehouse=warehouse,
        )

        # Создаем объект BatchBalance
        balance = BatchBalance(
            nomenclature=nomenclature,
            date=date_val,
            balance=quantity,  # Используем количество как баланс
            warehouse=warehouse,
            batch=batch,
        )

        return movement, balance

    def _validate_column_types(
        self,
        df: pd.DataFrame,
        col_name: str,
        expected_types: List[type] | type,
        col_display_name: str,
    ) -> None:
        """
        Валидирует типы данных в указанной колонке DataFrame.

        Args:
            df: DataFrame для проверки
            col_name: Имя колонки для проверки
            expected_types: Ожидаемые типы данных (или список типов)
            col_display_name: Отображаемое имя колонки для логирования
        """
        if not col_name or col_name not in df.columns:
            return  # Если колонка не найдена, пропускаем проверку

        # Преобразуем expected_types в список, если передан один тип
        if not isinstance(expected_types, list):
            expected_types = [expected_types]

        # Проверяем каждый элемент в колонке
        invalid_values = []
        for idx, value in enumerate(df[col_name]):
            if pd.isna(value):
                continue  # Пропускаем NaN значения

            value_type = type(value)
            if not any(
                isinstance(value, expected_type) for expected_type in expected_types
            ):
                invalid_values.append((idx, value, value_type.__name__))

        if invalid_values:
            error_details = [
                f"строка {idx}: значение '{val}' типа '{val_type}'"
                for idx, val, val_type in invalid_values[:5]
            ]  # Ограничиваем первые 5

            error_msg = (
                f"Найдены некорректные типы данных в колонке '{col_display_name}' "
                f"(ожидались типы: {[t.__name__ for t in expected_types]}). "
                f"Примеры некорректных значений: {', '.join(error_details)}"
            )

            self.logger.error(error_msg)
            raise ValidationException(error_msg, error_code="INVALID_COLUMN_TYPES")

    def parse_file(self, file_path: str) -> pd.DataFrame:
        """
        Основной метод парсинга. Преобразует Excel-файл в плоский DataFrame.

        Args:
            file_path (str): Путь к Excel-файлу

        Returns:
            pd.DataFrame: Плоская таблица с данными из Excel-файла
        """
        self.logger.info(f"Начало парсинга файла: {file_path}")
        try:
            # Просто читаем Excel файл в DataFrame
            df = pd.read_excel(file_path, engine="openpyxl")
            self.logger.info(f"Парсинг завершён успешно, всего строк: {len(df)}")
            return df
        except Exception as e:
            self.logger.error(f"Ошибка при чтении Excel файла {file_path}: {e}")
            raise

    def parse_excel(
        self, file_path: str
    ) -> Tuple[List[BatchMovement], List[BatchBalance]]:
        """
        Преобразует Excel-файл в списки объектов BatchMovement и BatchBalance.

        Args:
            file_path (str): Путь к Excel-файлу

        Returns:
            tuple[list[BatchMovement], list[BatchBalance]]: Кортеж из двух списков:
                - список объектов BatchMovement
                - список объектов BatchBalance
        """
        self.logger.info(f"Начало парсинга Excel-файла: {file_path}")
        try:
            # Считываем данные из Excel файла
            df = pd.read_excel(file_path, engine="openpyxl")
            self.logger.info(f"Excel-файл успешно прочитан, строк: {len(df)}")

            # Проверяем, что DataFrame не пуст
            if df.empty:
                self.logger.warning(f"Excel файл {file_path} пустой")
                raise ParserException("Excel файл пустой", error_code="EMPTY_FILE")

            # Списки для хранения сущностей
            movements = []
            balances = []

            # Определяем колонки, которые нужно использовать
            # Используем стандартные имена колонок из тестов
            required_columns = {
                "Номенклатура": "nomenclature",
                "Партия": "batch",
                "Дата": "date",
                "ТипДвижения": "movement_type",
                "Количество": "quantity",
                "Склад": "warehouse",
            }

            # Проверяем, есть ли нужные колонки в DataFrame
            available_columns = df.columns.tolist()
            self.logger.debug(f"Доступные колонки в Excel-файле: {available_columns}")

            # Определяем сопоставление колонок (пытаемся использовать стандартные имена или русские)
            nomenclature_col = self._find_column(
                available_columns, ["Номенклатура", "nomenclature", "product"]
            )
            batch_col = self._find_column(
                available_columns, ["Партия", "batch", "party"]
            )
            date_col = self._find_column(available_columns, ["Дата", "date", "dt"])
            movement_type_col = self._find_column(
                available_columns, ["ТипДвижения", "movement_type", "type"]
            )
            quantity_col = self._find_column(
                available_columns, ["Количество", "quantity", "qty", "amount"]
            )
            warehouse_col = self._find_column(
                available_columns, ["Склад", "warehouse", "wh"]
            )

            # Проверяем наличие обязательных колонок
            missing_columns = []
            if not nomenclature_col:
                missing_columns.append("Номенклатура")
            if not date_col:
                missing_columns.append("Дата")
            if not movement_type_col:
                missing_columns.append("ТипДвижения")
            if not quantity_col:
                missing_columns.append("Количество")
            if not warehouse_col:
                missing_columns.append("Склад")

            if missing_columns:
                error_msg = (
                    f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}"
                )
                self.logger.error(error_msg)
                raise ValidationException(error_msg, error_code="MISSING_COLUMNS")

            # Валидация типов данных в обязательных колонках
            if nomenclature_col:
                self._validate_column_types(df, nomenclature_col, str, "Номенклатура")
            if date_col:
                self._validate_column_types(
                    df, date_col, [pd.Timestamp, date, str], "Дата"
                )
            if movement_type_col:
                self._validate_column_types(df, movement_type_col, str, "ТипДвижения")
            if quantity_col:
                self._validate_column_types(
                    df, quantity_col, [int, float], "Количество"
                )
            if warehouse_col:
                self._validate_column_types(df, warehouse_col, str, "Склад")

            # Если колонка партии не найдена, используем пустую строку
            if not batch_col:
                self.logger.warning(
                    "Колонка 'Партия' не найдена в Excel-файле, будет использоваться пустая строка для всех записей"
                )

            # Логирование начала обработки строк
            self.logger.info(f"Начало обработки {len(df)} строк данных из Excel-файла")

            for idx, row in df.iterrows():
                # Обработка строки и создание объектов
                movement, balance = self._process_row(
                    row,
                    idx,
                    nomenclature_col,
                    batch_col,
                    movement_type_col,
                    warehouse_col,
                    date_col,
                    quantity_col,
                )
                movements.append(movement)
                balances.append(balance)

            self.logger.info(
                f"Парсинг Excel-файла завершён успешно. Создано {len(movements)} объектов BatchMovement и {len(balances)} объектов BatchBalance"
            )
            return movements, balances

        except ValidationException as ve:
            self.logger.error(
                f"Ошибка валидации при парсинге Excel файла {file_path}: {ve.message}"
            )
            raise
        except ParserException as pe:
            self.logger.error(
                f"Ошибка парсинга при обработке Excel файла {file_path}: {pe.message}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Неизвестная ошибка при парсинге Excel файла {file_path}: {e}"
            )
            raise ParserException(
                f"Неизвестная ошибка при парсинге Excel файла: {str(e)}",
                error_code="PARSING_ERROR",
            )

    def save_to_json(self, data: pd.DataFrame, output_file: str) -> None:
        """
        Сохранение результата парсинга в JSON-файл.

        Args:
            data: Результат из parse_file() (pandas DataFrame)
            output_file (str): Путь к выходному файлу (e.g., 'inventory.json')
        """
        try:
            data.to_json(output_file, orient="records", force_ascii=False, indent=2)
            self.logger.info("JSON сохранён: %s", output_file)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения JSON: {e}")
