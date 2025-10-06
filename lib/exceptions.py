"""
Excepciones personalizadas para la biblioteca EVAL-ADMX2001.

Define una jerarquía de excepciones que permite un manejo de errores
preciso y específico para diferentes situaciones.
"""


class ADMX2001Error(Exception):
    """Excepción base para todos los errores relacionados con ADMX2001."""
    pass


class ConnectionError(ADMX2001Error):
    """Error de conexión con el dispositivo."""
    pass


class CalibrationError(ADMX2001Error):
    """Error durante el proceso de calibración."""
    pass


class MeasurementError(ADMX2001Error):
    """Error durante la medición."""
    pass


class ValidationError(ADMX2001Error):
    """Error de validación de parámetros."""
    pass


class TimeoutError(ADMX2001Error):
    """Error de timeout en comunicación."""
    pass


class CommandError(ADMX2001Error):
    """Error al ejecutar un comando."""
    pass


class SaturationError(MeasurementError):
    """Error de saturación del ADC."""
    pass


class SelfTestError(ADMX2001Error):
    """Error en el self-test del dispositivo."""
    pass
