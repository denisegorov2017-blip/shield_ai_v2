import sys
from pathlib import (
    Path,
)

# Добавляем директорию src в путь Python для корректных импортов
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Импорты после изменения sys.path
from shield_ai.application.use_cases.calibrate_coefficients import (
    CalibrateCoefficientsUseCase,
)
from shield_ai.infrastructure.config import (
    settings,
)
from shield_ai.infrastructure.database.session import (
    get_session,
)
from shield_ai.infrastructure.repositories.calibration_repository import (
    SQLAlchemyCalibrationDataRepository,
)
from shield_ai.infrastructure.repositories.coefficient_repository import (
    SQLAlchemyCoefficientRepository,
)
from shield_ai.infrastructure.repositories.product_repository import (
    SQLAlchemyProductRepository,
)


def create_use_case_with_dependencies(session):
    """
    Создает экземпляр CalibrateCoefficientsUseCase с внедренными зависимостями.

    Args:
        session: SQLAlchemy сессия для работы с базой данных

    Returns:
        Экземпляр CalibrateCoefficientsUseCase с внедренными репозиториями
    """
    # В текущей реализации CalibrateCoefficientsUseCase не принимает репозитории в конструкторе
    # Вместо этого он использует стратегию расчета усушки
    return CalibrateCoefficientsUseCase()


def main():
    # Выводим информацию о текущих настройках
    print(f"Application: {settings.application.name} v{settings.application.version}")
    print(f"Database URL: {settings.database.url}")
    print(f"Debug mode: {settings.application.debug}")
    print(f"Log level: {settings.logging.level}")

    with get_session() as session:
        use_case = create_use_case_with_dependencies(session)
        results = use_case.execute_all()
        print(results)


if __name__ == "__main__":
    main()
