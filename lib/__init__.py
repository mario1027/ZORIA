"""
EVAL-ADMX2001 Library
=====================

Biblioteca Python para el control completo del analizador de impedancia EVAL-ADMX2001.

Esta biblioteca proporciona una interfaz Python rigurosa y completa para controlar
el EVAL-ADMX2001 de Analog Devices, siguiendo estrictamente la documentación oficial.

Autor: Sistema de desarrollo
Licencia: MIT
"""

from .admx2001 import ADMX2001, CalibrationManager, MeasurementManager
from .utils import (
    list_available_ports,
    find_admx2001_devices,
    test_device_connection,
    validate_frequency,
    validate_magnitude,
    validate_offset,
    validate_average,
    validate_count,
    calculate_impedance_from_rx,
    recommend_gain_settings,
    estimate_measurement_time,
)
from .enums import (
    DisplayMode,
    SweepType,
    SweepScale,
    TriggerMode,
    GainChannel0,
    GainChannel1,
    ImpedanceRange,
)
from .exceptions import (
    ADMX2001Error,
    ConnectionError,
    CalibrationError,
    MeasurementError,
    ValidationError,
    TimeoutError,
    CommandError,
    SaturationError,
)

__version__ = '1.0.0'
__all__ = [
    # Clases principales
    'ADMX2001',
    'CalibrationManager',
    'MeasurementManager',
    # Utilidades de puerto
    'list_available_ports',
    'find_admx2001_devices',
    'test_device_connection',
    # Validaciones
    'validate_frequency',
    'validate_magnitude',
    'validate_offset',
    'validate_average',
    'validate_count',
    # Cálculos
    'calculate_impedance_from_rx',
    'recommend_gain_settings',
    'estimate_measurement_time',
    # Enumeraciones
    'DisplayMode',
    'SweepType',
    'SweepScale',
    'TriggerMode',
    'GainChannel0',
    'GainChannel1',
    'ImpedanceRange',
    # Excepciones
    'ADMX2001Error',
    'ConnectionError',
    'CalibrationError',
    'MeasurementError',
    'ValidationError',
    'TimeoutError',
    'CommandError',
    'SaturationError',
]
