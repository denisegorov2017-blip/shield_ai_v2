"""
Модуль, определяющий базовую иерархию исключений для проекта Shield AI.

Эти исключения обеспечивают стандартизированный подход к обработке ошибок
в соответствии с принципами Clean Architecture.
"""


class ShieldAIException(Exception):
    """
    Базовый класс для всех исключений, специфичных для Shield AI.

    Все исключения приложения должны наследоваться от этого класса.
    """

    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class DomainException(ShieldAIException):
    """
    Исключения, связанные с бизнес-логикой доменного слоя.
    """

    pass


class ApplicationException(ShieldAIException):
    """
    Исключения, связанные с прикладной логикой слоя приложения.
    """

    pass


class InfrastructureException(ShieldAIException):
    """
    Исключения, связанные с инфраструктурой (базы данных, файлы и т.д.).
    """

    pass


class ValidationException(DomainException):
    """
    Исключения, возникающие при валидации данных.
    """

    pass


class CalculationException(DomainException):
    """
    Исключения, возникающие при выполнении вычислений.
    """

    pass


class RepositoryException(InfrastructureException):
    """
    Исключения, связанные с работой репозиториев.
    """

    pass


class ParserException(InfrastructureException):
    """
    Исключения, связанные с парсингом данных.
    """

    pass


class ConfigurationException(InfrastructureException):
    """
    Исключения, связанные с конфигурацией приложения.
    """

    pass
