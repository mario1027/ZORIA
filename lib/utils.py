"""
Utilidades para EVAL-ADMX2001.

Funciones auxiliares para detección de puertos, validación,
conversiones y helpers generales.
"""

import serial
import serial.tools.list_ports
import re
import math
import logging
import os
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


def _port_identity_blob(port_obj: Any) -> str:
    """Construye un texto normalizado con los metadatos del puerto."""
    device = getattr(port_obj, 'device', '') or ''
    description = getattr(port_obj, 'description', '') or ''
    manufacturer = getattr(port_obj, 'manufacturer', '') or ''
    product = getattr(port_obj, 'product', '') or ''
    hwid = getattr(port_obj, 'hwid', '') or ''
    interface = getattr(port_obj, 'interface', '') or ''
    return f"{device} {description} {manufacturer} {product} {hwid} {interface}".upper()


def is_usb_serial_port(port_obj: Any) -> bool:
    """Retorna True si el puerto corresponde a un adaptador serial USB."""
    device = (getattr(port_obj, 'device', '') or '').upper()
    return (
        'TTYUSB' in device or
        'TTYACM' in device or
        device.startswith('COM') or
        '/DEV/CU.USBSERIAL' in device or
        '/DEV/CU.USBMODEM' in device
    )


def get_admx_port_priority(port_obj: Any) -> int:
    """Asigna prioridad a puertos USB según qué tan probable es que sean el cable TTL usado."""
    if not is_usb_serial_port(port_obj):
        return -1

    blob = _port_identity_blob(port_obj)

    if 'TTL232R-3V3' in blob:
        return 120
    if 'TTL-232R-RPI' in blob:
        return 115
    if 'TTL232R' in blob or 'TTL-232R' in blob:
        return 110
    if 'FT232R' in blob or 'FT232' in blob:
        return 95
    if 'FTDI' in blob and ('USB' in blob or 'SERIAL' in blob):
        return 90
    if 'USB SERIAL CONVERTER' in blob:
        return 80
    if 'CP210' in blob or 'SILICON LABS' in blob:
        return 40
    if 'CH340' in blob or 'PL2303' in blob:
        return 30
    return 10


def is_likely_admx_port(port_obj: Any) -> bool:
    """Determina si el puerto coincide con el perfil esperado del adaptador TTL del ADMX2001."""
    return get_admx_port_priority(port_obj) >= 80


def get_preferred_usb_serial_ports(ports: Optional[List[Any]] = None) -> List[Any]:
    """Devuelve puertos USB ordenados por prioridad, con el TTL esperado primero."""
    port_list = list(ports) if ports is not None else list(serial.tools.list_ports.comports())
    usb_ports = [port for port in port_list if is_usb_serial_port(port)]
    return sorted(
        usb_ports,
        key=lambda port: (-get_admx_port_priority(port), (getattr(port, 'device', '') or '').upper())
    )


def list_available_ports() -> List[Dict[str, str]]:
    """
    Lista solo los puertos USB disponibles en el sistema.
    
    Filtra automáticamente puertos ttyS* (puertos seriales integrados)
    que pueden causar errores de I/O.
    
    Returns:
        Lista de diccionarios con información de puertos USB:
        - device: ruta del dispositivo (/dev/ttyUSB0, COM3, etc.)
        - description: descripción del puerto
        - hwid: hardware ID
        - manufacturer: fabricante
    
    Example:
        >>> ports = list_available_ports()
        >>> for port in ports:
        ...     print(f"{port['device']}: {port['description']}")
    """
    ports = []
    for port in get_preferred_usb_serial_ports():
        ports.append({
            'device': port.device,
            'description': port.description,
            'hwid': port.hwid,
            'manufacturer': port.manufacturer or 'Unknown'
        })
    return ports


def find_admx2001_devices() -> List[str]:
    """
    Busca dispositivos ADMX2001 conectados en puertos USB.
    
    Intenta identificar puertos que probablemente sean ADMX2001
    basándose en descriptores conocidos (FTDI, USB Serial).
    Solo busca en puertos USB para evitar errores I/O en ttyS*.
    
    Returns:
        Lista de rutas de dispositivos potenciales.
    
    Note:
        Esta función usa heurísticas; no garantiza que el dispositivo
        sea realmente un ADMX2001. Use test_device_connection() para verificar.
    """
    return [
        port.device
        for port in get_preferred_usb_serial_ports()
        if is_likely_admx_port(port)
    ]


def test_device_connection(port: str, baudrate: int = 115200, timeout: float = 2.0) -> bool:
    """
    Prueba si hay un dispositivo ADMX2001 en el puerto especificado.
    
    Args:
        port: Ruta del puerto serie
        baudrate: Velocidad de comunicación
        timeout: Timeout en segundos
    
    Returns:
        True si se detecta un ADMX2001, False en caso contrario.
    
    Example:
        >>> if test_device_connection('/dev/ttyUSB0'):
        ...     print("ADMX2001 detectado")
    """
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        ser.write(b'\n')  # Limpiar buffer
        ser.readline()
        ser.write(b'*idn\n')
        response = ser.readline().decode('utf-8', errors='ignore')
        ser.close()
        
        # Verificar si la respuesta contiene indicadores de ADMX2001
        return 'ADMX' in response.upper() or 'ANALOG' in response.upper()
    except Exception as e:
        logger.debug(f"Error probando puerto {port}: {e}")
        return False


def validate_frequency(freq: float) -> None:
    """
    Valida que la frecuencia esté en el rango permitido.
    
    Args:
        freq: Frecuencia en Hz (0 para modo DC, 0.2-10MHz para AC)
    
    Raises:
        ValidationError: Si la frecuencia está fuera de rango.
    """
    from .enums import FREQUENCY_MIN, FREQUENCY_MAX
    
    if freq < 0:
        raise ValidationError(f"Frecuencia no puede ser negativa: {freq}")
    if freq != 0 and (freq < FREQUENCY_MIN or freq > FREQUENCY_MAX):
        raise ValidationError(
            f"Frecuencia debe estar entre {FREQUENCY_MIN} Hz y {FREQUENCY_MAX} Hz "
            f"(o 0 para modo DC). Valor recibido: {freq}"
        )


def validate_magnitude(mag: float) -> None:
    """
    Valida que la magnitud (amplitud) esté en el rango permitido.
    
    Args:
        mag: Magnitud en Vpk
    
    Raises:
        ValidationError: Si la magnitud está fuera de rango.
    """
    from .enums import MAGNITUDE_MIN, MAGNITUDE_MAX
    
    if mag < MAGNITUDE_MIN or mag > MAGNITUDE_MAX:
        raise ValidationError(
            f"Magnitud debe estar entre {MAGNITUDE_MIN} Vpk y {MAGNITUDE_MAX} Vpk. "
            f"Valor recibido: {mag}"
        )


def validate_offset(offset: float) -> None:
    """
    Valida que el offset DC esté en el rango permitido.
    
    Args:
        offset: Offset en V
    
    Raises:
        ValidationError: Si el offset está fuera de rango.
    """
    from .enums import OFFSET_MIN, OFFSET_MAX
    
    if offset < OFFSET_MIN or offset > OFFSET_MAX:
        raise ValidationError(
            f"Offset debe estar entre {OFFSET_MIN} V y {OFFSET_MAX} V. "
            f"Valor recibido: {offset}"
        )


def validate_average(avg: int) -> None:
    """
    Valida el número de promedios.
    
    Args:
        avg: Número de promedios (1-256)
    
    Raises:
        ValidationError: Si está fuera de rango.
    """
    from .enums import AVERAGE_MIN, AVERAGE_MAX
    
    if not isinstance(avg, int) or avg < AVERAGE_MIN or avg > AVERAGE_MAX:
        raise ValidationError(
            f"Average debe ser un entero entre {AVERAGE_MIN} y {AVERAGE_MAX}. "
            f"Valor recibido: {avg}"
        )


def validate_count(count: int) -> None:
    """
    Valida el número de muestras.
    
    Args:
        count: Número de muestras (1-1000)
    
    Raises:
        ValidationError: Si está fuera de rango.
    """
    from .enums import COUNT_MIN, COUNT_MAX
    
    if not isinstance(count, int) or count < COUNT_MIN or count > COUNT_MAX:
        raise ValidationError(
            f"Count debe ser un entero entre {COUNT_MIN} y {COUNT_MAX}. "
            f"Valor recibido: {count}"
        )


def max_count_for_span(start_hz: float, end_hz: float) -> int:
    """
    Calcula el número máximo de puntos que acepta el firmware del ADMX2001
    para un barrido de frecuencias dado.

    Basado en mediciones empíricas del hardware real:
      - Spans >= 4 décadas: máximo 100 pts  (CONFIRMADO: 6 dec → 100 )
      - Spans < 4 décadas:  máximo 200 pts  (CONFIRMADO: 3 dec → 200 )

    IMPORTANTE: Superar este límite corrompe el estado del firmware, haciendo
    que barridos siguientes retornen sólo COUNT_MIN=10 puntos en lugar del
    valor configurado.

    Args:
        start_hz: Frecuencia inicial en Hz.
        end_hz:   Frecuencia final en Hz.

    Returns:
        Número máximo de puntos seguros para este span.
    """
    import math
    if start_hz <= 0 or end_hz <= 0 or end_hz <= start_hz:
        return 10
    decades = math.log10(end_hz / start_hz)
    if decades >= 4.0:
        return 100   # ≥ 4 décadas → máx 100 pts (medido empíricamente)
    else:
        return 200   # < 4 décadas → máx 200 pts (medido empíricamente)


def calculate_impedance_from_rx(r: float, x: float) -> Dict[str, float]:
    """
    Calcula parámetros de impedancia desde componentes rectangulares.
    
    Args:
        r: Resistencia (Ohms)
        x: Reactancia (Ohms)
    
    Returns:
        Diccionario con:
        - magnitude: |Z| = sqrt(R² + X²)
        - phase_rad: fase en radianes
        - phase_deg: fase en grados
        - conductance: G (Siemens)
        - susceptance: B (Siemens)
    """
    magnitude = math.sqrt(r**2 + x**2)
    phase_rad = math.atan2(x, r)
    phase_deg = math.degrees(phase_rad)
    
    # Admitancia: Y = 1/Z = G + jB
    if magnitude > 0:
        y_magnitude = 1.0 / magnitude
        conductance = y_magnitude * math.cos(phase_rad)
        susceptance = y_magnitude * math.sin(phase_rad)
    else:
        conductance = float('inf')
        susceptance = 0.0
    
    return {
        'magnitude': magnitude,
        'phase_rad': phase_rad,
        'phase_deg': phase_deg,
        'conductance': conductance,
        'susceptance': susceptance
    }


def calculate_dut_voltage(magnitude: float, impedance: float) -> float:
    """
    Calcula el voltaje real a través del DUT considerando resistencias serie.
    
    Según documentación:
    V_DUT = magnitude * |Z_DUT| / (|Z_DUT| + 110Ω)
    
    Args:
        magnitude: Magnitud configurada (Vpk)
        impedance: Impedancia del DUT (Ohms)
    
    Returns:
        Voltaje efectivo en el DUT (Vpk)
    """
    from .enums import TOTAL_SERIES_RESISTANCE
    
    return magnitude * impedance / (impedance + TOTAL_SERIES_RESISTANCE)


def calculate_dut_current(magnitude: float, impedance: float) -> float:
    """
    Calcula la corriente real a través del DUT considerando resistencias serie.
    
    Según documentación:
    I_DUT = magnitude / (|Z_DUT| + 110Ω)
    
    Args:
        magnitude: Magnitud configurada (Vpk)
        impedance: Impedancia del DUT (Ohms)
    
    Returns:
        Corriente efectiva en el DUT (Apk)
    """
    from .enums import TOTAL_SERIES_RESISTANCE
    
    return magnitude / (impedance + TOTAL_SERIES_RESISTANCE)


def recommend_gain_settings(impedance: float, magnitude: float = 1.0, offset: float = 0.0) -> Tuple[int, int]:
    """
    Recomienda configuración de ganancia basada en impedancia estimada.
    
    Sigue las tablas de la documentación oficial.
    
    Args:
        impedance: Impedancia estimada del DUT (Ohms)
        magnitude: Magnitud de señal (Vpk)
        offset: Offset DC (V)
    
    Returns:
        Tupla (ch0_gain, ch1_gain)
    
    Example:
        >>> ch0, ch1 = recommend_gain_settings(2000)  # 2kΩ
        >>> print(f"Usar gain ch0={ch0}, ch1={ch1}")
    """
    from .enums import ImpedanceRange, TOTAL_SERIES_RESISTANCE
    
    # Calcular corriente y voltaje esperados
    total_v = magnitude + abs(offset)
    expected_current = total_v / (impedance + TOTAL_SERIES_RESISTANCE)
    expected_voltage = calculate_dut_voltage(total_v, impedance)
    
    # Determinar ganancia ch1 (corriente) basado en corriente esperada
    if expected_current > 0.0025:  # > 2.5mA
        ch1_gain = 0
    elif expected_current > 0.00025:  # > 250uA
        ch1_gain = 1
    elif expected_current > 0.000025:  # > 25uA
        ch1_gain = 2
    else:
        ch1_gain = 3
    
    # Determinar ganancia ch0 (voltaje) basado en voltaje esperado
    if expected_voltage > 1.25:  # > 1.25V
        ch0_gain = 0
    elif expected_voltage > 0.625:  # > 625mV
        ch0_gain = 1
    elif expected_voltage > 0.3125:  # > 312.5mV
        ch0_gain = 2
    else:
        ch0_gain = 3
    
    return (ch0_gain, ch1_gain)


def clean_response_line(line: str, preserve_indent: bool = False) -> str:
    """
    Limpia una línea de respuesta del dispositivo (MEJORADO estilo TeraTerm).
    
    Remueve:
    - Códigos ANSI de escape (secuencias de escape estándar)
    - Códigos de control de cursor VT100 (ESC 7, ESC 8, etc.)
    - Prompts (ADMX2001>)
    - Line endings (CR+LF, CR, LF normalizados)
    - Caracteres de control NULL
    - Espacios (configurable)
    
    Args:
        line: Línea cruda del dispositivo
        preserve_indent: Si True, preserva espacios de indentación (solo limpia trailing)
    
    Returns:
        Línea limpia
    """
    # 1. Remover códigos ANSI estándar (secuencias de escape complejas)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    line = ansi_escape.sub('', line)
    
    # 2. Remover códigos de control de cursor VT100 simples (ESC + dígito/letra)
    vt100_control = re.compile(r'\x1B[0-9A-Za-z]')
    line = vt100_control.sub('', line)
    
    # 3. Remover cualquier ESC solitario que pueda quedar
    line = line.replace('\x1B', '')
    
    # 4. Normalizar line endings (CR+LF -> espacio, CR -> espacio, mantener estructura)
    line = line.replace('\r\n', ' ').replace('\r', ' ')
    
    # 5. Remover NULL bytes y caracteres de control (excepto espacios y tabs)
    line = ''.join(ch for ch in line if ch >= ' ' or ch == '\t')
    
    # 6. Remover prompt
    line = line.replace('ADMX2001>', '')
    
    # 7. Limpiar espacios según configuración
    if preserve_indent:
        # Solo remover espacios finales (trailing whitespace)
        line = line.rstrip()
    else:
        # Strip completo (comportamiento original)
        line = line.strip()
    
    return line


def parse_numeric_response(line: str) -> Optional[float]:
    """
    Intenta extraer un valor numérico de una línea de respuesta.
    
    Args:
        line: Línea de respuesta
    
    Returns:
        Valor numérico si se encuentra, None en caso contrario.
    """
    line = clean_response_line(line)
    
    # Buscar patrones como "123.45", "1.23e-4", etc.
    match = re.search(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', line)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            pass
    return None


def parse_measurement_line(line: str) -> Optional[List[float]]:
    """
    Parsea una línea de medición que contiene valores separados por comas.
    
    Formato típico: "0,1.234567e+01,-5.678901e+00"
    
    Args:
        line: Línea de medición
    
    Returns:
        Lista de valores numéricos, o None si no se puede parsear.
    """
    line = clean_response_line(line)
    
    if ',' not in line:
        return None
    
    try:
        parts = line.split(',')
        values = [float(part.strip()) for part in parts]
        return values
    except ValueError:
        return None


def format_scientific(value: float, precision: int = 6) -> str:
    """
    Formatea un número en notación científica.
    
    Args:
        value: Valor a formatear
        precision: Dígitos de precisión
    
    Returns:
        String formateado
    """
    return f"{value:.{precision}e}"


# ---------------------------------------------------------------------------
# Constantes derivadas de la documentación oficial del EVAL-ADMX2001
# Firmware v1.3.x – medición vía UART a 115200 baud:
#
#   "Mediciones típicas: 10-12 ms" (trigger mode, autorange OFF, f > 3 kHz)
#   "Mediciones más rápidas sobre ~3 kHz"
#
# Deducción del número de ciclos de integración DFT del hardware:
#   piso_nominal = 15 ms  (modo UART normal, no trigger)
#   cruce a f=3000 Hz  →  N = 3000 Hz × 0.015 s = 45 ciclos
#   En la práctica el firmware oscila entre 30 y 36 ciclos en trigger;
#   para UART normal (overhead de 5-8 ms) usamos 36 ciclos + piso 15 ms.
#
# Esto corrige el modelo anterior de 3 ciclos, que subestimaba 10-15×
# los tiempos reales a bajas frecuencias.  La función también acepta
# datos del perfil de hardware medido (lib/hw_timing_profile.py).
# ---------------------------------------------------------------------------
_HW_DFT_CYCLES   = 36      # ciclos mínimos de integración DFT del chip
_HW_FLOOR_MS     = 15.0    # piso real en modo UART (measurement + comm)
_HW_DC_FLOOR_MS  = 80.0    # estimación para modo DC (settle + measure)
# Overhead fijo medido por cada llamada a perform_sweep():
#   setup hardware + primer punto + latencia del dispositivo
#   ~5800 ms medido en benchmark real (2024) a frecuencias > 100 Hz
_HW_SWEEP_STARTUP_MS = 5800.0


def _acquisition_time_ms(frequency: float, average: int = 1) -> float:
    """
    Calcula el tiempo de adquisición en ms para UNA medición a la frecuencia dada.

    Modelo derivado de la documentación oficial EVAL-ADMX2001 v1.3.x:
    - El motor DFT interno del chip necesita ~36 ciclos completos de la señal
      de excitación para alcanzar la precisión especificada.
    - Por encima de ~3 kHz, el piso de hardware (15 ms en modo UART) domina.
    - El promediado multiplica linealmente el tiempo de adquisición.

    Verificación:
      f=0.2 Hz  → 36/0.2×1000 = 180 000 ms ≈ 3 min por punto   (correcto)
      f=3 kHz   → max(12, 15) = 15 ms                            (docs: 10-12 ms)
      f=10 MHz  → piso 15 ms                                    

    Args:
        frequency: Frecuencia en Hz (>0 para AC, 0 para DC)
        average:   Número de promedios (multiplica el tiempo linealmente)

    Returns:
        Tiempo de adquisición en ms (sin incluir mdelay/tdelay externos)
    """
    if frequency <= 0:
        base_ms = _HW_DC_FLOOR_MS
    else:
        # Tiempo basado en ciclos de integración del hardware
        period_ms = (1.0 / frequency) * 1000.0
        base_ms = _HW_DFT_CYCLES * period_ms

    # Piso de hardware (comunicación + procesamiento mínimo)
    base_ms = max(base_ms, _HW_FLOOR_MS)

    # El promediado multiplica el tiempo de adquisición linealmente
    return base_ms * max(1, average)


def estimate_measurement_time(frequency: float, average: int, count: int,
                              mdelay: float = 1.0, tdelay: float = 4.0) -> float:
    """
    Estima el tiempo de medición basado en parámetros para UNA frecuencia fija.

    Args:
        frequency: Frecuencia en Hz
        average: Número de promedios
        count: Número de muestras repetidas a esa frecuencia
        mdelay: Delay de medición (ms)
        tdelay: Delay de trigger (ms)

    Returns:
        Tiempo estimado en segundos
    """
    sample_time = _acquisition_time_ms(frequency, average)

    # Suma de tiempos individuales + delays + overhead de comunicación
    total_ms = sample_time * count + mdelay * count + tdelay + 50.0
    return total_ms / 1000.0


def estimate_sweep_time(freq_start: float, freq_end: float, n_points: int,
                        scale: str = 'log', average: int = 1,
                        mdelay: float = 0.0, tdelay: float = 0.0) -> dict:
    """
    Estima el tiempo total de un barrido de frecuencias de freq_start a freq_end.

    Calcula punto a punto el tiempo de adquisición, ya que a frecuencias muy bajas
    (p. ej. 0.2 Hz) cada medición requiere ~15 s, mientras que a 10 MHz el piso
    de 10 ms domina.  La suma correcta es crítica para configurar timeouts reales.

    Args:
        freq_start : Frecuencia inicial en Hz  (≥ 0.2)
        freq_end   : Frecuencia final en Hz    (≤ 10_000_000)
        n_points   : Número de puntos del barrido
        scale      : 'log' | 'linear'
        average    : Número de promedios
        mdelay     : Delay de medición por punto (ms)
        tdelay     : Delay de trigger global (ms)

    Returns:
        dict con las siguientes claves:
          - total_seconds     : tiempo total estimado en segundos
          - frequencies       : array numpy de frecuencias del barrido
          - per_point_ms      : array numpy – ms por punto
          - bottleneck_freq   : frecuencia más lenta (Hz)
          - bottleneck_ms     : tiempo del punto más lento (ms)
          - fast_segment_s    : tiempo estimado de la mitad de alta frecuencia
          - slow_segment_s    : tiempo estimado de la mitad de baja frecuencia
          - recommended_segments : número mínimo de segmentos recomendado
          - human_readable    : string legible (p. ej. "3 min 12 s")
    """
    n_points = max(2, int(n_points))
    freq_start = max(0.2, float(freq_start))
    freq_end   = min(10_000_000.0, float(freq_end))

    if scale == 'log':
        freqs = np.logspace(np.log10(freq_start), np.log10(freq_end), n_points)
    else:
        freqs = np.linspace(freq_start, freq_end, n_points)

    # Intentar usar el perfil de timing real del hardware si está disponible.
    # Si no hay datos medidos, la función get_ms() cae en la fórmula teórica.
    try:
        from .hw_timing_profile import get_profile as _get_hw_profile
        _hw_profile = _get_hw_profile()
        per_point_ms = np.array([_hw_profile.get_ms(f, average) for f in freqs])
    except Exception:
        per_point_ms = np.array([_acquisition_time_ms(f, average) for f in freqs])

    per_point_ms += mdelay  # añadir delay de medición por punto

    # Overhead total:
    #   - _HW_SWEEP_STARTUP_MS: tiempo fijo de setup por cada llamada a perform_sweep()
    #     (inicialización HW + latencia de primer punto). Medido en benchmark real.
    #   - tdelay: delay global de trigger
    # El overhead de startup es dominante en sweeps cortos de alta frecuencia.
    total_ms = per_point_ms.sum() + tdelay + _HW_SWEEP_STARTUP_MS

    # Frecuencia "cuello de botella" (la más lenta)
    bottleneck_idx = int(np.argmax(per_point_ms))
    bottleneck_freq = float(freqs[bottleneck_idx])
    bottleneck_ms   = float(per_point_ms[bottleneck_idx])

    # Tiempos de la mitad lenta y rápida
    mid = n_points // 2
    slow_segment_s = float(per_point_ms[:mid].sum()) / 1000.0
    fast_segment_s = float(per_point_ms[mid:].sum()) / 1000.0

    total_s = total_ms / 1000.0

    # Segmentos recomendados: no más de 50 puntos por segmento si hay frecuencias < 10 Hz,
    # no más de 100 si hay frecuencias < 100 Hz, 200 en caso general.
    if freq_start < 0.5:
        max_seg = 1      # 0.2–0.5 Hz → 180–450 s/punto → 1 punto por segmento
    elif freq_start < 1.0:
        max_seg = 2      # 0.5–1 Hz   → 90–180 s/punto
    elif freq_start < 5.0:
        max_seg = 3      # 1–5 Hz     → 18–90 s/punto
    elif freq_start < 20.0:
        max_seg = 5      # 5–20 Hz    → 4.5–18 s/punto
    elif freq_start < 100.0:
        max_seg = 10     # 20–100 Hz  → 0.9–4.5 s/punto
    elif freq_start < 1000.0:
        max_seg = 30     # 100 Hz–1 kHz → 50ms–0.9s/punto
    elif freq_start < 10000.0:
        max_seg = 100    # 1–10 kHz   → 15–50 ms/punto (piso)
    else:
        max_seg = 200    # > 10 kHz   → piso 15 ms/punto
    recommended_segs = math.ceil(n_points / max_seg)

    # Texto legible
    if total_s < 1.0:
        human = f"{int(total_s * 1000)} ms"
    else:
        total_s_int = int(total_s)
        h = total_s_int // 3600
        m = (total_s_int % 3600) // 60
        s = total_s_int % 60
        if h > 0:
            human = f"{h}h {m}min {s}s"
        elif m > 0:
            human = f"{m}min {s}s"
        else:
            human = f"{s}s"

    return {
        'total_seconds'       : total_s,
        'frequencies'         : freqs,
        'per_point_ms'        : per_point_ms,
        'bottleneck_freq'     : bottleneck_freq,
        'bottleneck_ms'       : bottleneck_ms,
        'slow_segment_s'      : slow_segment_s,
        'fast_segment_s'      : fast_segment_s,
        'recommended_segments': recommended_segs,
        'human_readable'      : human,
    }


def max_points_per_segment(freq_start: float) -> int:
    """
    Devuelve el tamaño máximo de segmento recomendado según la frecuencia más baja.

    Basado en el modelo empírico de 36 ciclos de integración DFT del ADMX2001:
    - 0.2 Hz: ~180 s/punto → solo 1 punto por segmento es tolerable
    - 3 kHz+: piso de 15 ms/punto → segmentos grandes sin problema

    El objetivo es que ningún segmento supere ~3-5 minutos de medición total,
    para que los timeouts y el feedback al usuario sean razonables.

    Args:
        freq_start: Frecuencia mínima del segmento en Hz

    Returns:
        Número máximo de puntos por segmento
    """
    if freq_start < 0.5:
        return 1      # 0.2–0.5 Hz → 180–450 s/pto → 1 pto max (3-7.5 min/seg)
    if freq_start < 1.0:
        return 2      # 0.5–1 Hz   → 90–180 s/pto  → 2 ptos  (3-6 min/seg)
    if freq_start < 5.0:
        return 3      # 1–5 Hz     → 18–90 s/pto   → 3 ptos  (~ 3 min/seg)
    if freq_start < 20.0:
        return 5      # 5–20 Hz    → 4.5–18 s/pto  → 5 ptos  (1-1.5 min/seg)
    if freq_start < 100.0:
        return 10     # 20–100 Hz  → 0.9–4.5 s/pto → 10 ptos (1-2 min/seg)
    if freq_start < 1000.0:
        return 30     # 100 Hz–1 kHz → 50ms–0.9s/pto → 30 ptos (1-2 min/seg)
    if freq_start < 10000.0:
        return 100    # 1–10 kHz   → piso 15-50 ms/pto → 100 ptos (1-5 s/seg)
    return 200        # > 10 kHz   → piso 15 ms/pto → 200 ptos (3 s/seg)


def save_sweep_data_to_csv(data: Dict[str, List], filename: str = None) -> str:
    """
    Guarda datos de barrido de frecuencia en un archivo CSV.
    
    Args:
        data: Diccionario con datos del barrido:
            - param: Lista de frecuencias (Hz)
            - z_real: Lista de partes reales de impedancia (Ω)
            - z_imag: Lista de partes imaginarias de impedancia (Ω)
            - z_mag: Lista de magnitudes de impedancia (Ω)
            - phase: Lista de fases (radianes)
        filename: Nombre del archivo (opcional). Si no se proporciona,
                 se genera automáticamente con timestamp.
    
    Returns:
        Nombre del archivo creado
    
    Raises:
        ValueError: Si los datos no tienen la estructura correcta
    """
    import csv
    from datetime import datetime
    
    # Validar estructura de datos
    required_keys = ['param', 'z_real', 'z_imag', 'z_mag', 'phase']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Falta la clave requerida: {key}")
        if not isinstance(data[key], list) or len(data[key]) == 0:
            raise ValueError(f"Datos inválidos para {key}: debe ser una lista no vacía")
    
    # Verificar que todas las listas tengan la misma longitud
    lengths = [len(data[key]) for key in required_keys]
    if len(set(lengths)) != 1:
        raise ValueError(f"Todas las listas deben tener la misma longitud. Longitudes encontradas: {dict(zip(required_keys, lengths))}")
    
    # Generar nombre de archivo si no se proporciona
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sweep_data_{timestamp}.csv"
    
    # Asegurar extensión .csv
    if not filename.lower().endswith('.csv'):
        filename += '.csv'
    
    # Crear directorio si no existe
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    
    # Escribir archivo CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['frequency_hz', 'z_real_ohm', 'z_imag_ohm', 'z_magnitude_ohm', 'phase_rad', 'phase_deg']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escribir encabezado
        writer.writeheader()
        
        # Escribir datos
        for i in range(len(data['param'])):
            row = {
                'frequency_hz': data['param'][i],
                'z_real_ohm': data['z_real'][i],
                'z_imag_ohm': data['z_imag'][i],
                'z_magnitude_ohm': data['z_mag'][i],
                'phase_rad': data['phase'][i],
                'phase_deg': np.degrees(data['phase'][i])  # Convertir a grados
            }
            writer.writerow(row)
    
    return filename


def load_sweep_data_from_csv(filepath: str) -> Dict[str, List]:
    """
    Carga datos de barrido de frecuencia desde un archivo CSV.
    
    Args:
        filepath: Ruta al archivo CSV
    
    Returns:
        Diccionario con datos del barrido:
            - param: Lista de frecuencias (Hz)
            - z_real: Lista de partes reales de impedancia (Ω)
            - z_imag: Lista de partes imaginarias de impedancia (Ω)
            - z_mag: Lista de magnitudes de impedancia (Ω)
            - phase: Lista de fases (radianes)
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el formato del CSV es inválido
    """
    import csv
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
    
    data = {
        'param': [],
        'z_real': [],
        'z_imag': [],
        'z_mag': [],
        'phase': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Verificar encabezados requeridos
            required_headers = ['frequency_hz', 'z_real_ohm', 'z_imag_ohm', 'z_magnitude_ohm', 'phase_rad']
            missing_headers = [h for h in required_headers if h not in reader.fieldnames]
            if missing_headers:
                raise ValueError(f"Encabezados requeridos faltantes: {missing_headers}")
            
            # Leer datos
            for row_num, row in enumerate(reader, start=2):  # +2 porque header es línea 1
                try:
                    data['param'].append(float(row['frequency_hz']))
                    data['z_real'].append(float(row['z_real_ohm']))
                    data['z_imag'].append(float(row['z_imag_ohm']))
                    data['z_mag'].append(float(row['z_magnitude_ohm']))
                    data['phase'].append(float(row['phase_rad']))
                except (ValueError, KeyError) as e:
                    raise ValueError(f"Error en línea {row_num}: {str(e)}")
    
    except UnicodeDecodeError:
        raise ValueError("El archivo CSV debe estar codificado en UTF-8")
    except Exception as e:
        raise ValueError(f"Error al leer el archivo CSV: {str(e)}")
    
    # Validar que se cargaron datos
    if len(data['param']) == 0:
        raise ValueError("El archivo CSV no contiene datos válidos")
    
    return data


def list_csv_files() -> List[str]:
    """
    Lista todos los archivos CSV en el directorio data/.
    
    Returns:
        Lista de nombres de archivos CSV ordenados por fecha de modificación (más reciente primero)
    """
    
    data_dir = 'data'
    if not os.path.exists(data_dir):
        return []
    
    csv_files = []
    for filename in os.listdir(data_dir):
        if filename.lower().endswith('.csv'):
            filepath = os.path.join(data_dir, filename)
            if os.path.isfile(filepath):
                csv_files.append(filename)
    
    # Ordenar por fecha de modificación (más reciente primero)
    csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(data_dir, x)), reverse=True)
    
    return csv_files
