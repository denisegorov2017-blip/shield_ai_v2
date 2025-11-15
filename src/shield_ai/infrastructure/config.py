import os
from typing import (
    Optional,
)

from dotenv import (
    load_dotenv,
)
from pydantic import (
    BaseModel,
    Field,
)
from pydantic_settings import (
    BaseSettings,
)

# Загружаем переменные окружения из .env файла
load_dotenv()


class DatabaseSettings(BaseModel):
    """Настройки базы данных"""

    url: str = Field(
        default="sqlite:///./ocean_shop.db",
        description="URL для подключения к базе данных",
    )
    echo: bool = Field(default=False, description="Включить логирование SQL-запросов")


class LoggingSettings(BaseModel):
    """Настройки логирования"""

    level: str = Field(
        default="INFO",
        description="Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    file: str = Field(default="logs/shield_ai.log", description="Путь к файлу логов")


class ApplicationSettings(BaseModel):
    """Настройки приложения"""

    name: str = Field(default="Shield AI", description="Название приложения")
    version: str = Field(default="2.0.0", description="Версия приложения")
    debug: bool = Field(default=False, description="Режим отладки")


class StreamlitSettings(BaseModel):
    """Настройки Streamlit"""

    server_port: int = Field(
        default=8501, description="Порт для запуска Streamlit сервера"
    )
    server_address: str = Field(
        default="localhost", description="Адрес для запуска Streamlit сервера"
    )


class ShrinkageSettings(BaseModel):
    """Настройки моделей усушки"""

    default_strategy: str = Field(
        default="weighted", description="Стратегия по умолчанию для расчета усушки"
    )
    calibration_strategy: str = Field(
        default="portion", description="Стратегия калибровки"
    )
    min_calibration_points: int = Field(
        default=3, description="Минимальное количество точек для калибровки"
    )


class Settings(BaseSettings):
    """Основные настройки приложения"""

    database: DatabaseSettings = DatabaseSettings()
    logging: LoggingSettings = LoggingSettings()
    application: ApplicationSettings = ApplicationSettings()
    streamlit: StreamlitSettings = StreamlitSettings()
    shrinkage: ShrinkageSettings = ShrinkageSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Обновляем настройки из переменных окружения
        self.database = DatabaseSettings(
            url=os.getenv("DATABASE_URL", self.database.url),
            echo=os.getenv("DATABASE_ECHO", str(self.database.echo)).lower() == "true",
        )

        self.logging = LoggingSettings(
            level=os.getenv("LOG_LEVEL", self.logging.level),
            file=os.getenv("LOG_FILE", self.logging.file),
        )

        self.application = ApplicationSettings(
            name=os.getenv("APP_NAME", self.application.name),
            version=os.getenv("APP_VERSION", self.application.version),
            debug=os.getenv("DEBUG", str(self.application.debug)).lower() == "true",
        )

        self.streamlit = StreamlitSettings(
            server_port=int(
                os.getenv("STREAMLIT_SERVER_PORT", self.streamlit.server_port)
            ),
            server_address=os.getenv(
                "STREAMLIT_SERVER_ADDRESS", self.streamlit.server_address
            ),
        )

        self.shrinkage = ShrinkageSettings(
            default_strategy=os.getenv(
                "DEFAULT_STRATEGY", self.shrinkage.default_strategy
            ),
            calibration_strategy=os.getenv(
                "CALIBRATION_STRATEGY", self.shrinkage.calibration_strategy
            ),
            min_calibration_points=int(
                os.getenv(
                    "MIN_CALIBRATION_POINTS", self.shrinkage.min_calibration_points
                )
            ),
        )


# Глобальный экземпляр настроек
settings = Settings()
