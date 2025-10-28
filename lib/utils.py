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


def list_available_ports() -> List[Dict[str, str]]:
    """
    Lista todos los puertos serie disponibles en el sistema.
    
    Returns:
        Lista de diccionarios con información de puertos:
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
    for port in serial.tools.list_ports.comports():
        ports.append({
            'device': port.device,
            'description': port.description,
            'hwid': port.hwid,
            'manufacturer': port.manufacturer or 'Unknown'
        })
    return ports


def find_admx2001_devices() -> List[str]:
    """
    Busca dispositivos ADMX2001 conectados.
    
    Intenta identificar puertos que probablemente sean ADMX2001
    basándose en descriptores conocidos (FTDI, USB Serial).
    
    Returns:
        Lista de rutas de dispositivos potenciales.
    
    Note:
        Esta función usa heurísticas; no garantiza que el dispositivo
        sea realmente un ADMX2001. Use test_device_connection() para verificar.
    """
    potential_devices = []
    for port in serial.tools.list_ports.comports():
        # ADMX2001 usa cable FTDI USB-to-UART (TTL-232R-RPI)
        if 'FTDI' in port.description or 'USB Serial' in port.description:
            potential_devices.append(port.device)
    return potential_devices


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


def clean_response_line(line: str) -> str:
    """
    Limpia una línea de respuesta del dispositivo.
    
    Remueve:
    - Códigos ANSI de escape (secuencias de escape estándar)
    - Códigos de control de cursor VT100 (ESC 7, ESC 8, etc.)
    - Prompts (ADMX2001>)
    - Espacios en blanco al inicio/final
    
    Args:
        line: Línea cruda del dispositivo
    
    Returns:
        Línea limpia
    """
    # Remover códigos ANSI estándar (secuencias de escape complejas)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    line = ansi_escape.sub('', line)
    
    # Remover códigos de control de cursor VT100 simples (ESC + dígito/letra)
    # ESC 7 = save cursor, ESC 8 = restore cursor, etc.
    vt100_control = re.compile(r'\x1B[0-9A-Za-z]')
    line = vt100_control.sub('', line)
    
    # Remover cualquier ESC solitario que pueda quedar
    line = line.replace('\x1B', '')
    
    # Remover prompt
    line = line.replace('ADMX2001>', '')
    
    # Limpiar espacios
    return line.strip()


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


def estimate_measurement_time(frequency: float, average: int, count: int, 
                              mdelay: float = 1.0, tdelay: float = 4.0) -> float:
    """
    Estima el tiempo de medición basado en parámetros.
    
    Según documentación, el tiempo depende de:
    - Frecuencia (necesita mínimo 3 ciclos)
    - Average y count
    - Delays configurados
    - Overhead de comunicación
    
    Args:
        frequency: Frecuencia en Hz
        average: Número de promedios
        count: Número de muestras
        mdelay: Delay de medición (ms)
        tdelay: Delay de trigger (ms)
    
    Returns:
        Tiempo estimado en segundos
    """
    # Tiempo mínimo por ciclo (3 ciclos mínimo)
    if frequency > 0:
        min_acquisition_time = (3.0 / frequency) * 1000  # en ms
    else:
        min_acquisition_time = 50  # Para modo DC
    
    # Tiempo por muestra individual
    sample_time = max(min_acquisition_time, 10)  # mínimo 10ms
    
    # Tiempo total considerando average y count
    measurement_time = sample_time * count + mdelay * count + tdelay
    
    # Overhead de comunicación
    communication_overhead = 50  # ms aproximado
    
    total_time_ms = measurement_time + communication_overhead
    return total_time_ms / 1000.0  # convertir a segundos


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
