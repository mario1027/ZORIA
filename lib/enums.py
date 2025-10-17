"""
Enumeraciones y constantes para EVAL-ADMX2001.

Define todos los modos, escalas y parámetros válidos
según la documentación oficial del dispositivo.
"""

from enum import Enum, IntEnum


class DisplayMode(IntEnum):
    """
    Modos de visualización disponibles en ADMX2001.
    
    Cada modo representa una forma diferente de expresar la impedancia:
    - Series: componentes en serie
    - Parallel: componentes en paralelo
    - Rectangular: coordenadas rectangulares (R, X) o (G, B)
    - Polar: magnitud y fase
    """
    # Series Capacitance
    CS_RS = 0   # Equivalent series capacitance and resistance (Farads, Ohms)
    CS_D = 1    # Equivalent series capacitance and dissipation factor (Farads, Dimensionless)
    CS_Q = 2    # Equivalent series capacitance and quality factor (Farads, Dimensionless)
    
    # Series Inductance
    LS_RS = 3   # Inductance and equivalent series resistance (Henries, Ohms)
    LS_D = 4    # Equivalent series inductance and dissipation factor (Henries, Dimensionless)
    LS_Q = 5    # Equivalent series inductance and quality factor (Henries, Dimensionless)
    
    # Impedance
    R_X = 6     # Impedance in rectangular coordinates (Ohms, Ohms) - DEFAULT
    Z_DEG = 7   # Impedance in magnitude and phase in degrees (Ohms, Degrees)
    Z_RAD = 8   # Impedance in magnitude and phase in radians (Ohms, Radians)
    
    # Parallel Capacitance
    CP_RP = 9   # Capacitance and equivalent parallel resistance (Farads, Ohms)
    CP_D = 10   # Equivalent parallel capacitance and dissipation factor (Farads, Dimensionless)
    CP_Q = 11   # Equivalent parallel capacitance and quality factor (Farads, Dimensionless)
    
    # Parallel Inductance
    LP_RP = 12  # Inductance and equivalent parallel resistance (Henries, Ohms)
    LP_D = 13   # Equivalent parallel inductance and dissipation factor (Henries, Dimensionless)
    LP_Q = 14   # Equivalent parallel inductance and quality factor (Henries, Dimensionless)
    
    # Admittance
    G_B = 15    # Admittance in rectangular coordinates (Siemens, Siemens)
    Y_DEG = 16  # Admittance in magnitude and phase in degrees (Siemens, Degrees)
    Y_RAD = 17  # Admittance in magnitude and phase in radians (Siemens, Radians)
    
    OFF = 18    # Off


class SweepType(Enum):
    """Tipos de barrido (sweep) disponibles."""
    FREQUENCY = "frequency"
    DC_BIAS = "offset"
    MAGNITUDE = "magnitude"
    OFF = "off"


class SweepScale(Enum):
    """Escala del barrido."""
    LINEAR = "linear"
    LOG = "log"


class TriggerMode(Enum):
    """Modo de trigger."""
    INTERNAL = "internal"
    EXTERNAL = "external"


class GainChannel0(IntEnum):
    """
    Configuración de ganancia para el canal 0 (voltaje).
    
    Según la documentación:
    - Gain 0: ±2.5V max, factor 1
    - Gain 1: ±1.25V max, factor 2
    - Gain 2: ±625mV max, factor 4
    - Gain 3: ±312.5mV max, factor 8
    """
    GAIN_0 = 0  # ±2.5V range
    GAIN_1 = 1  # ±1.25V range
    GAIN_2 = 2  # ±625mV range
    GAIN_3 = 3  # ±312.5mV range


class GainChannel1(IntEnum):
    """
    Configuración de ganancia para el canal 1 (corriente).
    
    Según la documentación:
    - Gain 0: 25mA max, 49.9Ω transimpedance
    - Gain 1: 2.5mA max, 499Ω transimpedance
    - Gain 2: 250uA max, 4.99kΩ transimpedance
    - Gain 3: 25uA max, 49.9kΩ transimpedance
    """
    GAIN_0 = 0  # 25mA max
    GAIN_1 = 1  # 2.5mA max
    GAIN_2 = 2  # 250uA max
    GAIN_3 = 3  # 25uA max


class ImpedanceRange(Enum):
    """
    Rangos de impedancia recomendados según la documentación.
    
    Cada rango especifica la configuración óptima de ganancia
    para el canal 0 y canal 1.
    """
    UNDER_10_OHM = (3, 0)      # < 10Ω
    UNDER_25_OHM = (2, 0)      # < 25Ω
    UNDER_50_OHM = (1, 0)      # < 50Ω
    RANGE_100_1K = (0, 0)      # 100Ω to 1kΩ
    RANGE_1K_10K = (0, 1)      # 1kΩ to 10kΩ
    RANGE_10K_100K = (0, 2)    # 10kΩ to 100kΩ
    OVER_100K = (0, 3)         # > 100kΩ


# Constantes físicas del dispositivo
SOURCE_RESISTANCE = 100.0  # Ohms
INPUT_PROTECTION_RESISTANCE = 10.0  # Ohms
TOTAL_SERIES_RESISTANCE = SOURCE_RESISTANCE + INPUT_PROTECTION_RESISTANCE  # 110 Ohms

# Límites de parámetros según documentación
FREQUENCY_MIN = 0.2  # Hz (0 para modo DC)
FREQUENCY_MAX = 10_000_000  # Hz (10 MHz)
MAGNITUDE_MIN = 0.15  # Vpk
MAGNITUDE_MAX = 2.25  # Vpk
OFFSET_MIN = -2.0  # V
OFFSET_MAX = 2.0  # V
AVERAGE_MIN = 1
AVERAGE_MAX = 256  # Documentación sugiere no exceder 256
COUNT_MIN = 1
COUNT_MAX = 1000  # Límite realista basado en pruebas empíricas
                  # IMPORTANTE: El máximo depende del ANCHO DE BANDA (décadas):
                  #   • < 0.5 déc (muy estrecho):  hasta 1000 puntos
                  #   • 0.5-1.0 déc (estrecho):    hasta 500 puntos  
                  #   • 1.0-2.0 déc (mediano):     hasta 300 puntos
                  #   • 2.0-3.0 déc (grande):      hasta 255 puntos
                  #   • 3.0-4.0 déc (muy grande):  hasta 200 puntos
                  #   • > 4.0 déc (completo):      hasta 100 puntos
                  # Regla: A MENOR ancho de banda → MÁS puntos posibles
TRIGGER_COUNT_INFINITE = 65536  # Valor especial para trigger infinito

# Delays recomendados (millisegundos)
DEFAULT_MDELAY = 1.0  # Measurement delay
DEFAULT_TDELAY = 4.0  # Trigger delay
RECOMMENDED_MIN_TDELAY = 0.0  # Para optimización de velocidad
RECOMMENDED_MIN_MDELAY = 0.0  # Solo a frecuencias > 10kHz

# Baudrate y timeout
DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT = 5.0  # Aumentado para dispositivos lentos
COMMAND_TIMEOUT = 10.0
SWEEP_TIMEOUT = 600.0  # 10 minutos - para sweeps muy largos (era 60s)

# Temperatura
TEMPERATURE_WARNING_THRESHOLD = 60.0  # °C
