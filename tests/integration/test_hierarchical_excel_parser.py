import pytest
from pathlib import Path
from src.shield_ai.infrastructure.parsers.hierarchical_excel_parser import HierarchicalExcelParser
from src.shield_ai.infrastructure.parsers.dto import FlatRecord


class TestHierarchicalExcelParserIntegration:
    """
    Интеграционный тест для полного цикла парсинга иерархического Excel-файла.
    
    Проверяет полный цикл работы парсера на эталонном файле.
    Тест должен падать до тех пор, пока парсер не будет полностью реализован.
    """
    
    def test_full_parsing_cycle_with_reference_file(self):
        """
        Тестирует полный цикл парсинга одного из эталонных файлов.
        
        Проверяет:
        - Инициализацию HierarchicalExcelParser
        - Вызов метода parse с эталонным файлом
        - Что результат является списком FlatRecord
        - Что количество записей больше нуля
        - Базовые проверки первой и последней записи
        """
        # Путь к эталонному файлу
        reference_file_path = Path("data/input/13.10.25-13.10.25 Полный все склады с коррекцией.xlsx")
        
        # Проверяем, что файл существует
        assert reference_file_path.exists(), f"Эталонный файл не найден: {reference_file_path}"
        
        # Инициализируем парсер
        parser = HierarchicalExcelParser()
        
        # Вызываем метод парсинга (ожидаем, что он будет реализован позже)
        result_tuple = parser.parse(reference_file_path)
        
        # Проверяем, что результат является кортежем
        assert isinstance(result_tuple, tuple), f"Результат должен быть кортежем, получен: {type(result_tuple)}"
        assert len(result_tuple) == 2, f"Результат должен содержать 2 элемента, получен: {len(result_tuple)}"
        
        # Извлекаем списки из кортежа
        flat_records, other_data = result_tuple
        
        # Проверяем, что первый элемент кортежа - это список FlatRecord
        assert isinstance(flat_records, list), f"Первый элемент должен быть списком, получен: {type(flat_records)}"
        
        # Проверяем, что flat_records содержит FlatRecord объекты
        assert all(isinstance(record, FlatRecord) for record in flat_records), \
            "Все элементы flat_records должны быть объектами FlatRecord"
        
        # Проверяем, что количество записей больше нуля
        assert len(flat_records) > 0, "Результат должен содержать хотя бы одну запись"
        
        # Проверяем первую запись
        first_record = flat_records[0]
        assert first_record.warehouse is not None and first_record.warehouse != "", \
            "Поле warehouse первой записи не должно быть пустым"
        assert first_record.product is not None and first_record.product != "", \
            "Поле product первой записи не должно быть пустым"
        
        # Проверяем последнюю запись
        last_record = flat_records[-1]
        assert last_record.warehouse is not None and last_record.warehouse != "", \
            "Поле warehouse последней записи не должно быть пустым"
        assert last_record.product is not None and last_record.product != "", \
            "Поле product последней записи не должно быть пустым"


if __name__ == "__main__":
    pytest.main([__file__])