import pytest
from src.shield_ai.infrastructure.parsers.dto import RowType


# Импортируем тестируемую функцию. Она еще не реализована.
# Это вызовет ImportError, что подтвердит, что тест падает до реализации.
from src.shield_ai.infrastructure.parsers.hierarchical_excel_parser import recognize_row_type


class TestRecognizeRowType:
    """
    Тестовый класс для функции recognize_row_type.

    Проверяет, что функция корректно определяет тип строки в Excel-отчёте.
    Тесты должны падать до тех пор, пока функция recognize_row_type не будет реализована.
    """

    @pytest.mark.parametrize(
        "row_data, expected_type",
        [
            # Строка-заголовок: содержит слово "Склад" или "СКЛАД"
            (["Склад", "Группа", "Товар", "Код"], RowType.HEADER),
            (["СКЛАД", "Адрес", "Регион"], RowType.HEADER),
            # Строка-группа: содержит слово "Итого" или "Итого по"
            (["Итого", "100", "200", "300"], RowType.TOTAL),
            (["Итого по группе А", "50", "100"], RowType.TOTAL),
            # Строка данных: содержит числовые значения в определенных колонках (предполагаем колонки 2, 3, 4)
            (["Товар1", "Код1", 10, 20, 30], RowType.DATA),
            (["Товар2", "Код2", 0, 5.5, 10], RowType.DATA),
            # Пустая строка: все значения - None или пустые строки
            ([None, None, None], RowType.EMPTY),
            (["", "", ""], RowType.EMPTY),
            # Неопределённый тип: не подходит ни под один из вышеперечисленных
            (["Примечание", "Комментарий"], RowType.UNDEFINED),
            (["Случайная", "Строка", "Данных"], RowType.UNDEFINED),
        ],
    )
    def test_recognize_row_type(self, row_data, expected_type):
        """
        Проверяет, что recognize_row_type возвращает ожидаемый тип для различных строк.
        """
        result = recognize_row_type(row_data)
        assert result == expected_type
