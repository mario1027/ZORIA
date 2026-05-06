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
    max_count_for_span,
    calculate_impedance_from_rx,
    recommend_gain_settings,
    estimate_measurement_time,
    estimate_sweep_time,
    max_points_per_segment,
    _acquisition_time_ms,
)
from .hw_timing_profile import HardwareTimingProfile, get_profile as get_hw_timing_profile
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

# Exportar ajuste RC
from .rc_model import (
    fit_parallel_rc,
    fit_parallel_rc_from_csv,
    parallel_rc_z,
    fit_series_rc,
    fit_series_rc_from_csv,
    series_rc_z,
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
    'max_count_for_span',
    # Cálculos
    'calculate_impedance_from_rx',
    'recommend_gain_settings',
    'estimate_measurement_time',
    'estimate_sweep_time',
    'max_points_per_segment',
    # Ajuste de modelo RC
    'fit_parallel_rc',
    'fit_parallel_rc_from_csv',
    'parallel_rc_z',
    'fit_series_rc',
    'fit_series_rc_from_csv',
    'series_rc_z',
    'estimate_series_equivalent',
    'estimate_series_from_plateau',
    'evaluate_bode',
    'evaluate_nyquist',
    'series_rc_with_leak_z',
    'fit_series_rc_with_leak',
    'fit_series_rc_from_csv',
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
