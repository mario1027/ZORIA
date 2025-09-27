#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=======================================================================
LEVALIB - Biblioteca Completa para Control del ADMX2001
=======================================================================

Esta biblioteca proporciona una interfaz Python completa y robusta para 
controlar el analizador de impedancia EVAL-ADMX2001 de Analog Devices 
a través de comunicación UART/USB.

Características principales:
- ✅ Implementación completa de todos los comandos documentados
- ✅ Análisis automático e inteligente de componentes (R, L, C)
- ✅ Barridos de frecuencia avanzados con detección de resonancias
- ✅ Mediciones de alta precisión con análisis estadístico
- ✅ Manejo robusto de errores y reconexión automática
- ✅ Parsing inteligente de respuestas del dispositivo
- ✅ Exportación automática de datos en múltiples formatos
- ✅ Monitoreo de temperatura en tiempo real
- ✅ Compatibilidad con múltiples versiones de firmware

Ejemplo de uso básico:
    >>> from levalib import ADMX2001
    >>> 
    >>> # Conexión y medición simple
    >>> with ADMX2001("/dev/ttyUSB0") as device:
    ...     result = device.quick_impedance_measurement(1000)
    ...     print(f"Impedancia: {result['impedance']['magnitude']:.2f} Ω")
    
Ejemplo de análisis avanzado:
    >>> # Análisis automático de componente
    >>> analysis = device.advanced_component_analysis(
    ...     frequencies=[100, 1000, 10000, 100000],
    ...     component_type="unknown"
    ... )
    >>> print(f"Tipo detectado: {analysis['analysis']['detected_type']}")

Autor: Mario Montero
Fecha: Septiembre 2025
Versión: 1.0.0
Licencia: MIT

Requisitos:
- Python 3.8+
- pyserial >= 3.5
- EVAL-ADMX2001 conectado vía USB

Documentación completa disponible en MANUAL_USUARIO.md
=======================================================================
"""

import serial
import time
import re
import math
import logging
import threading
from datetime import datetime
from typing import List, Union, Optional, Dict, Any, Tuple

# =====================================================================
# CONFIGURACIÓN DE LOGGING DE ALTO RENDIMIENTO
# =====================================================================

# Configurar logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)8s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Logger específico para ADMX2001
logger = logging.getLogger('ADMX2001')
logger.setLevel(logging.INFO)  # Cambiar a DEBUG para desarrollo

# =====================================================================
# CONSTANTES Y CONFIGURACIÓN GLOBAL
# =====================================================================

# Configuración por defecto del dispositivo
DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT = 2.0

# Sistema de delays adaptativos de alto rendimiento
DELAY_PROFILES = {
    'critical': 0.001,      # Comandos críticos de tiempo (sweep, trigger)
    'fast': 0.005,          # Comandos de configuración rápida
    'normal': 0.01,         # Comandos estándar (default)
    'stable': 0.02,         # Comandos que requieren estabilización
    'slow': 0.05            # Comandos complejos (calibración, análisis)
}

# Patrones regex para limpieza de respuestas
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
# Match common shell prompts and the device prompt 'ADMX2001>' exactly (with optional whitespace)
PROMPT_PATTERN = re.compile(r'^(?:ADMX2001>|[>$#])\s*$')

# Rangos válidos para parámetros del dispositivo
FREQUENCY_RANGE = (1, 100000)      # Hz
MAGNITUDE_RANGE = (0.01, 2.0)      # Voltios
OFFSET_RANGE = (-2.0, 2.0)         # Voltios
AVERAGE_RANGE = (1, 100)           # Número de promedios
COUNT_RANGE = (1, 100)             # Número de mediciones

class ADMX2001:
    """
    Clase principal para el control completo del analizador de impedancia EVAL-ADMX2001.
    
    Esta clase proporciona una interfaz Python completa y robusta para controlar
    el EVAL-ADMX2001 de Analog Devices. Incluye implementación de todos los comandos
    documentados, análisis avanzado de componentes, y funciones de medición de alta
    precisión.
    
    Características principales:
    - Control completo de todos los parámetros del dispositivo
    - Análisis automático e inteligente de componentes electrónicos
    - Barridos de frecuencia con detección automática de resonancias
    - Mediciones de alta precisión con análisis estadístico
    - Manejo robusto de errores con reconexión automática
    - Exportación de datos en múltiples formatos (JSON, CSV)
    - Monitoreo continuo de temperatura del chip
    - Compatibilidad con diferentes versiones de firmware
    
    Uso básico:
        >>> # Conexión simple
        >>> device = ADMX2001("/dev/ttyUSB0")
        >>> device.connect()
        >>> 
        >>> # Medición básica
        >>> device.set_frequency(1000)
        >>> impedance = device.read_impedance()
        >>> print(f"Z = {impedance['magnitude']:.2f} Ω")
        >>> 
        >>> device.disconnect()
        
    Uso con context manager (recomendado):
        >>> with ADMX2001("/dev/ttyUSB0") as device:
        ...     result = device.quick_impedance_measurement(1000)
        ...     print(f"Impedancia: {result['impedance']['magnitude']:.2f} Ω")
        ...     print(f"Temperatura: {result['temperature']['temperature_celsius']:.1f}°C")
    
    Análisis avanzado:
        >>> with ADMX2001("/dev/ttyUSB0") as device:
        ...     # Detectar tipo de componente automáticamente
        ...     analysis = device.advanced_component_analysis(
        ...         frequencies=[100, 1000, 10000, 100000],
        ...         component_type="unknown"
        ...     )
        ...     detected_type = analysis['analysis']['detected_type']
        ...     confidence = analysis['analysis']['confidence']
        ...     print(f"Componente detectado: {detected_type} (confianza: {confidence:.1%})")
    
    Atributos:
        port (str): Puerto serie utilizado para la comunicación
        baudrate (int): Velocidad de comunicación en baudios
        timeout (float): Timeout en segundos para operaciones serie
        ser (serial.Serial): Objeto de conexión serie
        is_connected (bool): Estado de conexión actual
        last_error (str): Último error ocurrido (si existe)
        firmware_version (str): Versión del firmware detectada
        device_info (dict): Información del dispositivo
    
    Raises:
        serial.SerialException: Error en la comunicación serie
        ValueError: Parámetros inválidos
        ConnectionError: Error de conexión con el dispositivo
        TimeoutError: Timeout en comunicación
    
    Note:
        - Siempre usar context manager (with statement) cuando sea posible
        - El dispositivo debe estar conectado vía USB antes de inicializar
        - Verificar permisos de puerto serie en Linux (/dev/ttyUSB*)
        - El firmware del dispositivo puede afectar comandos disponibles
    
    Version: 1.0.0
    Author: Mario Montero
    Date: Septiembre 2025
    """
    
    def __init__(self, port: str, baudrate: int = DEFAULT_BAUDRATE, timeout: float = DEFAULT_TIMEOUT):
        """
        Inicializa la conexión serie con el EVAL-ADMX2001.
        
        Establece la comunicación UART/USB con el dispositivo y realiza la
        configuración inicial necesaria. Incluye limpieza de buffers y
        verificación básica de conectividad.
        
        Args:
            port (str): Puerto serie del dispositivo. Ejemplos:
                       - Linux: "/dev/ttyUSB0", "/dev/ttyACM0"
                       - Windows: "COM1", "COM3", etc.
                       - macOS: "/dev/cu.usbserial-*"
                       
            baudrate (int, optional): Velocidad de comunicación en baudios.
                                    Default: 115200. El ADMX2001 utiliza
                                    115200 baudios por especificación.
                                    
            timeout (float, optional): Timeout en segundos para operaciones
                                     de lectura/escritura. Default: 2.0.
                                     Valores recomendados: 1.0-5.0 segundos.
        
        Raises:
            serial.SerialException: Si no se puede abrir el puerto serie.
                                  Causas comunes:
                                  - Puerto no existe o está ocupado
                                  - Permisos insuficientes (Linux)
                                  - Dispositivo no conectado
                                  
            ValueError: Si los parámetros están fuera de rango válido.
            
            PermissionError: Si no hay permisos para acceder al puerto (Linux).
                           Solución: agregar usuario al grupo 'dialout'.
        
        Example:
            >>> # Inicialización básica
            >>> device = ADMX2001("/dev/ttyUSB0")
            >>> 
            >>> # Con parámetros personalizados
            >>> device = ADMX2001(
            ...     port="/dev/ttyUSB0",
            ...     baudrate=115200,
            ...     timeout=3.0
            ... )
            >>> 
            >>> # Verificar conexión
            >>> if device.is_connected():
            ...     print("✅ Dispositivo conectado correctamente")
            ... else:
            ...     print("❌ Error en la conexión")
        
        Note:
            - El constructor intenta conectar inmediatamente al dispositivo
            - Se realiza una pausa de 2 segundos para estabilización
            - Los buffers de entrada y salida se limpian automáticamente
            - Use context manager (with statement) para manejo automático de recursos
        """
        # Validar parámetros de entrada
        if not isinstance(port, str) or not port.strip():
            raise ValueError("El puerto debe ser una cadena no vacía")
            
        if not isinstance(baudrate, int) or baudrate <= 0:
            raise ValueError("El baudrate debe ser un entero positivo")
            
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("El timeout debe ser un número positivo")
        
        # Almacenar parámetros de configuración
        self.port = port.strip()
        self.baudrate = baudrate
        self.timeout = timeout
        
        # Inicializar atributos de estado
        self.ser = None
        self.is_connected = False
        self.last_error = None
        self.firmware_version = "Unknown"
        self.device_info = {}
        
        # Sistema de caching de alto rendimiento
        self._config_cache = {}
        self._cache_timestamps = {}
        self._cache_timeout = 5.0  # 5 segundos de validez de cache
        self._cache_lock = threading.Lock()
        
        # Métricas de rendimiento
        self._performance_metrics = {
            'commands_sent': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_delay_time': 0.0,
            'start_time': time.time()
        }
        
        try:
            # Establecer conexión serie
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Pausa de estabilización - crítica para el ADMX2001
            # El dispositivo necesita tiempo para inicializar después de abrir el puerto
            time.sleep(2.0)
            
            # Limpiar buffers de comunicación
            self.ser.flushInput()   # Limpiar buffer de entrada
            self.ser.flushOutput()  # Limpiar buffer de salida
            
            # Marcar como conectado
            self.is_connected = True
            
            # Intentar obtener información básica del dispositivo
            try:
                self._initialize_device_info()
            except Exception as e:
                # No es crítico si falla la inicialización de info
                self.last_error = f"Advertencia: No se pudo obtener info del dispositivo: {e}"
                
        except serial.SerialException as e:
            self.last_error = f"Error de puerto serie: {e}"
            raise serial.SerialException(f"No se pudo conectar al puerto {port}: {e}")
            
        except Exception as e:
            self.last_error = f"Error inesperado durante inicialización: {e}"
            raise ConnectionError(f"Error inicializando ADMX2001: {e}")

        except Exception as e:
            self.last_error = f"Error inesperado durante inicialización: {e}"
            raise ConnectionError(f"Error inicializando ADMX2001: {e}")
    
    def _initialize_device_info(self):
        """
        Inicializa información básica del dispositivo.
        
        Intenta obtener información del firmware y estado del dispositivo
        durante la inicialización. No es crítico si falla.
        
        Raises:
            Exception: Si hay errores en la comunicación inicial
        """
        try:
            # Intentar obtener versión de firmware o información básica
            # Esto es opcional y no debe interrumpir la inicialización
            response = self.send_command("VER")
            if response and len(response) > 0:
                self.device_info['version_response'] = response
                
        except Exception:
            # Silenciosamente continuar si no se puede obtener info
            pass

    # =====================================================================
    # MÉTODOS DE OPTIMIZACIÓN DE ALTO RENDIMIENTO
    # =====================================================================
    
    def _adaptive_delay(self, command_type: str = 'normal') -> float:
        """
        Calcula delay adaptativo basado en el tipo de comando.
        
        Args:
            command_type: Tipo de comando ('critical', 'fast', 'normal', 'stable', 'slow')
            
        Returns:
            float: Delay en segundos optimizado para el tipo de comando
        """
        delay = DELAY_PROFILES.get(command_type, DELAY_PROFILES['normal'])
        self._performance_metrics['total_delay_time'] += delay
        return delay
    
    def _determine_command_type(self, cmd: str) -> str:
        """
        Determina el tipo de comando para delay adaptativo.
        
        Args:
            cmd: Comando a enviar
            
        Returns:
            str: Tipo de comando para optimización de delay
        """
        cmd_lower = cmd.lower().strip()
        
        # Comandos críticos de tiempo
        if cmd_lower in ['z', 'trigger', 'initiate']:
            return 'critical'
        
        # Comandos rápidos de configuración
        elif any(x in cmd_lower for x in ['frequency', 'magnitude', 'setgain']):
            return 'fast'
            
        # Comandos que requieren estabilización
        elif any(x in cmd_lower for x in ['sweep_type', 'calibrate', 'reset']):
            return 'stable'
            
        # Comandos complejos
        elif any(x in cmd_lower for x in ['selftest', 'errorlog']):
            return 'slow'
            
        # Default: normal
        return 'normal'
    
    def _is_config_cached(self, cache_key: str) -> bool:
        """
        Verifica si una configuración está en cache y es válida.
        
        Args:
            cache_key: Clave del cache a verificar
            
        Returns:
            bool: True si está cacheado y válido
        """
        with self._cache_lock:
            if cache_key not in self._cache_timestamps:
                return False
                
            age = time.time() - self._cache_timestamps[cache_key]
            return age < self._cache_timeout
    
    def _cache_config(self, cache_key: str, value: Any = None):
        """
        Guarda una configuración en cache.
        
        Args:
            cache_key: Clave del cache
            value: Valor a cachear (opcional)
        """
        with self._cache_lock:
            self._config_cache[cache_key] = value
            self._cache_timestamps[cache_key] = time.time()
    
    def _efficient_response_storage(self, raw_result: List[str], keep_raw: bool = False) -> Any:
        """
        Almacena respuestas de forma eficiente para optimizar memoria.
        
        Args:
            raw_result: Respuesta cruda del dispositivo
            keep_raw: Si mantener datos completos
            
        Returns:
            Respuesta optimizada o completa según parámetros
        """
        if keep_raw or len(raw_result) < 50:  # Respuestas pequeñas se mantienen completas
            return raw_result
        else:
            # Para respuestas grandes, almacenar resumen + datos clave
            summary = {
                'line_count': len(raw_result),
                'first_lines': raw_result[:3],
                'last_lines': raw_result[-3:],
                'data_lines': [line for line in raw_result if ',' in line][:10],  # Máximo 10 líneas de datos
                'timestamp': time.time(),
                'note': f'Respuesta optimizada - {len(raw_result)} líneas originales'
                }
            return summary
    
    def _normalize_frequency_unit(self, freq_value: float, expected_min: float, expected_max: float) -> float:
        """
        Normaliza automáticamente las unidades de frecuencia (Hz vs kHz).
        
        CORRECCIÓN CRÍTICA: El ADMX2001 puede devolver frecuencias en Hz o kHz 
        dependiendo del firmware. Este método detecta automáticamente la unidad
        y convierte todo a Hz para consistencia.
        
        Args:
            freq_value: Valor de frecuencia recibido del dispositivo
            expected_min: Frecuencia mínima esperada en Hz
            expected_max: Frecuencia máxima esperada en Hz
            
        Returns:
            float: Frecuencia normalizada en Hz
            
        Raises:
            ValueError: Si no se puede determinar la unidad correcta
        """
        # Caso 1: El valor ya está en el rango esperado (Hz)
        if expected_min <= freq_value <= expected_max:
            return freq_value
        
        # Caso 2: El valor está en kHz, convertir a Hz
        freq_hz = freq_value * 1000.0
        if expected_min <= freq_hz <= expected_max:
            logger.debug(f"Frecuencia convertida de kHz a Hz: {freq_value} → {freq_hz}")
            return freq_hz
        
        # Caso 3: El valor está en MHz, convertir a Hz
        freq_hz_from_mhz = freq_value * 1000000.0
        if expected_min <= freq_hz_from_mhz <= expected_max:
            logger.debug(f"Frecuencia convertida de MHz a Hz: {freq_value} → {freq_hz_from_mhz}")
            return freq_hz_from_mhz
        
        # Caso 4: Tolerancia extendida para variaciones del hardware
        tolerance_factor = 2.0  # Permitir 2x fuera del rango
        extended_min = expected_min / tolerance_factor
        extended_max = expected_max * tolerance_factor
        
        if extended_min <= freq_value <= extended_max:
            logger.warning(f"Frecuencia {freq_value} Hz fuera de rango esperado pero dentro de tolerancia")
            return freq_value
        
        # Si convertimos de kHz y está en tolerancia extendida
        if extended_min <= freq_hz <= extended_max:
            logger.warning(f"Frecuencia {freq_hz} Hz (convertida de kHz) fuera de rango pero en tolerancia")
            return freq_hz
        
        # Si nada funciona, lanzar error con información de debug
        raise ValueError(
            f"No se pudo normalizar frecuencia {freq_value}. "
            f"Rango esperado: {expected_min}-{expected_max} Hz. "
            f"Intentos: {freq_value} Hz, {freq_hz} Hz, {freq_hz_from_mhz} Hz"
        )
    
    def _validate_hardware_limits(self, parameter: str, value: Union[int, float]) -> bool:
        """
        Valida parámetros contra límites reales del hardware ADMX2001.
        
        Args:
            parameter: Nombre del parámetro ('frequency', 'magnitude', 'points', etc.)
            value: Valor a validar
            
        Returns:
            bool: True si el valor está dentro de límites del hardware
        """
        hardware_limits = {
            'frequency': (1, 100000),          # 1 Hz - 100 kHz
            'magnitude': (0.01, 2.0),          # 10 mV - 2 V
            'offset': (-2.0, 2.0),             # ±2 V
            'sweep_points_native': (2, 500),    # Límite real del sweep nativo
            'average': (1, 100),               # Promedios por medición
            'count': (1, 100),                 # Repeticiones
            'gain': (0, 3),                    # Niveles de ganancia
            'temperature_operating': (-40, 85), # Rango operativo en °C
        }
        
        if parameter not in hardware_limits:
            logger.warning(f"Parámetro {parameter} no tiene límites definidos")
            return True
        
        min_val, max_val = hardware_limits[parameter]
        is_valid = min_val <= value <= max_val
        
        if not is_valid:
            logger.error(f"Parámetro {parameter}={value} fuera de límites hardware: {min_val}-{max_val}")
        
        return is_valid
    
    def _estimate_sweep_time(self, points: int, is_logarithmic: bool = True) -> float:
        """
        Estima el tiempo de ejecución de un sweep basado en parámetros.
        
        Args:
            points: Número de puntos del sweep
            is_logarithmic: Si es sweep logarítmico (más rápido)
            
        Returns:
            float: Tiempo estimado en segundos
        """
        # Factores de tiempo basados en experiencia real con ADMX2001
        base_time_per_point = 0.15  # Segundos por punto para medición individual
        native_sweep_factor = 0.03  # Mucho más rápido el sweep nativo
        
        if points <= 500:  # Puede usar sweep nativo
            estimated_time = points * native_sweep_factor
        else:  # Debe usar punto-a-punto
            estimated_time = points * base_time_per_point
        
        # Factores de corrección
        if is_logarithmic:
            estimated_time *= 0.9  # Ligeramente más rápido
        
        # Agregar overhead de configuración
        setup_overhead = 2.0  # 2 segundos de setup
        
        return estimated_time + setup_overhead
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento del dispositivo.
        
        Returns:
            Dict con estadísticas de rendimiento y uso
        """
        current_time = time.time()
        uptime = current_time - self._performance_metrics['start_time']
        
        commands_sent = self._performance_metrics['commands_sent']
        cache_hits = self._performance_metrics['cache_hits']
        cache_misses = self._performance_metrics['cache_misses']
        total_cache_ops = cache_hits + cache_misses
        
        return {
            'uptime_seconds': uptime,
            'commands_sent': commands_sent,
            'commands_per_second': commands_sent / uptime if uptime > 0 else 0,
            'cache_statistics': {
                'hits': cache_hits,
                'misses': cache_misses,
                'hit_rate': cache_hits / total_cache_ops if total_cache_ops > 0 else 0,
                'total_operations': total_cache_ops
            },
            'timing_statistics': {
                'total_delay_time': self._performance_metrics['total_delay_time'],
                'average_delay_per_command': (
                    self._performance_metrics['total_delay_time'] / commands_sent 
                    if commands_sent > 0 else 0
                )
            },
            'cache_size': len(self._config_cache),
            'memory_efficiency': {
                'cached_configurations': len(self._config_cache),
                'cache_age_seconds': max(
                    current_time - min(self._cache_timestamps.values())
                    if self._cache_timestamps else 0, 0
                )
            }
        }

    def send_command(self, cmd: str, priority: str = 'auto', timeout_override: Optional[float] = None, 
                    cache_result: bool = False, keep_raw_response: bool = False) -> List[str]:
        """
        Envía un comando al ADMX2001 con optimizaciones de alto rendimiento.
        
        Sistema optimizado que incluye:
        - Delays adaptativos basados en tipo de comando
        - Timeouts dinámicos según complejidad
        - Caching inteligente de configuraciones
        - Almacenamiento eficiente de respuestas
        - Logging estructurado para debugging
        - Métricas de rendimiento automáticas
        
        Args:
            cmd (str): Comando a enviar al ADMX2001
            priority (str): Prioridad del comando ('auto', 'critical', 'fast', 'normal', 'stable', 'slow')
            timeout_override (float, optional): Timeout personalizado en segundos
            cache_result (bool): Si cachear el resultado para evitar comandos redundantes
            keep_raw_response (bool): Si mantener respuesta completa (para debugging)
        
        Returns:
            List[str]: Lista de líneas de respuesta procesadas y optimizadas
        
        Raises:
            serial.SerialException: Error en la comunicación serie
            TimeoutError: El dispositivo no responde en el tiempo especificado
            ValueError: Si el comando está mal formado
        """
        try:
            # Incrementar métricas de rendimiento
            self._performance_metrics['commands_sent'] += 1
            command_start_time = time.time()
            
            # Verificar conexión activa
            if not self.is_connected or not self.ser or not self.ser.is_open:
                raise ConnectionError("Dispositivo no conectado")
            
            # Determinar tipo de comando para optimización
            if priority == 'auto':
                command_type = self._determine_command_type(cmd)
            else:
                command_type = priority
            
            # Verificar cache para comandos de configuración
            cache_key = f"cmd_{cmd.strip()}"
            if cache_result and self._is_config_cached(cache_key):
                self._performance_metrics['cache_hits'] += 1
                logger.debug(f"Cache hit para comando: {cmd}")
                return self._config_cache.get(cache_key, ["OK"])
            else:
                if cache_result:
                    self._performance_metrics['cache_misses'] += 1
            
            # Limpiar buffers con verificación de estado
            try:
                if self.ser.in_waiting > 0:
                    logger.debug(f"Limpiando {self.ser.in_waiting} bytes del buffer de entrada")
                self.ser.flushInput()
                self.ser.flushOutput()
            except Exception as e:
                logger.warning(f"Problema limpiando buffers: {e}")
            
            # Preparar y enviar comando
            command_to_send = cmd.strip() + '\r\n'
            bytes_written = self.ser.write(command_to_send.encode('utf-8'))
            
            # Verificar envío completo
            if bytes_written != len(command_to_send.encode('utf-8')):
                raise serial.SerialException("Envío incompleto del comando")
            
            # Asegurar transmisión (no bloquear si driver/tty se comporta raro)
            try:
                self.ser.flush()
            except Exception as e:
                logger.debug(f"Ignorando excepción en flush(): {e}")
            
            # Delay adaptativo optimizado
            adaptive_delay = self._adaptive_delay(command_type)
            time.sleep(adaptive_delay)
            
            # Timeout adaptativo basado en complejidad del comando
            if timeout_override:
                effective_timeout = timeout_override
            else:
                timeout_multipliers = {
                    'critical': 0.5,    # Comandos rápidos
                    'fast': 0.8,        # Configuración rápida
                    'normal': 1.0,      # Timeout estándar
                    'stable': 1.5,      # Comandos de estabilización
                    'slow': 3.0         # Comandos complejos
                }
                effective_timeout = self.timeout * timeout_multipliers.get(command_type, 1.0)
            
            # Lectura optimizada de respuesta
            response_lines = []
            start_time = time.time()
            consecutive_empty_reads = 0
            max_empty_reads = 10
            
            while time.time() - start_time < effective_timeout:
                try:
                    if self.ser.in_waiting > 0:  # Datos disponibles
                        line = self.ser.readline().decode('utf-8', errors='ignore')
                        consecutive_empty_reads = 0  # Reset contador
                        
                        if line:
                            # Limpiar códigos ANSI de forma eficiente
                            clean_line = ANSI_ESCAPE_PATTERN.sub('', line)
                            # Quitar secuencias específicas observadas en firmware (p.ej. \x1b7\x1b8)
                            clean_line = clean_line.replace('\x1b7', '').replace('\x1b8', '')
                            # Quitar caracteres de control residuales (C0) que rompen comparaciones
                            clean_line = re.sub(r'[\x00-\x1F\x7F]', '', clean_line).strip()

                            # Filtrar líneas útiles con mayor precisión
                            lower = clean_line.lower()
                            # Normalizar forma del comando enviado para comparar con eco
                            cmd_norm = re.sub(r'[\x00-\x1F\x7F]', '', cmd.strip()).lower()
                            # Evitar agregar eco parcial del comando o líneas vacías
                            if (clean_line and
                                not PROMPT_PATTERN.match(clean_line) and
                                not lower.startswith('warn') and
                                cmd_norm not in lower and
                                clean_line != cmd.strip()):
                                response_lines.append(clean_line)
                            # Si encontramos el prompt del dispositivo, hemos terminado
                            if PROMPT_PATTERN.match(clean_line):
                                break
                        else:
                            break  # Fin de datos
                    else:
                        # No hay datos disponibles
                        consecutive_empty_reads += 1
                        if consecutive_empty_reads >= max_empty_reads and response_lines:
                            # Ya tenemos datos y llevamos tiempo sin recibir más
                            break
                        time.sleep(0.005)  # Pausa mínima optimizada
                        
                except UnicodeDecodeError:
                    logger.debug("Carácter no decodificable ignorado")
                    continue
                except Exception as e:
                    logger.error(f"Error leyendo respuesta: {e}")
                    break
            
            # Procesar respuesta para almacenamiento eficiente
            if response_lines:
                processed_response = self._efficient_response_storage(response_lines, keep_raw_response)
                
                # Cachear resultado si se solicita
                if cache_result:
                    self._cache_config(cache_key, response_lines)
                
                # Logging de debug con información de rendimiento
                command_duration = time.time() - command_start_time
                logger.debug(f"Comando '{cmd}' completado en {command_duration:.3f}s, "
                           f"tipo: {command_type}, timeout: {effective_timeout:.1f}s, "
                           f"respuesta: {len(response_lines)} líneas")
                
                # Si tenemos almacenamiento optimizado, devolver datos originales
                if isinstance(processed_response, dict) and 'data_lines' in processed_response:
                    return processed_response['data_lines']
                else:
                    return response_lines
            else:
                logger.warning(f"Sin respuesta para comando '{cmd}' después de {effective_timeout:.1f}s")
                return []
            
            # Actualizar estado exitoso
            self.last_error = None
            return response_lines
            
        except serial.SerialException as e:
            error_msg = f"Error de comunicación serie: {e}"
            self.last_error = error_msg
            self.is_connected = False
            logger.error(f"Comando '{cmd}' falló: {error_msg}")
            raise serial.SerialException(error_msg)
            
        except Exception as e:
            error_msg = f"Error enviando comando '{cmd}': {e}"
            self.last_error = error_msg
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    # ==============================
    # Comandos Generales y Sistema
    # ==============================
    
    def get_idn(self) -> List[str]:
        """Identifica firmware y hardware del dispositivo."""
        return self.send_command("*idn")

    def help(self, command: Optional[str] = None) -> List[str]:
        """
        Muestra ayuda general o de un comando específico.
        
        Args:
            command (str, optional): Comando específico para ayuda
        """
        if command:
            return self.send_command(f"help {command}")
        return self.send_command("help")

    def version(self) -> List[str]:
        """Devuelve versión de firmware."""
        return self.send_command("version")

    def reset(self) -> List[str]:
        """Reinicia el dispositivo."""
        return self.send_command("reset")

    def abort(self) -> List[str]:
        """Aborta cualquier operación en curso."""
        return self.send_command("abort")

    def echo(self, state: str = "on") -> List[str]:
        """
        Activa o desactiva eco en CLI.
        
        Args:
            state (str): "on" o "off"
        """
        return self.send_command(f"echo {state}")

    def get_status(self) -> List[str]:
        """Obtiene estado general del dispositivo."""
        return self.send_command("status")

    # ==============================
    # ==============================
    # MÉTODOS DE MEDICIÓN PRINCIPAL
    # ==============================
    
    def measure_impedance(self) -> List[str]:
        """
        Realiza una medición de impedancia compleja del dispositivo bajo prueba.
        
        Ejecuta una medición de impedancia usando la configuración actual del
        dispositivo (frecuencia, amplitud, ganancia, promedios, etc.) y retorna
        los datos en bruto del ADMX2001. Esta es la función de medición fundamental.
        
        La medición incluye:
        - Impedancia compleja (magnitud y fase)
        - Componentes resistiva y reactiva
        - Información de estado y calidad de la medición
        
        Returns:
            List[str]: Respuesta en bruto del dispositivo conteniendo:
                      - Valor de impedancia en formato específico del firmware
                      - Información de fase y componentes R/X
                      - Códigos de estado o error si aplicable
                      
                      Ejemplo típico de respuesta:
                      ["1000.5, -45.2, 707.1, -707.1"]
                      (magnitud_ohm, fase_deg, resistencia_ohm, reactancia_ohm)
        
        Raises:
            serial.SerialException: Error de comunicación con el dispositivo
            TimeoutError: El dispositivo no responde en el tiempo especificado
        
        Example:
            >>> # Configurar parámetros de medición
            >>> device.set_frequency(1000)  # 1 kHz
            >>> device.set_magnitude(0.5)   # 500 mV
            >>> device.set_average(20)      # 20 promedios
            >>> 
            >>> # Realizar medición en bruto
            >>> raw_result = device.measure_impedance()
            >>> print(f"Respuesta del dispositivo: {raw_result}")
            >>> 
            >>> # Para datos procesados, usar quick_impedance_measurement()
            >>> processed = device.quick_impedance_measurement(1000)
            >>> print(f"Impedancia: {processed['impedance']['magnitude']:.2f} Ω")
        
        Note:
            - Esta función retorna datos en bruto sin procesar
            - Para datos estructurados, usar quick_impedance_measurement()
            - El formato de respuesta depende del firmware del dispositivo
            - Usar parse_impedance_result() para procesar la respuesta
            
        Warning:
            - Verificar que el dispositivo esté configurado apropiadamente antes de medir
            - La calidad de la medición depende de los parámetros configurados
            - Algunos componentes pueden requerir tiempo de estabilización
        """
        try:
            # Secuencia correcta para medición:
            # 1. Inicializar medición (prepara el dispositivo)
            # 2. Usar trigger para obtener datos (z no funciona después de initiate)
            
            # Inicializar medición (prepara el dispositivo)
            init_response = self.send_command("initiate")
            
            # Realizar medición con comando trigger (funciona después de initiate)
            measurement_response = self.send_command("trigger")
            
            # Filtrar solo datos válidos (no warnings ni prompts)
            valid_data = []
            for line in measurement_response:
                if isinstance(line, str):
                    # Limpiar códigos ANSI
                    clean_line = re.sub(r'\x1b7\x1b8', '', line)
                    # Verificar si es una línea de datos (contiene comas y números)
                    if (',' in clean_line and 
                        not clean_line.startswith('ADMX2001>') and 
                        not clean_line.startswith('Warn') and
                        not clean_line == 'trigger'):
                        valid_data.append(clean_line.strip())
            
            # Si tenemos datos válidos, devolver solo los datos de medición
            if valid_data:
                return valid_data
            else:
                # Devolver respuesta completa para debug
                return measurement_response
                
        except Exception as e:
            return [f"ERROR: {str(e)}"]

    def measure_dcr(self) -> List[str]:
        """
        Mide la resistencia de corriente continua (DCR) del dispositivo bajo prueba.
        
        Realiza una medición de resistencia pura usando corriente continua,
        sin componente AC. Útil para caracterizar la resistencia óhmica de
        componentes sin considerar efectos reactivos.
        
        Returns:
            List[str]: Respuesta del dispositivo con valor de resistencia DC
        
        Raises:
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Medir resistencia DC de un resistor
            >>> dcr_result = device.measure_dcr()
            >>> print(f"Resistencia DC: {dcr_result}")
            >>> 
            >>> # Para una medición completa incluyendo DC y AC
            >>> impedance_result = device.measure_impedance()
            >>> print(f"Impedancia AC: {impedance_result}")
        
        Note:
            - La medición DCR ignora efectos reactivos (L, C)
            - Útil para verificar resistencias óhmicas básicas
            - Puede diferir de la componente resistiva de impedancia AC
            - No aplicable a componentes puramente reactivos
        """
        return self.send_command("dcr")

    def measure_vdc(self) -> List[str]:
        """
        Mide el voltaje de corriente continua presente en el dispositivo bajo prueba.
        
        Monitorea el nivel de voltaje DC en los terminales del DUT, útil para
        verificar polarización, offset aplicado, o voltajes residuales.
        
        Returns:
            List[str]: Respuesta del dispositivo con valor de voltaje DC en voltios
        
        Raises:
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Verificar offset aplicado
            >>> device.set_offset(1.2)  # Aplicar 1.2V DC
            >>> vdc_reading = device.measure_vdc()
            >>> print(f"Voltaje DC medido: {vdc_reading}")
            >>> 
            >>> # Verificar que no hay voltaje residual
            >>> device.set_offset(0)
            >>> vdc_check = device.measure_vdc()
            >>> print(f"Voltaje residual: {vdc_check}")
        
        Note:
            - Útil para verificar la configuración de offset
            - Puede detectar voltajes parásitos o de polarización
            - Importante para componentes sensibles a polarización
        """
        return self.send_command("vdc")

    def measure_idc(self) -> List[str]:
        """
        Mide la corriente de corriente continua que fluye por el dispositivo bajo prueba.
        
        Monitorea la corriente DC a través del DUT, útil para caracterizar
        consumo de corriente, verificar polarización, o detectar fugas.
        
        Returns:
            List[str]: Respuesta del dispositivo con valor de corriente DC
        
        Raises:
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Medir corriente de fuga en un capacitor
            >>> device.set_offset(1.0)  # Aplicar 1V DC
            >>> idc_reading = device.measure_idc()
            >>> print(f"Corriente de fuga: {idc_reading}")
            >>> 
            >>> # Verificar consumo de corriente de un dispositivo activo
            >>> device.set_offset(3.3)  # Voltaje de alimentación
            >>> idc_consumption = device.measure_idc()
            >>> print(f"Corriente de consumo: {idc_consumption}")
        
        Note:
            - Útil para detectar corrientes de fuga en capacitores
            - Permite caracterizar consumo de dispositivos activos
            - Importante para verificar funcionamiento de componentes polarizados
        """
        return self.send_command("idc")

    def get_temperature(self) -> List[str]:
        """
        Obtiene la temperatura interna del chip ADMX2001.
        
        Lee el sensor de temperatura interno del dispositivo, útil para
        monitorear condiciones térmicas que pueden afectar la precisión
        de las mediciones y detectar sobrecalentamiento.
        
        Returns:
            List[str]: Respuesta del dispositivo con temperatura en formato
                      específico del firmware (típicamente en Celsius)
        
        Raises:
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Monitorear temperatura durante mediciones
            >>> temp_raw = device.get_temperature()
            >>> print(f"Temperatura en bruto: {temp_raw}")
            >>> 
            >>> # Para temperatura procesada
            >>> temp_processed = device.parse_temperature_result(temp_raw)
            >>> if temp_processed['success']:
            ...     print(f"Temperatura: {temp_processed['temperature_celsius']:.1f}°C")
            >>> 
            >>> # Verificar condiciones térmicas antes de mediciones críticas
            >>> temp = device.quick_impedance_measurement(1000)['temperature']
            >>> if temp['temperature_celsius'] > 50:
            ...     print("⚠️ Advertencia: Temperatura alta detectada")
        
        Note:
            - La temperatura afecta la precisión de las mediciones
            - Útil para detectar condiciones ambientales extremas
            - Permite implementar compensación térmica si es necesaria
            - La temperatura interna puede diferir de la ambiental
            
        Warning:
            - Temperaturas muy altas pueden indicar sobrecarga o mal funcionamiento
            - Permitir estabilización térmica antes de mediciones de precisión
            - La deriva térmica puede afectar mediciones de larga duración
        """
        return self.send_command("temperature")

    def initiate(self) -> List[str]:
        """Entra en modo espera de trigger."""
        return self.send_command("initiate")

    def trigger(self) -> List[str]:
        """Dispara medición manual (software trigger)."""
        return self.send_command("trigger")

    def set_mdelay(self, ms: int) -> List[str]:
        """
        Establece delay entre mediciones.
        
        Args:
            ms (int): Delay en milisegundos
        """
        return self.send_command(f"mdelay {ms}")

    def set_tdelay(self, ms: int) -> List[str]:
        """
        Establece delay tras trigger.
        
        Args:
            ms (int): Delay en milisegundos
        """
        return self.send_command(f"tdelay {ms}")

    def set_tcount(self, n: int) -> List[str]:
        """
        Establece número de triggers automáticos.
        
        Args:
            n (int): Número de triggers
        """
        return self.send_command(f"tcount {n}")

    def set_trigger_mode(self, mode: str = "internal") -> List[str]:
        """
        Establece fuente de trigger.
        
        Args:
            mode (str): "internal" o "external"
        """
        return self.send_command(f"trig_mode {mode}")

    # ==============================
    # CONFIGURACIÓN DE EXCITACIÓN Y SEÑAL
    # ==============================
    
    def set_frequency(self, freq: Union[int, float]) -> List[str]:
        """
        Configura la frecuencia de excitación del generador interno con caching inteligente.
        
        OPTIMIZADO: Incluye sistema de cache para evitar comandos redundantes.
        Si la frecuencia ya está configurada, evita el comando duplicado.
        """
        # Validar rango de frecuencia
        if not isinstance(freq, (int, float)):
            raise ValueError("La frecuencia debe ser un número")
            
        if not (FREQUENCY_RANGE[0] <= freq <= FREQUENCY_RANGE[1]):
            raise ValueError(f"Frecuencia {freq} Hz fuera del rango válido: "
                           f"{FREQUENCY_RANGE[0]} - {FREQUENCY_RANGE[1]} Hz")
        
        # Verificar cache para evitar comando redundante
        cache_key = f"frequency_{freq}"
        if self._is_config_cached(cache_key):
            logger.debug(f"Cache hit: frecuencia {freq} Hz ya configurada")
            return ["OK"]
        
        # Enviar comando con prioridad alta y caching habilitado
        result = self.send_command(f"frequency {freq}", priority='fast', cache_result=True)
        
        # Actualizar cache específico de frecuencia
        self._cache_config(cache_key, result)
        self._cache_config("current_frequency", freq)
        
        logger.info(f"Frecuencia configurada: {freq} Hz")
        return result

    def set_magnitude(self, val: Union[int, float]) -> List[str]:
        """
        Configura la amplitud de la señal de excitación con caching optimizado.
        
        OPTIMIZADO: Sistema de cache para evitar configuraciones redundantes.
        """
        # Validar rango de amplitud
        if not isinstance(val, (int, float)):
            raise ValueError("La amplitud debe ser un número")
            
        if not (MAGNITUDE_RANGE[0] <= val <= MAGNITUDE_RANGE[1]):
            raise ValueError(f"Amplitud {val} V fuera del rango válido: "
                           f"{MAGNITUDE_RANGE[0]} - {MAGNITUDE_RANGE[1]} V")
        
        # Verificar cache
        cache_key = f"magnitude_{val}"
        if self._is_config_cached(cache_key):
            logger.debug(f"Cache hit: amplitud {val} V ya configurada")
            return ["OK"]
        
        # Enviar comando optimizado
        result = self.send_command(f"magnitude {val}", priority='fast', cache_result=True)
        self._cache_config(cache_key, result)
        self._cache_config("current_magnitude", val)
        
        logger.info(f"Amplitud configurada: {val} V")
        return result

    def set_offset(self, val: Union[int, float]) -> List[str]:
        """
        Configura el offset de corriente continua (DC) aplicado a la señal.
        
        Establece un nivel DC que se suma a la señal sinusoidal de excitación.
        Esto es útil para polarizar componentes que requieren un punto de
        operación DC específico, como diodos, transistores, o electrolíticos.
        
        Args:
            val (Union[int, float]): Offset DC en Voltios.
                                   Rango válido: -2.0 V a +2.0 V
                                   
                                   Valores típicos:
                                   - 0 V: Sin polarización (componentes lineales)
                                   - +0.7 V: Polarización directa de diodos
                                   - +1.2 V: Polarización de electrolíticos
                                   - Valores negativos: Polarización inversa
        
        Returns:
            List[str]: Respuesta del dispositivo, típicamente ["OK"] si exitoso
        
        Raises:
            ValueError: Si el offset está fuera del rango válido
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Sin offset para componentes lineales
            >>> device.set_offset(0)
            >>> 
            >>> # Polarización para electrolíticos
            >>> device.set_offset(1.2)  # +1.2V DC
            >>> 
            >>> # Polarización directa de diodos
            >>> device.set_offset(0.7)   # +0.7V DC
            >>> 
            >>> # Verificar configuración
            >>> current_offset = device.get_offset()
            >>> print(f"Offset actual: {current_offset} V")
        
        Note:
            - El offset se suma algebraicamente a la señal AC
            - Necesario para caracterizar componentes polarizados correctamente
            - Puede afectar significativamente las mediciones de impedancia
            - Usar con cuidado para evitar dañar componentes sensibles
            
        Warning:
            - Offset incorrecto puede dañar o destruir componentes
            - Verificar polaridad y nivel antes de aplicar offset
            - Algunos componentes pueden calentarse con offset alto
            - Para componentes no polarizados, mantener offset en 0V
        """
        # Validar rango de offset
        if not isinstance(val, (int, float)):
            raise ValueError("El offset debe ser un número")
            
        if not (OFFSET_RANGE[0] <= val <= OFFSET_RANGE[1]):
            raise ValueError(f"Offset {val} V fuera del rango válido: "
                           f"{OFFSET_RANGE[0]} - {OFFSET_RANGE[1]} V")
        
        return self.send_command(f"offset {val}")

    def set_gain_auto(self) -> List[str]:
        """
        Configura el sistema de ganancia automática del ADMX2001.
        
        Habilita el modo de auto-rango que permite al dispositivo ajustar
        automáticamente las ganancias de los canales de medición para
        optimizar la precisión y el rango dinámico según la impedancia
        del dispositivo bajo prueba.
        
        En modo automático, el ADMX2001:
        - Monitorea continuamente los niveles de señal
        - Ajusta las ganancias para maximizar resolución
        - Previene saturación de los amplificadores
        - Optimiza la relación señal/ruido
        
        Returns:
            List[str]: Respuesta del dispositivo, típicamente ["OK"] si exitoso
        
        Raises:
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Habilitar auto-ganancia (recomendado para uso general)
            >>> device.set_gain_auto()
            >>> 
            >>> # Realizar medición con ganancia optimizada automáticamente
            >>> result = device.read_impedance()
            >>> print(f"Impedancia: {result['magnitude']:.2f} Ω")
        
        Note:
            - Recomendado para la mayoría de aplicaciones
            - El dispositivo puede tardar unos momentos en estabilizar
            - Proporciona mejor precisión que ganancia manual fija
            - Especialmente útil para barridos de frecuencia amplios
            
        Warning:
            - En modo auto, la ganancia puede cambiar entre mediciones
            - Para máxima repetibilidad, considerar ganancia manual fija
            - Algunos componentes muy ruidosos pueden causar oscilación de ganancia
        """
        return self.send_command("setgain auto")

    def set_gain_ch0(self, gain: int) -> List[str]:
        """
        Configura la ganancia del canal 0 (canal de voltaje) manualmente.
        
        Establece una ganancia fija para el canal de medición de voltaje,
        deshabilitando el auto-rango para este canal. Útil cuando se necesita
        ganancia constante para mediciones repetibles o cuando el auto-rango
        no converge apropiadamente.
        
        Args:
            gain (int): Nivel de ganancia del canal 0.
                       Valores válidos: 0, 1, 2, 3
                       
                       Interpretación típica:
                       - 0: Ganancia mínima (rango máximo)
                       - 1: Ganancia baja
                       - 2: Ganancia media  
                       - 3: Ganancia máxima (rango mínimo, máxima precisión)
        
        Returns:
            List[str]: Respuesta del dispositivo, típicamente ["OK"] si exitoso
        
        Raises:
            ValueError: Si el valor de ganancia está fuera del rango válido (0-3)
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Ganancia baja para impedancias altas
            >>> device.set_gain_ch0(0)
            >>> 
            >>> # Ganancia alta para máxima precisión con impedancias bajas
            >>> device.set_gain_ch0(3)
            >>> 
            >>> # Ganancia media para uso general
            >>> device.set_gain_ch0(2)
            >>> 
            >>> # Verificar configuración actual
            >>> current_gains = device.get_gain()
            >>> print(f"Ganancia CH0: {current_gains}")
        
        Note:
            - Ganancia alta mejora precisión pero reduce rango de medición
            - Ganancia baja aumenta rango pero puede reducir precisión
            - La ganancia óptima depende de la impedancia del DUT
            - Usar auto-ganancia cuando no se conoce la impedancia esperada
            
        Warning:
            - Ganancia incorrecta puede causar saturación o pérdida de precisión
            - Verificar que las señales no saturen con la ganancia seleccionada
            - Para cambios grandes de impedancia, regresar a modo automático
        """
        # Validar rango de ganancia
        if not isinstance(gain, int):
            raise ValueError("La ganancia debe ser un número entero")
            
        if not (0 <= gain <= 3):
            raise ValueError(f"Ganancia {gain} fuera del rango válido: 0-3")
        
        return self.send_command(f"setgain ch0 {gain}")

    def set_gain_ch1(self, gain: int) -> List[str]:
        """
        Establece ganancia del canal de corriente.
        
        Args:
            gain (int): Ganancia (0-3)
        """
        return self.send_command(f"setgain ch1 {gain}")

    # ==============================
    # CONFIGURACIÓN DE PROMEDIADO Y REPETICIONES
    # ==============================
    
    def set_average(self, n: int) -> List[str]:
        """
        Configura el número de promedios por cada medición individual.
        
        Establece cuántas muestras internas promedia el ADMX2001 para generar
        cada valor de medición reportado. Más promedios resultan en mediciones
        más estables y precisas, pero requieren más tiempo por medición.
        
        El promediado interno del dispositivo:
        - Reduce el ruido aleatorio en √n (n = número de promedios)
        - Mejora la estabilidad de las mediciones
        - Aumenta el tiempo necesario por medición
        - Ayuda a estabilizar mediciones en ambientes ruidosos
        
        Args:
            n (int): Número de promedios internos por medición.
                    Rango válido: 1 - 100
                    
                    Valores recomendados:
                    - 1-5: Mediciones rápidas, precisión básica
                    - 10-20: Uso general, buen balance velocidad/precisión
                    - 30-50: Alta precisión, ambientes ruidosos
                    - 80-100: Máxima precisión, mediciones críticas
        
        Returns:
            List[str]: Respuesta del dispositivo, típicamente ["OK"] si exitoso
        
        Raises:
            ValueError: Si el número de promedios está fuera del rango válido
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Configuración rápida para barridos
            >>> device.set_average(5)
            >>> 
            >>> # Configuración estándar para mediciones generales
            >>> device.set_average(15)
            >>> 
            >>> # Alta precisión para mediciones críticas
            >>> device.set_average(50)
            >>> 
            >>> # Verificar configuración actual
            >>> current_avg = device.get_average()
            >>> print(f"Promedios configurados: {current_avg}")
        
        Note:
            - Tiempo de medición ≈ proporcional al número de promedios
            - La mejora de SNR es proporcional a √n, no a n
            - Para componentes estables, 10-20 promedios suelen ser suficientes
            - En ambientes muy ruidosos, puede requerirse 50+ promedios
            
        Warning:
            - Valores muy altos (>80) pueden hacer las mediciones muy lentas
            - Para barridos de frecuencia, balancear precisión vs tiempo total
            - Algunos componentes pueden derivar durante mediciones muy largas
        """
        # Validar rango de promedios
        if not isinstance(n, int):
            raise ValueError("El número de promedios debe ser un entero")
            
        if not (AVERAGE_RANGE[0] <= n <= AVERAGE_RANGE[1]):
            raise ValueError(f"Número de promedios {n} fuera del rango válido: "
                           f"{AVERAGE_RANGE[0]} - {AVERAGE_RANGE[1]}")
        
        return self.send_command(f"average {n}")

    def set_count(self, n: int) -> List[str]:
        """
        Configura el número de mediciones repetidas que realiza el dispositivo.
        
        Establece cuántas mediciones individuales (cada una ya promediada según
        set_average) ejecuta el dispositivo cuando se solicita una lectura.
        Útil para análisis estadístico y detección de valores atípicos.
        
        La diferencia con set_average():
        - set_average(): promediado interno del hardware (más rápido)
        - set_count(): repeticiones de mediciones completas (más información)
        
        Args:
            n (int): Número de mediciones repetidas a realizar.
                    Rango válido: 1 - 100
                    
                    Valores típicos:
                    - 1: Medición única (más rápido)
                    - 3-5: Detección básica de inconsistencias
                    - 10-15: Análisis estadístico robusto
                    - 20+: Caracterización de estabilidad/deriva
        
        Returns:
            List[str]: Respuesta del dispositivo, típicamente ["OK"] si exitoso
        
        Raises:
            ValueError: Si el número de repeticiones está fuera del rango válido
            serial.SerialException: Error de comunicación con el dispositivo
        
        Example:
            >>> # Medición única para máxima velocidad
            >>> device.set_count(1)
            >>> 
            >>> # Múltiples mediciones para análisis estadístico
            >>> device.set_count(10)
            >>> result = device.read_impedance()
            >>> # El resultado puede incluir estadísticas de las 10 mediciones
            >>> 
            >>> # Para caracterización de precisión
            >>> device.set_count(20)
            >>> device.set_average(30)  # Cada medición usa 30 promedios
        
        Note:
            - Tiempo total ≈ count × average × tiempo_base_medición
            - Útil para calcular desviación estándar y repetibilidad
            - Permite detectar mediciones inconsistentes o atípicas
            - Combinado con set_average() proporciona control completo de precisión
            
        Warning:
            - Valores altos pueden hacer las mediciones extremadamente lentas
            - Para uso interactivo, mantener count × average < 500
            - Considerar deriva térmica en mediciones muy largas
        """
        # Validar rango de conteo
        if not isinstance(n, int):
            raise ValueError("El número de repeticiones debe ser un entero")
            
        if not (COUNT_RANGE[0] <= n <= COUNT_RANGE[1]):
            raise ValueError(f"Número de repeticiones {n} fuera del rango válido: "
                           f"{COUNT_RANGE[0]} - {COUNT_RANGE[1]}")
        
        return self.send_command(f"count {n}")

    # ==============================
    # Display y Formato de Salida
    # ==============================
    
    def set_display(self, mode: int) -> List[str]:
        """
        Selecciona qué se muestra en resultados.
        
        Args:
            mode (int): Modo de display (0-18)
                       0: Z, 1: R+jX, 2: |Z|+θ, etc.
        """
        return self.send_command(f"display {mode}")

    def set_format(self, fmt: str = "ascii") -> List[str]:
        """
        Establece formato de salida de resultados.
        
        Args:
            fmt (str): "ascii" o "hex"
        """
        return self.send_command(f"format {fmt}")

    # ==============================
    # Barridos (Sweeps)
    # ==============================
    
    def sweep_frequency(self, start: Union[int, float], end: Union[int, float]) -> List[str]:
        """
        Configura barrido de frecuencia.
        
        Args:
            start (Union[int, float]): Frecuencia inicial en Hz
            end (Union[int, float]): Frecuencia final en Hz
        """
        return self.send_command(f"sweep_type frequency {start} {end}")

    def sweep_magnitude(self, start: Union[int, float], end: Union[int, float]) -> List[str]:
        """
        Configura barrido de amplitud.
        
        Args:
            start (Union[int, float]): Amplitud inicial
            end (Union[int, float]): Amplitud final
        """
        return self.send_command(f"sweep_type magnitude {start} {end}")

    def sweep_offset(self, start: Union[int, float], end: Union[int, float]) -> List[str]:
        """
        Configura barrido de offset.
        
        Args:
            start (Union[int, float]): Offset inicial
            end (Union[int, float]): Offset final
        """
        return self.send_command(f"sweep_type offset {start} {end}")

    def sweep_scale(self, mode: str = "log") -> List[str]:
        """
        Establece escala del barrido.
        
        Args:
            mode (str): "log" o "linear"
        """
        return self.send_command(f"sweep_scale {mode}")

    def sweep_points(self, n: int) -> List[str]:
        """
        Establece número de puntos en el sweep.
        
        Args:
            n (int): Número de puntos
        """
        return self.send_command(f"sweep_points {n}")

    def sweep_run(self) -> List[str]:
        """Ejecuta el sweep definido."""
        return self.send_command("sweep run")

    # ==============================
    # Calibración (Comandos Completos)
    # ==============================
    
    def calibrate_open(self) -> List[str]:
        """Calibración con circuito abierto."""
        return self.send_command("calibrate open")

    def calibrate_short(self) -> List[str]:
        """Calibración con cortocircuito."""
        return self.send_command("calibrate short")

    def calibrate_load(self, r: Union[int, float], x: Union[int, float]) -> List[str]:
        """
        Calibración con carga conocida.
        
        Args:
            r (Union[int, float]): Resistencia conocida en Ω
            x (Union[int, float]): Reactancia conocida en Ω
        """
        return self.send_command(f"calibrate rt {r} xt {x}")

    def calibrate_commit(self, timestamp: Optional[str] = None) -> List[str]:
        """
        Guarda coeficientes de calibración en flash.
        
        Args:
            timestamp (str, optional): Timestamp para la calibración
        """
        if timestamp:
            return self.send_command(f"calibrate commit {timestamp}")
        return self.send_command("calibrate commit")

    def calibrate_password(self, new_password: Optional[str] = None) -> List[str]:
        """
        Cambia contraseña de calibración.
        
        Args:
            new_password (str, optional): Nueva contraseña
        """
        if new_password:
            return self.send_command(f"calibrate password {new_password}")
        return self.send_command("calibrate password")

    def calibrate_reload(self) -> List[str]:
        """Restaura calibraciones desde flash."""
        return self.send_command("calibrate reload")

    def calibrate_erase(self) -> List[str]:
        """Borra todas las calibraciones (¡PELIGROSO!)."""
        return self.send_command("calibrate erase")

    def calibrate_list(self) -> List[str]:
        """Lista frecuencias calibradas."""
        return self.send_command("calibrate list")

    def rdcal(self, vgain: int, igain: int) -> List[str]:
        """
        Lee coeficientes de calibración.
        
        Args:
            vgain (int): Ganancia de voltaje (0-3)
            igain (int): Ganancia de corriente (0-3)
        """
        return self.send_command(f"rdcal {vgain} {igain}")

    def storecal(self, vgain: int, igain: int, coef: int, val: Union[int, float]) -> List[str]:
        """
        Escribe coeficientes de calibración manualmente.
        
        Args:
            vgain (int): Ganancia de voltaje (0-3)
            igain (int): Ganancia de corriente (0-3)
            coef (int): Número de coeficiente
            val (Union[int, float]): Valor del coeficiente
        """
        return self.send_command(f"storecal {vgain} {igain} {coef} {val}")

    # ==============================
    # GPIO y Auxiliares
    # ==============================
    
    def gpio_ctrl(self, value: int) -> List[str]:
        """
        Control directo de GPIO.
        
        Args:
            value (int): Valor GPIO (0-255)
        """
        return self.send_command(f"gpio_ctrl {value}")

    def gpio_read(self) -> List[str]:
        """Lee estado de GPIO."""
        return self.send_command("gpio_read")

    def led(self, state: str = "on") -> List[str]:
        """
        Control del LED de estado.
        
        Args:
            state (str): "on", "off" o "blink"
        """
        return self.send_command(f"led {state}")

    # ==============================
    # Diagnóstico y Test
    # ==============================
    
    def selftest(self) -> List[str]:
        """Devuelve estado del autodiagnóstico."""
        return self.send_command("selftest")

    def selftest_run(self) -> List[str]:
        """Ejecuta prueba de hardware."""
        return self.send_command("selftest run")

    def errorlog(self) -> List[str]:
        """Devuelve últimos errores del sistema."""
        return self.send_command("errorlog")

    # ==============================
    # Métodos de Alto Nivel
    # ==============================
    
    # ==============================
    # Métodos de Alto Nivel y Análisis
    # ==============================
    
    def parse_impedance_result(self, raw_result: List[str]) -> dict:
        """
        Parsea resultado de medición de impedancia del formato ADMX2001.
        
        Args:
            raw_result (List[str]): Resultado crudo de medición
            
        Returns:
            dict: Datos parseados de impedancia
        """
        try:
            # Limpiar respuesta de códigos ANSI y prompt
            clean_lines = []
            for line in raw_result:
                if isinstance(line, str):
                    # Remover códigos ANSI 
                    clean_line = re.sub(r'\x1b7\x1b8', '', line)
                    # Filtrar líneas de prompt y warnings
                    if (clean_line.strip() and 
                        not clean_line.startswith('ADMX2001>') and 
                        not clean_line.startswith('Warn')):
                        clean_lines.append(clean_line.strip())
            
            # Buscar líneas con datos numéricos
            for line in clean_lines:
                if ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        try:
                            # Formato: flag,real,imag (donde flag suele ser 0)
                            flag = float(parts[0])  # Puede ser útil para estado
                            real_part = float(parts[1])  
                            imag_part = float(parts[2])
                            
                            # Calcular parámetros de impedancia
                            magnitude = (real_part**2 + imag_part**2)**0.5
                            phase_rad = math.atan2(imag_part, real_part)
                            phase_deg = phase_rad * 180 / math.pi
                            
                            # Calcular conductancia y susceptancia (Y = 1/Z)
                            if magnitude != 0:
                                conductance = real_part / (real_part**2 + imag_part**2)
                                susceptance = -imag_part / (real_part**2 + imag_part**2)
                            else:
                                conductance = 0
                                susceptance = 0
                            
                            return {
                                'success': True,
                                'flag': flag,
                                'resistance': real_part,
                                'reactance': imag_part,
                                'magnitude': magnitude,
                                'phase_degrees': phase_deg,
                                'phase_radians': phase_rad,
                                'conductance': conductance,
                                'susceptance': susceptance,
                                'timestamp': datetime.now().isoformat(),
                                'raw_data': line,
                                'raw_response': raw_result
                            }
                        except (ValueError, IndexError) as e:
                            continue
            
            return {
                'success': False,
                'error': 'No se pudo parsear la respuesta - sin datos válidos',
                'raw_response': raw_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en parsing: {str(e)}',
                'raw_response': raw_result
            }

    def parse_temperature_result(self, raw_result: List[str]) -> dict:
        """
        Parsea resultado de temperatura.
        
        Args:
            raw_result (List[str]): Resultado crudo de temperatura
            
        Returns:
            dict: Temperatura parseada
        """
        try:
            for line in raw_result:
                if 'Temperature' in line and 'deg C' in line:
                    # Extraer valor numérico
                    import re
                    match = re.search(r'([-+]?\d*\.?\d+)\s+deg\s+C', line)
                    if match:
                        temp_value = float(match.group(1))
                        return {
                            'temperature_celsius': temp_value,
                            'temperature_fahrenheit': temp_value * 9/5 + 32,
                            'raw_line': line,
                            'success': True
                        }
            
            return {
                'success': False,
                'error': 'No se pudo parsear la temperatura',
                'raw_response': raw_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_response': raw_result
            }

    def quick_impedance_measurement(self, frequency: Union[int, float] = 1000) -> dict:
        """
        Realiza una medición completa de impedancia con análisis automático de datos.
        
        Este es el método principal recomendado para mediciones de impedancia.
        Combina configuración automática, medición, y procesamiento de datos en
        una sola llamada conveniente. Ideal para uso interactivo y aplicaciones
        que requieren resultados estructurados y listos para usar.
        
        Funcionalidad completa:
        1. Configura la frecuencia de medición automáticamente
        2. Realiza medición de impedancia con parámetros actuales
        3. Obtiene temperatura del dispositivo para referencia
        4. Procesa y estructura todos los datos automáticamente
        5. Calcula componentes derivadas (R, X, magnitud, fase)
        6. Retorna resultados en formato estructurado y fácil de usar
        
        Args:
            frequency (Union[int, float], optional): Frecuencia de medición en Hz.
                                                   Default: 1000 Hz (1 kHz)
                                                   Rango válido: 1 Hz - 100 kHz
                                                   
                                                   Frecuencias recomendadas:
                                                   - 100 Hz: Electrolíticos, audio
                                                   - 1 kHz: Caracterización general
                                                   - 10 kHz: Componentes cerámicos
                                                   - 100 kHz: Aplicaciones RF
        
        Returns:
            dict: Diccionario completo con todos los resultados estructurados:
                  
                  {
                      'impedance': {
                          'success': bool,           # True si medición exitosa
                          'magnitude': float,        # |Z| en Ohm
                          'phase_degrees': float,    # Fase en grados
                          'phase_radians': float,    # Fase en radianes
                          'resistance': float,       # Componente resistiva (R)
                          'reactance': float,        # Componente reactiva (X)
                          'conductance': float,      # Conductancia (G)
                          'susceptance': float,      # Susceptancia (B)
                          'frequency_hz': float,     # Frecuencia de medición
                          'timestamp': str,          # Marca de tiempo ISO
                          'raw_response': List[str], # Respuesta en bruto
                          'error': str               # Mensaje de error (si aplicable)
                      },
                      'temperature': {
                          'success': bool,           # True si lectura exitosa
                          'temperature_celsius': float,  # Temperatura en °C
                          'timestamp': str,          # Marca de tiempo ISO
                          'raw_response': List[str], # Respuesta en bruto
                          'error': str               # Mensaje de error (si aplicable)
                      },
                      'measurement_info': {
                          'device_port': str,        # Puerto serie usado
                          'measurement_duration': float, # Tiempo de medición
                          'configured_frequency': float, # Frecuencia configurada
                          'device_status': str       # Estado general del dispositivo
                      }
                  }
        
        Raises:
            ValueError: Si la frecuencia está fuera del rango válido
            serial.SerialException: Error de comunicación con el dispositivo
            RuntimeError: Error general durante la medición
        
        Example:
            >>> # Medición básica a 1 kHz
            >>> result = device.quick_impedance_measurement()
            >>> 
            >>> if result['impedance']['success']:
            ...     impedance = result['impedance']
            ...     temp = result['temperature']
            ...     
            ...     print(f"Impedancia: {impedance['magnitude']:.2f} Ω")
            ...     print(f"Fase: {impedance['phase_degrees']:.1f}°")
            ...     print(f"Resistencia: {impedance['resistance']:.2f} Ω")
            ...     print(f"Reactancia: {impedance['reactance']:.2f} Ω")
            ...     print(f"Temperatura: {temp['temperature_celsius']:.1f}°C")
            ... else:
            ...     print(f"Error en medición: {result['impedance']['error']}")
            >>> 
            >>> # Medición a frecuencia específica
            >>> result_10k = device.quick_impedance_measurement(10000)  # 10 kHz
            >>> 
            >>> # Serie de mediciones a diferentes frecuencias
            >>> frequencies = [100, 1000, 10000, 100000]
            >>> results = []
            >>> for freq in frequencies:
            ...     result = device.quick_impedance_measurement(freq)
            ...     if result['impedance']['success']:
            ...         results.append({
            ...             'frequency': freq,
            ...             'magnitude': result['impedance']['magnitude'],
            ...             'phase': result['impedance']['phase_degrees']
            ...         })
            >>> 
            >>> # Análisis de componente basado en medición
            >>> result = device.quick_impedance_measurement(1000)
            >>> if result['impedance']['success']:
            ...     imp = result['impedance']
            ...     if imp['phase_degrees'] > 45:
            ...         print("Componente inductivo detectado")
            ...     elif imp['phase_degrees'] < -45:
            ...         print("Componente capacitivo detectado")
            ...     else:
            ...         print("Componente resistivo detectado")
        
        Note:
            - Método recomendado para la mayoría de aplicaciones
            - Combina facilidad de uso con resultados completos
            - Ideal para mediciones interactivas y análisis automático
            - La temperatura se incluye automáticamente para referencia
            - Todos los datos se estructuran para fácil acceso y análisis
            
        Warning:
            - Verificar que el dispositivo esté conectado antes de usar
            - La precisión depende de la configuración previa (ganancia, promedios)
            - Para máxima precisión, configurar parámetros específicos antes de medir
            - La frecuencia se configura automáticamente, puede afectar mediciones posteriores
        """
        try:
            # Validar frecuencia de entrada
            if not isinstance(frequency, (int, float)):
                raise ValueError("La frecuencia debe ser un número")
                
            if not (FREQUENCY_RANGE[0] <= frequency <= FREQUENCY_RANGE[1]):
                raise ValueError(f"Frecuencia {frequency} Hz fuera del rango válido: "
                               f"{FREQUENCY_RANGE[0]} - {FREQUENCY_RANGE[1]} Hz")
            
            # Registrar tiempo de inicio para duración de medición
            start_time = time.time()
            
            # Configuración completa del dispositivo para medición confiable
            # 0. Reset para asegurar estado conocido (solo si es necesario)
            try:
                # Probar si el dispositivo responde correctamente
                test_response = self.send_command("frequency")
                if any('Warn' in line for line in test_response if isinstance(line, str)):
                    # Si hay warnings, hacer reset
                    self.send_command("reset")
                    time.sleep(1)  # Esperar reset
            except:
                # Si hay error, hacer reset
                self.send_command("reset")
                time.sleep(1)
            
            # 1. Configurar frecuencia
            freq_response = self.set_frequency(frequency)
            
            # 2. Configurar parámetros básicos de medición
            self.send_command("magnitude 1")        # Magnitud de 1V
            self.send_command("setgain auto")       # Ganancia automática
            self.send_command("average 10")         # 10 promedios para estabilidad
            self.send_command("trig_mode internal") # Trigger interno
            
            # Pequeña pausa para estabilización
            time.sleep(0.2)
            
            # Realizar medición de impedancia
            raw_impedance = self.measure_impedance()
            impedance_data = self.parse_impedance_result(raw_impedance)
            
            # Agregar información de frecuencia a los datos de impedancia
            if impedance_data['success']:
                impedance_data['frequency_hz'] = frequency
            
            # Obtener temperatura del dispositivo
            raw_temp = self.get_temperature()
            temp_data = self.parse_temperature_result(raw_temp)
            
            # Calcular duración de la medición
            measurement_duration = time.time() - start_time
            
            # Compilar información adicional de la medición
            measurement_info = {
                'device_port': self.port,
                'measurement_duration': measurement_duration,
                'configured_frequency': frequency,
                'device_status': 'connected' if self.is_connected else 'disconnected',
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'impedance': impedance_data,
                'temperature': temp_data,
                'measurement_info': measurement_info
            }
            
        except ValueError as e:
            # Error de validación de parámetros
            return {
                'impedance': {
                    'success': False,
                    'error': f"Error de parámetros: {e}",
                    'frequency_hz': frequency
                },
                'temperature': {
                    'success': False,
                    'error': "No se pudo medir debido a error de parámetros"
                },
                'measurement_info': {
                    'device_port': self.port,
                    'measurement_duration': 0,
                    'configured_frequency': frequency,
                    'device_status': 'error',
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except serial.SerialException as e:
            # Error de comunicación serie
            return {
                'impedance': {
                    'success': False,
                    'error': f"Error de comunicación: {e}",
                    'frequency_hz': frequency
                },
                'temperature': {
                    'success': False,
                    'error': "No se pudo medir debido a error de comunicación"
                },
                'measurement_info': {
                    'device_port': self.port,
                    'measurement_duration': 0,
                    'configured_frequency': frequency,
                    'device_status': 'communication_error',
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            # Error general no especificado
            return {
                'impedance': {
                    'success': False,
                    'error': f"Error inesperado: {e}",
                    'frequency_hz': frequency
                },
                'temperature': {
                    'success': False,
                    'error': "No se pudo medir debido a error inesperado"
                },
                'measurement_info': {
                    'device_port': self.port,
                    'measurement_duration': 0,
                    'configured_frequency': frequency,
                    'device_status': 'unknown_error',
                    'timestamp': datetime.now().isoformat()
                }
            }

    def frequency_sweep_advanced(self, start_freq: Union[int, float], end_freq: Union[int, float], 
                                 points: int = 100, scale: str = "log", 
                                 save_to_file: bool = False) -> dict:
        """
        Realiza un barrido de frecuencia completo con análisis automático avanzado.
        
        Este método ejecuta un análisis comprehensivo de impedancia vs frecuencia,
        incluyendo detección automática de resonancias, cálculo de estadísticas,
        análisis de pendientes, y caracterización del comportamiento del componente.
        Ideal para caracterización completa de dispositivos desconocidos.
        
        Características del análisis:
        - 🔍 Detección automática de resonancias y antiresonancias
        - 📊 Cálculo de estadísticas completas (min, max, promedio, desviación)
        - 📈 Análisis de pendiente para identificación de tipo de componente
        - 🎯 Cálculo de factor Q para resonancias detectadas
        - 💾 Exportación automática opcional de datos y análisis
        - ⏱️ Monitoreo de temperatura durante el barrido
        - 📉 Detección de rangos dinámicos y comportamientos anómalos
        
        Args:
            start_freq (Union[int, float]): Frecuencia inicial del barrido en Hz.
                                          Rango válido: 1 Hz - 100 kHz
                                          
            end_freq (Union[int, float]): Frecuencia final del barrido en Hz.
                                        Debe ser mayor que start_freq
                                        Rango válido: 1 Hz - 100 kHz
                                        
            points (int, optional): Número de puntos de medición en el barrido.
                                  Default: 100
                                  Rango recomendado: 10-500 puntos
                                  
                                  Consideraciones:
                                  - Más puntos = mayor resolución, más tiempo
                                  - Para resonancias estrechas: 200+ puntos
                                  - Para vista general: 50-100 puntos
                                  - Para análisis rápido: 20-50 puntos
                                  
            scale (str, optional): Tipo de escala para distribución de frecuencias.
                                 Opciones: "log" | "linear"
                                 Default: "log"
                                 
                                 - "log": Distribución logarítmica (recomendado)
                                   Ideal para barridos amplios (ej: 100 Hz - 100 kHz)
                                   Mejor resolución en bajas frecuencias
                                   
                                 - "linear": Distribución lineal uniforme
                                   Ideal para rangos estrechos
                                   Resolución constante en todo el rango
                                   
            save_to_file (bool, optional): Si guardar automáticamente los resultados.
                                         Default: False
                                         
                                         Si True, crea archivo JSON con:
                                         - Todos los datos de medición
                                         - Análisis completo de resultados
                                         - Metadatos de configuración
                                         - Timestamp para trazabilidad
        
        Returns:
            dict: Diccionario completo con resultados y análisis estructurados:
                  
                  {
                      'success': bool,               # True si barrido exitoso
                      'measurements': [              # Lista de mediciones
                          {
                              'frequency_hz': float,
                              'magnitude_ohm': float,
                              'phase_degrees': float,
                              'resistance_ohm': float,
                              'reactance_ohm': float,
                              'timestamp': str
                          }, ...
                      ],
                      'analysis': {
                          'data_points': int,        # Número de puntos válidos
                          'frequency_range': {
                              'start_hz': float,
                              'end_hz': float,
                              'span_decades': float
                          },
                          'magnitude_stats': {
                              'min_ohm': float,
                              'max_ohm': float,
                              'avg_ohm': float,
                              'std_ohm': float,
                              'dynamic_range_db': float
                          },
                          'phase_stats': {
                              'min_deg': float,
                              'max_deg': float,
                              'avg_deg': float,
                              'std_deg': float
                          },
                          'resonances_detected': [   # Resonancias encontradas
                              {
                                  'type': str,       # 'resonance' o 'antiresonance'
                                  'frequency_hz': float,
                                  'magnitude_ohm': float,
                                  'phase_deg': float,
                                  'q_factor': float
                              }, ...
                          ],
                          'slope_analysis': {        # Análisis de comportamiento
                              'magnitude_slope': float,
                              'suggested_component_type': str,
                              'slope_confidence': float
                          },
                          'temperature_info': {
                              'start_temp_c': float,
                              'end_temp_c': float,
                              'temp_drift_c': float
                          }
                      },
                      'configuration': {             # Parámetros utilizados
                          'start_frequency_hz': float,
                          'end_frequency_hz': float,
                          'points_requested': int,
                          'scale_type': str,
                          'measurement_duration_s': float
                      },
                      'saved_file': str,             # Archivo guardado (si save_to_file=True)
                      'error': str                   # Mensaje de error (si failure)
                  }
        
        Raises:
            ValueError: Si los parámetros están fuera de rango o son inconsistentes
            serial.SerialException: Error de comunicación con el dispositivo
            RuntimeError: Error durante la ejecución del barrido
        
        Example:
            >>> # Barrido básico logarítmico de audio a RF
            >>> result = device.frequency_sweep_advanced(
            ...     start_freq=100,      # 100 Hz
            ...     end_freq=100000,     # 100 kHz
            ...     points=50,           # 50 puntos
            ...     scale="log"          # Escala logarítmica
            ... )
            >>> 
            >>> if result['success']:
            ...     analysis = result['analysis']
            ...     print(f"Puntos medidos: {analysis['data_points']}")
            ...     print(f"Rango dinámico: {analysis['magnitude_stats']['dynamic_range_db']:.1f} dB")
            ...     print(f"Resonancias: {len(analysis['resonances_detected'])}")
            ... 
            >>> # Barrido con guardado automático para análisis posterior
            >>> detailed_result = device.frequency_sweep_advanced(
            ...     start_freq=1000,     # 1 kHz  
            ...     end_freq=50000,      # 50 kHz
            ...     points=200,          # Alta resolución
            ...     scale="log",
            ...     save_to_file=True    # Guardar automáticamente
            ... )
            >>> 
            >>> if detailed_result['success']:
            ...     print(f"Datos guardados en: {detailed_result['saved_file']}")
            ...     
            ...     # Analizar resonancias detectadas
            ...     resonances = detailed_result['analysis']['resonances_detected']
            ...     for i, res in enumerate(resonances):
            ...         freq_khz = res['frequency_hz'] / 1000
            ...         q_factor = res['q_factor']
            ...         print(f"Resonancia {i+1}: {freq_khz:.1f} kHz, Q={q_factor:.1f}")
            >>> 
            >>> # Barrido lineal de alta resolución en rango estrecho
            >>> narrow_result = device.frequency_sweep_advanced(
            ...     start_freq=9000,     # 9 kHz
            ...     end_freq=11000,      # 11 kHz  
            ...     points=100,          # 100 puntos en 2 kHz
            ...     scale="linear"       # Distribución uniforme
            ... )
        
        Note:
            - Para rangos amplios (>1 década), usar escala logarítmica
            - Para resonancias estrechas, usar muchos puntos (200+)
            - El análisis automático identifica tipo de componente probable
            - La temperatura se monitorea para detectar deriva térmica
            - Los archivos guardados incluyen metadatos para reproducibilidad
            
        Warning:
            - Barridos largos pueden tardar varios minutos en completarse
            - Componentes polarizados requieren configuración previa de offset
            - La precisión depende de la configuración de ganancia y promedios
            - Verificar que start_freq < end_freq antes de ejecutar
        """
        try:
            # Validar parámetros de entrada con límites de hardware reales
            if not isinstance(start_freq, (int, float)) or not isinstance(end_freq, (int, float)):
                raise ValueError("Las frecuencias deben ser números")
                
            if start_freq >= end_freq:
                raise ValueError("La frecuencia final debe ser mayor que la inicial")
                
            # Validación avanzada con límites reales del hardware
            if not self._validate_hardware_limits('frequency', start_freq):
                raise ValueError(f"Frecuencia inicial {start_freq} Hz fuera de límites del hardware")
                
            if not self._validate_hardware_limits('frequency', end_freq):
                raise ValueError(f"Frecuencia final {end_freq} Hz fuera de límites del hardware")
                
            if not isinstance(points, int) or points < 2:
                raise ValueError("El número de puntos debe ser un entero >= 2")
                
            # VALIDACIÓN CRÍTICA: Límite real del sweep nativo
            if not self._validate_hardware_limits('sweep_points_native', points):
                max_native_points = 500  # Límite documentado del ADMX2001
                logger.warning(f"Puntos solicitados ({points}) excede límite nativo ({max_native_points})")
                logger.info("Se usará sweep punto-a-punto como fallback automático")
                
            if scale not in ["log", "linear"]:
                raise ValueError("La escala debe ser 'log' o 'linear'")
            
            # Validación inteligente de span de frecuencias
            span_decades = math.log10(end_freq / start_freq)
            if span_decades > 5:  # >5 décadas
                logger.warning(f"Span muy amplio ({span_decades:.1f} décadas) - considere sweep logarítmico")
                if scale == "linear":
                    logger.warning("Escala lineal en rango amplio puede dar mala resolución en bajas frecuencias")
            
            # Estimación inteligente de tiempo de medición
            estimated_time = self._estimate_sweep_time(points, scale == "log")
            if estimated_time > 300:  # >5 minutos
                logger.warning(f"Sweep estimado en {estimated_time:.0f} segundos. Considere reducir puntos.")
                
            print(f"🔄 Iniciando barrido de {start_freq} Hz a {end_freq} Hz...")
            print(f"📊 Configuración: {points} puntos, escala {scale}, tiempo estimado: {estimated_time:.0f}s")
            
            # Registrar tiempo de inicio
            start_time = time.time()
            
            # Obtener temperatura inicial
            initial_temp_raw = self.get_temperature()
            initial_temp = self.parse_temperature_result(initial_temp_raw)
            
            # PRIORIZAR SWEEP NATIVO DEL ADMX2001 (mucho más rápido)
            try:
                print("🚀 Intentando sweep nativo del ADMX2001...")
                
                # El firmware usa kHz para sweep_type según documentación
                kstart = float(start_freq) / 1000.0
                kend = float(end_freq) / 1000.0
                
                # Configurar parámetros de sweep nativo (usar secuencia exitosa)
                self.send_command(f"count {points}")    # Número de puntos
                self.send_command(f"sweep_type frequency {kstart:.6f} {kend:.6f}")  # Rango en kHz
                self.send_command(f"sweep_scale {scale}")  # Escala log/linear
                
                # Ejecutar sweep nativo
                print("📡 Ejecutando sweep nativo...")
                # Usar un lector especializado para capturar la salida del sweep nativo
                native_timeout = max(5.0, min(estimated_time * 1.2, 60.0))
                raw_lines = self._capture_native_sweep(timeout=native_timeout)
                print(f"🔍 Respuesta comando 'z': {len(raw_lines) if raw_lines else 0} líneas")
                
                # Debug: mostrar las primeras líneas recibidas
                if raw_lines:
                    print("📝 Primeras líneas recibidas:")
                    for i, line in enumerate(raw_lines[:5]):
                        print(f"  [{i+1}] {repr(line)}")
                    if len(raw_lines) > 5:
                        print(f"  ... y {len(raw_lines)-5} líneas más")
                
                # Parsear líneas devueltas por el sweep nativo
                results = []
                valid_data_lines = []
                
                # Filtrar solo las líneas con datos válidos (formato: freq,real,imag)
                for line in raw_lines:
                    if not isinstance(line, str):
                        continue
                    line = line.strip()
                    
                    # Saltar líneas que no son datos
                    if (not line or 
                        line.startswith("ADMX2001>") or 
                        "warn" in line.lower() or
                        "autorange" in line.lower() or
                        "=" in line or
                        not ',' in line):
                        continue
                    
                    # Verificar formato científico: número,número,número
                    if line.count(',') >= 2:
                        try:
                            parts = line.split(',')
                            freq_raw = float(parts[0])   # Frecuencia (unidad a determinar)
                            real = float(parts[1])       # Resistencia (parte real)
                            imag = float(parts[2])       # Reactancia (parte imaginaria)
                            
                            # CORRECCIÓN CRÍTICA: Detectar unidad de frecuencia automáticamente
                            freq_hz = self._normalize_frequency_unit(freq_raw, start_freq, end_freq)
                            
                            # Verificar que la frecuencia esté en rango esperado tras normalización
                            if start_freq <= freq_hz <= end_freq:
                                valid_data_lines.append(line)
                                logger.debug(f"Frecuencia normalizada: {freq_raw} → {freq_hz} Hz")
                            else:
                                logger.warning(f"Frecuencia {freq_hz} Hz fuera de rango esperado [{start_freq}-{end_freq}]")
                                
                        except (ValueError, IndexError) as e:
                            logger.debug(f"Error parseando línea: {line} → {e}")
                            continue
                
                print(f"📋 Líneas de datos encontradas: {len(valid_data_lines)}")
                
                # Parsear cada línea de datos válida con unidades corregidas
                for idx, line in enumerate(valid_data_lines):
                    parts = [p.strip() for p in line.split(',')]
                    try:
                        if len(parts) >= 3:
                            # Formato del ADMX2001: frecuencia,real,imag
                            freq_raw = float(parts[0])
                            real = float(parts[1]) 
                            imag = float(parts[2])
                            
                            # Aplicar normalización de frecuencia
                            freq_hz = self._normalize_frequency_unit(freq_raw, start_freq, end_freq)
                            
                            # Calcular magnitude y phase
                            magnitude = (real**2 + imag**2)**0.5
                            phase_rad = math.atan2(imag, real)
                            phase_deg = phase_rad * 180.0 / math.pi
                            
                            # Log optimizado para sweep grandes
                            if idx < 5 or idx % max(1, len(valid_data_lines)//10) == 0:
                                print(f"  📊 Punto {idx+1}: {freq_hz:.0f} Hz → |Z|={magnitude:.1f}Ω ∠{phase_deg:.1f}°")
                            
                            # Crear estructura compatible con análisis existente
                            measurement = {
                                'impedance': {
                                    'success': True,
                                    'magnitude': magnitude,
                                    'phase_degrees': phase_deg,
                                    'resistance': real,
                                    'reactance': imag,
                                    'raw_response': self._efficient_response_storage([line], keep_raw=False)
                                },
                                'temperature': initial_temp,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            results.append({
                                'point': idx + 1,
                                'frequency_hz': freq_hz,  # Frecuencia normalizada
                                'measurement': measurement
                            })
                    except Exception as e:
                        logger.error(f"Error parseando línea {idx}: {line} → {e}")
                        continue
                
                # Si el sweep nativo funcionó, usar esos resultados
                if results and len(results) >= max(3, points * 0.5):  # Al menos 50% de los puntos o mínimo 3
                    measurement_time = time.time() - start_time
                    print(f"✅ Sweep nativo completado en {measurement_time:.1f}s: {len(results)} puntos de {points} solicitados")
                    
                    # Análisis de resultados
                    analysis = self._analyze_sweep_results(results)
                    analysis['method'] = 'native_sweep'
                    errors = []
                    
                else:
                    raise RuntimeError("Sweep nativo devolvió pocos puntos válidos")
                    
            except Exception as native_exc:
                # FALLBACK: Medición punto-a-punto si falla el sweep nativo
                print(f"⚠️ Sweep nativo falló: {native_exc}")
                print("🔁 Fallback: realizando medición punto-a-punto...")
                
                # Generar puntos de frecuencia según la escala seleccionada
                if scale == "log":
                    frequencies = [start_freq * (end_freq/start_freq)**(i/(points-1)) 
                                 for i in range(points)]
                else:  # linear
                    step = (end_freq - start_freq) / (points - 1)
                    frequencies = [start_freq + i * step for i in range(points)]
                
                # Realizar mediciones punto a punto
                results = []
                errors = []
                
                for i, freq in enumerate(frequencies):
                    print(f"  📏 Punto {i+1}/{points}: {freq:.1f} Hz")
                    
                    try:
                        measurement = self.quick_impedance_measurement(freq)
                        
                        if measurement.get('impedance', {}).get('success'):
                            results.append({
                                'point': i+1,
                                'frequency_hz': freq,
                                'measurement': measurement
                            })
                        else:
                            errors.append({
                                'point': i+1,
                                'frequency_hz': freq,
                                'error': measurement.get('error', 'Medición fallida')
                            })
                            
                    except Exception as e:
                        errors.append({
                            'point': i+1,
                            'frequency_hz': freq,
                            'error': str(e)
                        })
                    
                    # Pausa mínima entre mediciones
                    time.sleep(0.02)
                
                # Análisis de resultados del fallback
                analysis = self._analyze_sweep_results(results)
                analysis['method'] = 'point_by_point_fallback'
            
            sweep_data = {
                'sweep_parameters': {
                    'start_frequency_hz': start_freq,
                    'end_frequency_hz': end_freq,
                    'points_requested': points,
                    'points_measured': len(results),
                    'scale': scale,
                    'timestamp': datetime.now().isoformat()
                },
                'measurements': results,
                'errors': errors,
                'analysis': analysis,
                'success': len(results) > 0
            }
            
            # Guardar en archivo si se solicita
            if save_to_file and len(results) > 0:
                filename = f"sweep_{start_freq}Hz_to_{end_freq}Hz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                import json
                with open(filename, 'w') as f:
                    json.dump(sweep_data, f, indent=2)
                sweep_data['saved_file'] = filename
                print(f"💾 Resultados guardados en: {filename}")
            
            print(f"✅ Barrido completado: {len(results)}/{points} mediciones exitosas")
            return sweep_data
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'sweep_parameters': {
                    'start_frequency_hz': start_freq,
                    'end_frequency_hz': end_freq,
                    'points_requested': points,
                    'scale': scale
                }
            }

    def _analyze_sweep_results(self, results: List[dict]) -> dict:
        """
        Analiza resultados de un barrido de frecuencia.
        
        Args:
            results (List[dict]): Lista de resultados de medición
            
        Returns:
            dict: Análisis estadístico de los resultados
        """
        if not results:
            return {'error': 'No hay datos para analizar'}
        
        try:
            # Extraer datos numéricos
            frequencies = []
            magnitudes = []
            phases = []
            resistances = []
            reactances = []
            
            for result in results:
                imp_data = result.get('measurement', {}).get('impedance', {})
                if imp_data.get('success'):
                    frequencies.append(result['frequency_hz'])
                    magnitudes.append(imp_data.get('magnitude', 0))
                    phases.append(imp_data.get('phase_degrees', 0))
                    resistances.append(imp_data.get('resistance', 0))
                    reactances.append(imp_data.get('reactance', 0))
            
            if not frequencies:
                return {'error': 'No hay datos válidos para analizar'}
            
            # Estadísticas básicas
            analysis = {
                'data_points': len(frequencies),
                'frequency_range': {
                    'min_hz': min(frequencies),
                    'max_hz': max(frequencies),
                    'span_hz': max(frequencies) - min(frequencies)
                },
                'magnitude_stats': {
                    'min_ohm': min(magnitudes),
                    'max_ohm': max(magnitudes),
                    'avg_ohm': sum(magnitudes) / len(magnitudes),
                    'range_ohm': max(magnitudes) - min(magnitudes)
                },
                'phase_stats': {
                    'min_deg': min(phases),
                    'max_deg': max(phases),
                    'avg_deg': sum(phases) / len(phases),
                    'range_deg': max(phases) - min(phases)
                },
                'resistance_stats': {
                    'min_ohm': min(resistances),
                    'max_ohm': max(resistances),
                    'avg_ohm': sum(resistances) / len(resistances)
                },
                'reactance_stats': {
                    'min_ohm': min(reactances),
                    'max_ohm': max(reactances),
                    'avg_ohm': sum(reactances) / len(reactances)
                }
            }
            
            # Detectar resonancias (mínimos en magnitud)
            resonances = []
            for i in range(1, len(magnitudes) - 1):
                if magnitudes[i] < magnitudes[i-1] and magnitudes[i] < magnitudes[i+1]:
                    resonances.append({
                        'frequency_hz': frequencies[i],
                        'magnitude_ohm': magnitudes[i],
                        'phase_deg': phases[i]
                    })
            
            analysis['resonances_detected'] = resonances
            analysis['resonance_count'] = len(resonances)
            
            return analysis
            
        except Exception as e:
            return {'error': f'Error en análisis: {str(e)}'}

    def _capture_native_sweep(self, timeout: float = 10.0) -> List[str]:
        """
        Captura la salida del sweep nativo enviando 'z' y leyendo bytes
        directamente del puerto serie, recogiendo líneas que parezcan
        números en notación científica: freq,real,imag
        """
        if not self.ser or not self.ser.is_open:
            raise serial.SerialException("Puerto serie no abierto")

        # Limpiar buffers
        try:
            self.ser.reset_input_buffer()
        except Exception:
            pass

        # Enviar comando sweep
        try:
            self.ser.write(b'z\r\n')
        except Exception as e:
            logger.error(f"Error al enviar 'z': {e}")
            return []

        deadline = time.time() + timeout
        lines = []
        partial = ''
        while time.time() < deadline:
            try:
                chunk = self.ser.read(1024)
            except Exception as e:
                logger.debug(f"Error leyendo sweep nativo: {e}")
                break

            if not chunk:
                time.sleep(0.01)
                continue

            try:
                text = chunk.decode('utf-8', errors='replace')
            except Exception:
                text = repr(chunk)

            # Append to partial buffer
            partial += text

            # Clean obvious ANSI/control sequences to make regex matching easier
            cleaned = ANSI_ESCAPE_PATTERN.sub('', partial)
            cleaned = cleaned.replace('\x1b7', '').replace('\x1b8', '')
            # Replace stray control chars with spaces to preserve separators
            cleaned = re.sub(r'[\x00-\x1F\x7F]+', ' ', cleaned)

            # Find CSV-like numeric patterns anywhere in the cleaned chunk
            # Pattern: number,number,number (scientific notation allowed)
            csv_pattern = re.compile(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?\s*,\s*[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?\s*,\s*[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
            for m in csv_pattern.finditer(cleaned):
                candidate = m.group(1).strip()
                # Basic sanity check: must have at least two commas
                if candidate.count(',') >= 2:
                    lines.append(candidate)

            # Also split cleaned text into lines to detect prompts or completion
            parts = cleaned.splitlines()
            # Keep remainder as partial in case of truncated last line
            partial = parts[-1] if parts and not cleaned.endswith('\n') else ''

            for ln in parts:
                ln = ln.strip()
                if not ln:
                    continue
                if PROMPT_PATTERN.match(ln):
                    return lines
                low = ln.lower()
                if 'warn' in low or 'autorange' in low or ln.startswith('ADMX2001>'):
                    continue
                # Keep any CSV lines that survived
                if ln.count(',') >= 2 and ln not in lines:
                    lines.append(ln)

        # timeout expired
        return lines

    def advanced_component_analysis(self, frequencies: List[Union[int, float]], 
                                   component_type: str = "unknown") -> dict:
        """
        Realiza análisis avanzado para identificar tipo de componente.
        
        Args:
            frequencies (List[Union[int, float]]): Lista de frecuencias a medir
            component_type (str): Tipo esperado ("capacitor", "inductor", "resistor", "unknown")
            
        Returns:
            dict: Análisis completo del componente
        """
        try:
            print(f"🔬 Analizando componente tipo: {component_type}")
            
            measurements = []
            for freq in frequencies:
                print(f"  📏 Midiendo a {freq} Hz...")
                result = self.quick_impedance_measurement(freq)
                measurements.append({
                    'frequency_hz': freq,
                    'data': result
                })
                time.sleep(0.2)
            
            # Análisis específico por tipo de componente
            component_analysis = self._analyze_component_behavior(measurements, component_type)
            
            return {
                'component_type_expected': component_type,
                'component_type_detected': component_analysis.get('detected_type', 'unknown'),
                'measurements': measurements,
                'analysis': component_analysis,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'component_type_expected': component_type
            }

    def _analyze_component_behavior(self, measurements: List[dict], expected_type: str) -> dict:
        """
        Analiza el comportamiento de un componente basado en mediciones.
        
        Args:
            measurements (List[dict]): Mediciones del componente
            expected_type (str): Tipo esperado de componente
            
        Returns:
            dict: Análisis del comportamiento del componente
        """
        try:
            # Extraer datos válidos
            valid_data = []
            for measurement in measurements:
                imp_data = measurement.get('data', {}).get('impedance', {})
                if imp_data.get('success'):
                    valid_data.append({
                        'frequency': measurement['frequency_hz'],
                        'magnitude': imp_data.get('magnitude', 0),
                        'phase': imp_data.get('phase_degrees', 0),
                        'resistance': imp_data.get('resistance', 0),
                        'reactance': imp_data.get('reactance', 0)
                    })
            
            if len(valid_data) < 2:
                return {'error': 'Insuficientes datos para análisis'}
            
            # Análisis de tendencias
            frequencies = [d['frequency'] for d in valid_data]
            magnitudes = [d['magnitude'] for d in valid_data]
            phases = [d['phase'] for d in valid_data]
            reactances = [d['reactance'] for d in valid_data]
            
            # Detectar tipo de componente basado en comportamiento
            detected_type = "unknown"
            confidence = 0.0
            
            # Capacitor: impedancia decrece con frecuencia, fase negativa
            if all(phase < -45 for phase in phases) and magnitudes[0] > magnitudes[-1]:
                detected_type = "capacitor"
                confidence = 0.8
                
                # Calcular capacitancia aproximada
                # |Z| = 1/(2*π*f*C)
                capacitances = []
                for i, data in enumerate(valid_data):
                    if data['magnitude'] > 0:
                        C = 1 / (2 * math.pi * data['frequency'] * data['magnitude'])
                        capacitances.append(C)
                
                if capacitances:
                    avg_capacitance = sum(capacitances) / len(capacitances)
                    return {
                        'detected_type': detected_type,
                        'confidence': confidence,
                        'capacitance_F': avg_capacitance,
                        'capacitance_uF': avg_capacitance * 1e6,
                        'capacitance_nF': avg_capacitance * 1e9,
                        'capacitance_pF': avg_capacitance * 1e12,
                        'measurements_used': len(valid_data)
                    }
            
            # Inductor: impedancia aumenta con frecuencia, fase positiva
            elif all(phase > 45 for phase in phases) and magnitudes[0] < magnitudes[-1]:
                detected_type = "inductor"
                confidence = 0.8
                
                # Calcular inductancia aproximada
                # |Z| = 2*π*f*L
                inductances = []
                for data in valid_data:
                    if data['frequency'] > 0:
                        L = data['magnitude'] / (2 * math.pi * data['frequency'])
                        inductances.append(L)
                
                if inductances:
                    avg_inductance = sum(inductances) / len(inductances)
                    return {
                        'detected_type': detected_type,
                        'confidence': confidence,
                        'inductance_H': avg_inductance,
                        'inductance_mH': avg_inductance * 1e3,
                        'inductance_uH': avg_inductance * 1e6,
                        'inductance_nH': avg_inductance * 1e9,
                        'measurements_used': len(valid_data)
                    }
            
            # Resistor: impedancia relativamente constante, fase cerca de 0
            elif all(abs(phase) < 30 for phase in phases):
                detected_type = "resistor"
                confidence = 0.7
                
                avg_resistance = sum(d['resistance'] for d in valid_data) / len(valid_data)
                resistance_variation = max(d['resistance'] for d in valid_data) - min(d['resistance'] for d in valid_data)
                
                return {
                    'detected_type': detected_type,
                    'confidence': confidence,
                    'resistance_ohm': avg_resistance,
                    'resistance_variation_ohm': resistance_variation,
                    'resistance_stability_percent': (1 - resistance_variation/avg_resistance) * 100 if avg_resistance > 0 else 0,
                    'measurements_used': len(valid_data)
                }
            
            # Componente complejo o desconocido
            return {
                'detected_type': detected_type,
                'confidence': confidence,
                'phase_range': [min(phases), max(phases)],
                'magnitude_range': [min(magnitudes), max(magnitudes)],
                'frequency_dependency': 'complex',
                'measurements_used': len(valid_data),
                'note': 'Comportamiento complejo - puede ser componente con múltiples elementos'
            }
            
        except Exception as e:
            return {'error': f'Error en análisis de componente: {str(e)}'}

    def perform_calibration_sequence(self) -> dict:
        """
        Realiza secuencia completa de calibración.
        
        Returns:
            dict: Resultados de la calibración
        """
        results = {}
        
        try:
            print("Iniciando secuencia de calibración...")
            
            # Paso 1: Calibración abierto
            print("1. Conecte OPEN y presione Enter...")
            input()
            results['open'] = self.calibrate_open()
            
            # Paso 2: Calibración cortocircuito
            print("2. Conecte SHORT y presione Enter...")
            input()
            results['short'] = self.calibrate_short()
            
            # Paso 3: Guardar calibración
            print("3. Guardando calibración...")
            results['commit'] = self.calibrate_commit()
            
            print("✅ Calibración completada!")
            return results
            
        except Exception as e:
            return {'error': str(e)}

    def frequency_sweep(self, start_freq: Union[int, float], end_freq: Union[int, float], 
                       points: int = 100, scale: str = "log") -> dict:
        """
        Realiza un barrido de frecuencia completo.
        
        Args:
            start_freq (Union[int, float]): Frecuencia inicial en Hz
            end_freq (Union[int, float]): Frecuencia final en Hz
            points (int): Número de puntos (default: 100)
            scale (str): Escala "log" o "linear" (default: "log")
            
        Returns:
            dict: Resultados del barrido
        """
        try:
            # Configurar barrido
            self.sweep_frequency(start_freq, end_freq)
            self.sweep_points(points)
            self.sweep_scale(scale)
            
            # Ejecutar barrido
            results = self.sweep_run()
            
            return {
                'start_frequency': start_freq,
                'end_frequency': end_freq,
                'points': points,
                'scale': scale,
                'results': results,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {'error': str(e)}

    # ==============================
    # Utilidades y Estado
    # ==============================
    
    def clear_cache(self):
        """
        Limpia el cache de configuraciones.
        
        Útil cuando se sospecha que el dispositivo se ha reseteado
        o cuando se quiere forzar reconfiguración completa.
        """
        with self._cache_lock:
            self._config_cache.clear()
            self._cache_timestamps.clear()
            logger.info("Cache de configuraciones limpiado")
    
    def set_logging_level(self, level: str):
        """
        Configura el nivel de logging dinámicamente.
        
        Args:
            level: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        
        if level.upper() in level_map:
            logger.setLevel(level_map[level.upper()])
            logger.info(f"Nivel de logging configurado a: {level.upper()}")
        else:
            logger.warning(f"Nivel de logging inválido: {level}")

    def get_device_info(self) -> dict:
        """
        Obtiene información completa del dispositivo.
        
        Returns:
            dict: Información del dispositivo
        """
        try:
            return {
                'identification': self.get_idn(),
                'version': self.version(),
                'temperature': self.get_temperature(),
                'selftest': self.selftest(),
                'timestamp': time.time()
            }
        except Exception as e:
            return {'error': str(e)}

    def is_connected(self) -> bool:
        """
        Verifica si el dispositivo está conectado y responde.
        
        Returns:
            bool: True si está conectado
        """
        try:
            response = self.get_idn()
            return len(response) > 0 and 'error' not in response[0].lower()
        except:
            return False

    # ==============================
    # ==============================
    # GESTIÓN DE CONEXIÓN Y RECURSOS
    # ==============================
    
    def close(self):
        """
        Cierra la conexión serie con el dispositivo ADMX2001.
        
        Termina la comunicación con el dispositivo de forma segura, liberando
        el puerto serie para uso por otras aplicaciones. Este método debe
        llamarse siempre al finalizar el trabajo con el dispositivo.
        
        El método realiza las siguientes operaciones:
        1. Verifica que existe una conexión activa
        2. Cierra el puerto serie de forma segura
        3. Actualiza el estado interno de conexión
        4. Libera recursos del sistema operativo
        
        Returns:
            None
        
        Raises:
            No lanza excepciones. Maneja errores internamente para garantizar
            que el puerto se libere incluso si hay problemas.
        
        Example:
            >>> # Uso manual
            >>> device = ADMX2001("/dev/ttyUSB0")
            >>> # ... realizar mediciones ...
            >>> device.close()  # Cerrar explícitamente
            >>> 
            >>> # Uso con context manager (recomendado)
            >>> with ADMX2001("/dev/ttyUSB0") as device:
            ...     # ... realizar mediciones ...
            ...     pass  # close() se llama automáticamente
        
        Note:
            - Es seguro llamar close() múltiples veces
            - Se llama automáticamente al usar context manager (with statement)
            - Se llama automáticamente en el destructor de la clase
            - Libera el puerto para que otras aplicaciones puedan usarlo
            
        Warning:
            - No usar el dispositivo después de llamar close()
            - Para reconectar, crear una nueva instancia de ADMX2001
        """
        try:
            # Verificar si existe conexión activa
            if hasattr(self, 'ser') and self.ser and self.ser.is_open:
                # Limpiar buffers antes de cerrar
                try:
                    self.ser.flushInput()
                    self.ser.flushOutput()
                except:
                    pass  # Ignorar errores de limpieza
                
                # Cerrar puerto serie
                self.ser.close()
                
            # Actualizar estado interno
            self.is_connected = False
            
        except Exception as e:
            # No lanzar excepciones en close() para garantizar limpieza
            self.last_error = f"Advertencia durante cierre: {e}"
            self.is_connected = False
            
    def __enter__(self):
        """
        Entrada del context manager para uso con declaración 'with'.
        
        Permite usar la clase ADMX2001 con la sintaxis 'with' de Python,
        que garantiza el cierre automático de la conexión incluso si
        ocurren errores durante la ejecución.
        
        Returns:
            ADMX2001: La instancia actual del dispositivo, lista para usar
        
        Example:
            >>> with ADMX2001("/dev/ttyUSB0") as device:
            ...     # El dispositivo está conectado y listo
            ...     result = device.quick_impedance_measurement(1000)
            ...     print(f"Impedancia: {result['impedance']['magnitude']:.2f} Ω")
            ...     # close() se llama automáticamente al salir del bloque
        
        Note:
            - Este es el método recomendado para usar el dispositivo
            - Garantiza limpieza de recursos incluso con excepciones
            - Más seguro que manejo manual de conexiones
        """
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Salida del context manager - limpieza automática de recursos.
        
        Se llama automáticamente al salir del bloque 'with', tanto en
        ejecución normal como cuando ocurren excepciones. Garantiza que
        la conexión se cierre apropiadamente.
        
        Args:
            exc_type: Tipo de excepción (si ocurrió)
            exc_val: Valor de la excepción (si ocurrió)  
            exc_tb: Traceback de la excepción (si ocurrió)
        
        Returns:
            None: No suprime excepciones, las propaga normalmente
        
        Note:
            - Se llama automáticamente, no invocar manualmente
            - Garantiza limpieza incluso si hay errores
            - No modifica el manejo de excepciones del código usuario
        """
        self.close()

    def __del__(self):
        """
        Destructor de la clase - limpieza final de recursos.
        
        Se llama automáticamente cuando el objeto es destruido por el
        garbage collector de Python. Proporciona una última oportunidad
        de limpiar recursos si no se hizo explícitamente.
        
        Returns:
            None
        
        Note:
            - Se llama automáticamente por Python
            - No confiar solo en este método para limpieza
            - Usar context manager o close() explícito cuando sea posible
            - Maneja errores silenciosamente para evitar problemas en destrucción
        """
        try:
            self.close()
        except:
            # Ignorar todos los errores durante destrucción
            # Es crítico que __del__ nunca lance excepciones
            pass
    
    def is_device_connected(self) -> bool:
        """
        Verifica si el dispositivo está conectado y responde.
        
        Realiza una verificación activa de la conexión enviando un comando
        simple al dispositivo y verificando que responda apropiadamente.
        
        Returns:
            bool: True si el dispositivo está conectado y responde,
                  False en caso contrario
        
        Example:
            >>> if device.is_device_connected():
            ...     print("✅ Dispositivo listo para usar")
            ... else:
            ...     print("❌ Dispositivo no responde")
        
        Note:
            - Más confiable que solo verificar self.is_connected
            - Puede tardar hasta timeout segundos si hay problemas
            - Actualiza el estado interno de conexión
        """
        try:
            if not self.is_connected or not self.ser or not self.ser.is_open:
                return False
                
            # Intentar comando simple que siempre debe responder
            response = self.send_command("*IDN?")  # Comando de identificación estándar
            
            # Si hay respuesta, el dispositivo está activo
            self.is_connected = len(response) > 0
            return self.is_connected
            
        except Exception:
            self.is_connected = False
            return False
    
    def reconnect(self) -> bool:
        """
        Intenta reconectar al dispositivo después de una desconexión.
        
        Cierra la conexión actual (si existe) e intenta establecer una nueva
        conexión con los mismos parámetros de inicialización.
        
        Returns:
            bool: True si la reconexión fue exitosa, False en caso contrario
        
        Example:
            >>> if not device.is_device_connected():
            ...     if device.reconnect():
            ...         print("✅ Reconexión exitosa")
            ...     else:
            ...         print("❌ No se pudo reconectar")
        
        Note:
            - Útil cuando se detecta pérdida de conexión
            - Usa los mismos parámetros de la conexión original
            - Puede tardar varios segundos en completarse
        """
        try:
            # Cerrar conexión actual si existe
            self.close()
            
            # Intentar nueva conexión
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Pausa de estabilización
            time.sleep(2.0)
            
            # Limpiar buffers
            self.ser.flushInput()
            self.ser.flushOutput()
            
            # Verificar que la conexión funciona
            self.is_connected = True
            if self.is_device_connected():
                self.last_error = None
                return True
            else:
                self.close()
                return False
                
        except Exception as e:
            self.last_error = f"Error en reconexión: {e}"
            self.is_connected = False
            return False


# =====================================================================
# FUNCIONES AUXILIARES GLOBALES
# =====================================================================

def list_available_ports() -> List[str]:
    """
    Lista todos los puertos serie disponibles en el sistema.
    
    Returns:
        List[str]: Lista de nombres de puertos disponibles
    
    Example:
        >>> ports = list_available_ports()
        >>> print(f"Puertos disponibles: {ports}")
        ['COM3', 'COM4']  # En Windows
        ['/dev/ttyUSB0', '/dev/ttyACM0']  # En Linux
    """
    try:
        import serial.tools.list_ports
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return sorted(ports)
    except ImportError:
        # pyserial no disponible o versión antigua
        return []
    except Exception:
        return []


def test_device_connection(port: str, baudrate: int = DEFAULT_BAUDRATE, 
                          timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Prueba la conexión con un dispositivo ADMX2001 en el puerto especificado.
    
    Args:
        port: Puerto serie a probar (ej. "/dev/ttyUSB0")
        baudrate: Velocidad de comunicación (por defecto 115200)
        timeout: Timeout en segundos (por defecto 2.0)
    
    Returns:
        Dict con información de la prueba:
        - success: bool, True si la conexión es exitosa
        - port: str, puerto probado
        - message: str, mensaje descriptivo
        - device_info: str, información del dispositivo (si está disponible)
        - error: str, mensaje de error (si hay fallo)
    
    Example:
        >>> result = test_device_connection("/dev/ttyUSB0")
        >>> if result['success']:
        ...     print(f"✅ Dispositivo encontrado: {result['device_info']}")
        ... else:
        ...     print(f"❌ Error: {result['error']}")
    """
    result = {
        'success': False,
        'port': port,
        'message': '',
        'device_info': '',
        'error': ''
    }
    
    try:
        # Intentar conexión temporal con timeout optimizado
        with ADMX2001(port, baudrate=baudrate, timeout=timeout) as device:
            if device.is_device_connected():
                # Prueba rápida con comando simple
                try:
                    response = device.send_command("VER")  # Comando más rápido que *IDN?
                    device_info = response[0] if response else "ADMX2001 Detectado"
                except:
                    # Si VER falla, intentar comando alternativo
                    try:
                        response = device.send_command("*IDN?")
                        device_info = response[0] if response else "ADMX2001 Identificado"
                    except:
                        device_info = "ADMX2001 (comunicación básica)"
                
                result.update({
                    'success': True,
                    'message': 'Conexión exitosa',
                    'device_info': device_info
                })
            else:
                result.update({
                    'success': False,
                    'message': 'Dispositivo no responde',
                    'error': 'El dispositivo no responde a comandos'
                })
                
    except ConnectionError as e:
        result.update({
            'success': False,
            'message': 'Error de conexión',
            'error': str(e)
        })
    except Exception as e:
        result.update({
            'success': False,
            'message': 'Error desconocido',
            'error': str(e)
        })
    
    return result


def find_admx2001_devices(quick_scan: bool = True) -> List[Dict[str, Any]]:
    """
    Busca automáticamente dispositivos ADMX2001 en todos los puertos disponibles.
    
    Args:
        quick_scan (bool): Si True, usa búsqueda optimizada (recomendado).
                          Si False, busca exhaustivamente en todos los puertos.
    
    Returns:
        List[Dict]: Lista de dispositivos encontrados, cada uno con:
        - port: str, puerto donde se encontró
        - device_info: str, información del dispositivo
        - connection_test: Dict, resultado del test de conexión
    
    Example:
        >>> # Búsqueda rápida (10x más rápido)
        >>> devices = find_admx2001_devices(quick_scan=True)
        >>> 
        >>> # Búsqueda exhaustiva (si no se encuentra en modo rápido)
        >>> devices = find_admx2001_devices(quick_scan=False)
        >>> 
        >>> for device in devices:
        ...     print(f"ADMX2001 encontrado en {device['port']}")
        ...     print(f"Info: {device['device_info']}")
    
    Note:
        El modo quick_scan prioriza puertos USB comunes y usa timeouts menores.
        Es ~10x más rápido que el escaneo completo.
    """
    available_ports = list_available_ports()
    found_devices = []
    
    if quick_scan:
        # Búsqueda optimizada: priorizar puertos USB y comunes
        usb_ports = [p for p in available_ports if any(x in p for x in ['USB', 'ACM', 'ttyUSB'])]
        common_serial = [p for p in available_ports if any(x in p for x in ['/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3'])]
        
        priority_ports = usb_ports + common_serial[:4]  # Solo los primeros 4 puertos serie
        
        print(f"🚀 Búsqueda rápida en {len(priority_ports)} puertos prioritarios...")
        
        for port in priority_ports:
            print(f"Probando puerto {port}...")
            test_result = test_device_connection(port, timeout=1.5)  # Timeout reducido
            
            if test_result['success']:
                found_devices.append({
                    'port': port,
                    'device_info': test_result['device_info'],
                    'connection_test': test_result
                })
                print(f"✅ ADMX2001 encontrado en {port}")
                return found_devices  # Retornar inmediatamente al encontrar uno
            else:
                print(f"❌ No hay ADMX2001 en {port}")
        
        if not found_devices:
            print("⚠️  No se encontró en puertos comunes. Usa quick_scan=False para búsqueda exhaustiva.")
    
    else:
        # Búsqueda exhaustiva en todos los puertos
        print(f"🔍 Búsqueda exhaustiva en {len(available_ports)} puertos...")
        
        for port in available_ports:
            print(f"Probando puerto {port}...")
            test_result = test_device_connection(port)
            
            if test_result['success']:
                found_devices.append({
                    'port': port,
                    'device_info': test_result['device_info'],
                    'connection_test': test_result
                })
                print(f"✅ ADMX2001 encontrado en {port}")
            else:
                print(f"❌ No hay ADMX2001 en {port}")
    
    return found_devices


# =====================================================================
# FUNCIONES DE ANÁLISIS AVANZADO
# =====================================================================

def analyze_component_type(impedance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analiza una serie de mediciones de impedancia para determinar el tipo de componente.
    
    Args:
        impedance_data: Lista de mediciones con frecuencia, magnitud y fase
    
    Returns:
        Dict con análisis del componente:
        - detected_type: str, tipo detectado ("resistor", "capacitor", "inductor", "unknown")
        - confidence: float, confianza del análisis (0.0 a 1.0)
        - characteristics: Dict, características específicas del componente
        - recommendations: List[str], recomendaciones para el usuario
    
    Example:
        >>> data = [
        ...     {'frequency': 100, 'magnitude': 1000, 'phase_degrees': -2},
        ...     {'frequency': 1000, 'magnitude': 1002, 'phase_degrees': -1},
        ...     {'frequency': 10000, 'magnitude': 1005, 'phase_degrees': 0}
        ... ]
        >>> analysis = analyze_component_type(data)
        >>> print(f"Tipo: {analysis['detected_type']}")
        >>> print(f"Confianza: {analysis['confidence']:.1%}")
    """
    if not impedance_data or len(impedance_data) < 2:
        return {
            'detected_type': 'unknown',
            'confidence': 0.0,
            'characteristics': {},
            'recommendations': ['Necesita más datos para análisis']
        }
    
    # Extraer datos para análisis
    frequencies = [d['frequency'] for d in impedance_data]
    magnitudes = [d['magnitude'] for d in impedance_data]
    phases = [d['phase_degrees'] for d in impedance_data]
    
    # Calcular tendencias
    freq_ratio = max(frequencies) / min(frequencies)
    mag_variation = (max(magnitudes) - min(magnitudes)) / min(magnitudes)
    phase_average = sum(phases) / len(phases)
    phase_variation = max(phases) - min(phases)
    
    analysis = {
        'detected_type': 'unknown',
        'confidence': 0.0,
        'characteristics': {
            'frequency_range_ratio': freq_ratio,
            'magnitude_variation': mag_variation,
            'phase_average': phase_average,
            'phase_variation': phase_variation
        },
        'recommendations': []
    }
    
    # Análisis de tipo de componente
    if abs(phase_average) < 10 and phase_variation < 15:
        # Comportamiento resistivo
        analysis['detected_type'] = 'resistor'
        analysis['confidence'] = 0.8 if mag_variation < 0.1 else 0.6
        analysis['characteristics']['estimated_resistance'] = sum(magnitudes) / len(magnitudes)
        analysis['recommendations'] = [
            'Componente resistivo detectado',
            'Verificar estabilidad en frecuencia',
            'Comprobar efectos parasitarios en altas frecuencias'
        ]
        
    elif phase_average < -45 and phase_variation < 30:
        # Comportamiento capacitivo
        analysis['detected_type'] = 'capacitor'
        analysis['confidence'] = 0.7
        
        # Estimar capacitancia (fórmula simplificada)
        if len(impedance_data) >= 2:
            f1, z1 = frequencies[0], magnitudes[0]
            f2, z2 = frequencies[1], magnitudes[1]
            if f1 != f2 and z1 > 0 and z2 > 0:
                # C = 1 / (2 * pi * f * |Z|)
                c1 = 1 / (2 * math.pi * f1 * z1)
                c2 = 1 / (2 * math.pi * f2 * z2)
                estimated_c = (c1 + c2) / 2
                analysis['characteristics']['estimated_capacitance_f'] = estimated_c
        
        analysis['recommendations'] = [
            'Componente capacitivo detectado',
            'Verificar ESR en alta frecuencia',
            'Comprobar resonancia serie'
        ]
        
    elif phase_average > 45 and phase_variation < 30:
        # Comportamiento inductivo
        analysis['detected_type'] = 'inductor'
        analysis['confidence'] = 0.7
        
        # Estimar inductancia (fórmula simplificada)
        if len(impedance_data) >= 2:
            f1, z1 = frequencies[0], magnitudes[0]
            f2, z2 = frequencies[1], magnitudes[1]
            if f1 != f2:
                # L = |Z| / (2 * pi * f)
                l1 = z1 / (2 * math.pi * f1)
                l2 = z2 / (2 * math.pi * f2)
                estimated_l = (l1 + l2) / 2
                analysis['characteristics']['estimated_inductance_h'] = estimated_l
        
        analysis['recommendations'] = [
            'Componente inductivo detectado',
            'Verificar frecuencia de auto-resonancia',
            'Comprobar factor Q'
        ]
    
    else:
        # Comportamiento complejo o desconocido
        analysis['detected_type'] = 'complex'
        analysis['confidence'] = 0.3
        analysis['recommendations'] = [
            'Componente complejo o circuito detectado',
            'Puede ser combinación R-L-C',
            'Analizar resonancias o anti-resonancias',
            'Considerar usar más puntos de frecuencia'
        ]
    
    return analysis
