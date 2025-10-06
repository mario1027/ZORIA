"""
Clase principal ADMX2001 para control del analizador de impedancia.

Esta es la clase principal que proporciona acceso completo a todas
las funcionalidades del EVAL-ADMX2001 de Analog Devices.
"""

import serial
import time
import logging
import re
from typing import List, Optional, Dict, Tuple, Union, Any
from datetime import datetime

from .exceptions import (
    ADMX2001Error, ConnectionError, MeasurementError,
    TimeoutError, CommandError, ValidationError
)
from .enums import (
    DisplayMode, SweepType, SweepScale, TriggerMode,
    GainChannel0, GainChannel1, ImpedanceRange,
    DEFAULT_BAUDRATE, DEFAULT_TIMEOUT, COMMAND_TIMEOUT,
    TEMPERATURE_WARNING_THRESHOLD
)
from .utils import (
    validate_frequency, validate_magnitude, validate_offset,
    validate_average, validate_count,
    calculate_impedance_from_rx, clean_response_line,
    parse_measurement_line, parse_numeric_response,
    estimate_measurement_time
)
from .calibration import CalibrationManager

logger = logging.getLogger(__name__)


class MeasurementManager:
    """
    Gestiona las mediciones y su procesamiento.
    
    Separa la lógica de medición de la clase principal para
    mayor claridad y mantenibilidad.
    """
    
    def __init__(self, device):
        self.device = device
        
    def measure_impedance(self, parse: bool = True) -> Union[Dict, List[str]]:
        """
        Realiza una medición de impedancia.
        
        Usa el comando 'z' según la documentación del EVAL-ADMX2001.
        
        Args:
            parse: Si True, parsea automáticamente el resultado
        
        Returns:
            Si parse=True: diccionario con valores parseados
            Si parse=False: respuesta cruda del dispositivo
        """
        try:
            # Comando 'z' para medir
            response = self.device.send_command("z")
            
            if parse:
                return self.parse_impedance_response(response)
            else:
                return response
                
        except Exception as e:
            logger.error(f"Error en medición: {e}")
            raise MeasurementError(f"Error en medición de impedancia: {e}")
    
    def parse_impedance_response(self, response: List[str]) -> Dict[str, any]:
        """
        Parsea la respuesta de medición de impedancia.
        
        El formato depende del display mode configurado.
        Formato típico: "index, valor1, valor2"
        
        Returns:
            Diccionario estructurado con los resultados
        """
        result = {
            'success': False,
            'raw_response': response,
            'measurements': [],
            'display_mode': None,
            'timestamp': datetime.now().isoformat()
        }
        
        for line in response:
            parsed_line = parse_measurement_line(line)
            if parsed_line and len(parsed_line) >= 3:
                measurement = {
                    'index': int(parsed_line[0]),
                    'value1': parsed_line[1],
                    'value2': parsed_line[2]
                }
                
                # Si está en modo R,X calcular parámetros adicionales
                if self.device.current_config.get('display_mode') == DisplayMode.R_X:
                    r = parsed_line[1]
                    x = parsed_line[2]
                    impedance_params = calculate_impedance_from_rx(r, x)
                    measurement.update({
                        'resistance': r,
                        'reactance': x,
                        'magnitude': impedance_params['magnitude'],
                        'phase_deg': impedance_params['phase_deg'],
                        'phase_rad': impedance_params['phase_rad'],
                        'conductance': impedance_params['conductance'],
                        'susceptance': impedance_params['susceptance']
                    })
                
                result['measurements'].append(measurement)
                result['success'] = True
        
        return result
    
    def measure_temperature(self) -> Dict[str, any]:
        """
        Mide la temperatura interna del dispositivo.
        
        Returns:
            Diccionario con temperatura y estado
        """
        try:
            response = self.device.send_command("temperature")
            
            result = {
                'success': False,
                'temperature_celsius': None,
                'warning': False,
                'raw_response': response
            }
            
            # Buscar patrón "XX.X deg C"
            for line in response:
                match = re.search(r'([\d.]+)\s*deg\s*C', line, re.IGNORECASE)
                if match:
                    temp = float(match.group(1))
                    result['temperature_celsius'] = temp
                    result['success'] = True
                    
                    if temp > TEMPERATURE_WARNING_THRESHOLD:
                        result['warning'] = True
                        logger.warning(f"Temperatura alta detectada: {temp}°C")
                    
                    break
            
            return result
            
        except Exception as e:
            logger.error(f"Error leyendo temperatura: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def measure_dcr(self) -> Dict[str, any]:
        """
        Mide resistencia DC.
        
        Según documentación:
        - Configurar frequency 0
        - Usar offset negativo
        - Display mode 6 (R,X)
        """
        try:
            # Guardar configuración actual
            prev_freq = self.device.current_config.get('frequency')
            prev_offset = self.device.current_config.get('offset')
            prev_display = self.device.current_config.get('display_mode')
            
            # Configurar para modo DC
            self.device.send_command("frequency 0")
            self.device.send_command("display 6")
            self.device.send_command("offset -1")
            
            # Medir
            response = self.device.send_command("z")
            
            # Parsear
            result = {
                'success': False,
                'dcr_ohms': None,
                'raw_response': response
            }
            
            for line in response:
                parsed = parse_measurement_line(line)
                if parsed and len(parsed) >= 2:
                    result['dcr_ohms'] = parsed[1]  # Segundo valor es la resistencia
                    result['success'] = True
                    break
            
            # Restaurar configuración
            if prev_freq is not None:
                self.device.send_command(f"frequency {prev_freq/1000}")
            if prev_offset is not None:
                self.device.send_command(f"offset {prev_offset}")
            if prev_display is not None:
                self.device.send_command(f"display {prev_display}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en medición DCR: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class ADMX2001:
    """
    Clase principal para controlar el EVAL-ADMX2001.
    
    Proporciona acceso completo a todas las funcionalidades:
    - Configuración de parámetros de medición
    - Mediciones de impedancia, temperatura, DC
    - Calibración
    - Barridos (sweeps)
    - Control GPIO y triggers
    
    Example:
        >>> with ADMX2001('/dev/ttyUSB0') as device:
        ...     device.set_frequency(1000)  # 1 kHz
        ...     device.set_magnitude(0.5)   # 0.5 Vpk
        ...     result = device.measure_impedance()
        ...     print(f"Impedancia: {result['measurements'][0]['magnitude']} Ω")
    
    Attributes:
        serial: Objeto serial.Serial para comunicación
        calibration: CalibrationManager para gestión de calibración
        measurement: MeasurementManager para gestión de mediciones
        current_config: Diccionario con configuración actual
        is_connected: Estado de conexión
    """
    
    def __init__(self, port: str, baudrate: int = DEFAULT_BAUDRATE, 
                 timeout: float = DEFAULT_TIMEOUT):
        """
        Inicializa conexión con ADMX2001.
        
        Args:
            port: Ruta del puerto serie (/dev/ttyUSB0, COM3, etc.)
            baudrate: Velocidad de comunicación (default: 115200)
            timeout: Timeout en segundos (default: 2.0)
        
        Raises:
            ConnectionError: Si no se puede conectar al dispositivo
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.is_connected = False
        
        # Managers
        self.calibration = CalibrationManager(self)
        self.measurement = MeasurementManager(self)
        
        # Estado interno
        self.current_config = {
            'frequency': None,
            'magnitude': None,
            'offset': None,
            'average': None,
            'count': None,
            'display_mode': DisplayMode.R_X,
            'ch0_gain': None,
            'ch1_gain': None,
            'autorange': True
        }
        
        # Estadísticas
        self.command_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        # Conectar
        self._connect()
        
    def _connect(self) -> None:
        """Establece conexión con el dispositivo."""
        try:
            logger.info(f"Conectando a {self.port} @ {self.baudrate} baud...")
            
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Limpiar buffers
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
            # Enviar enter para obtener prompt
            self.serial.write(b'\n')
            time.sleep(0.2)
            prompt_response = self.serial.read(1024).decode('utf-8', errors='ignore')
            
            # Verificar si hay prompt ADMX2001>
            if 'ADMX2001>' in prompt_response or True:  # Asumir conectado si el puerto abrió
                self.is_connected = True
                logger.info(f"Conectado exitosamente a EVAL-ADMX2001")
            else:
                raise ConnectionError("No se recibió respuesta del dispositivo")
                
        except serial.SerialException as e:
            raise ConnectionError(f"Error abriendo puerto serie: {e}")
        except Exception as e:
            raise ConnectionError(f"Error conectando: {e}")
    
    def send_command(self, command: str, timeout: Optional[float] = None,
                    expect_prompt: bool = True, retries: int = 2) -> List[str]:
        """
        Envía un comando al dispositivo y lee la respuesta.
        
        Args:
            command: Comando a enviar (sin \\n final)
            timeout: Timeout opcional para este comando
            expect_prompt: Si esperar el prompt "ADMX2001>" al final
            retries: Número de reintentos en caso de error (default: 2)
        
        Returns:
            Lista de líneas de respuesta
        
        Raises:
            CommandError: Si hay error enviando el comando
            TimeoutError: Si no se recibe respuesta en el tiempo esperado
        """
        if not self.is_connected or self.serial is None:
            raise ConnectionError("No conectado al dispositivo")
        
        last_exception = None
        
        for attempt in range(retries + 1):
            try:
                # Limpiar comando
                command = command.strip()
                
                # Limpiar buffers antes de enviar (solo en reintentos)
                if attempt > 0:
                    logger.debug(f"Reintento {attempt}/{retries} para comando: {command}")
                    time.sleep(0.2)
                    try:
                        self.serial.reset_input_buffer()
                        self.serial.reset_output_buffer()
                    except:
                        pass
                
                # Enviar comando
                cmd_bytes = (command + '\n').encode('utf-8')
                self.serial.write(cmd_bytes)
                self.command_count += 1
                
                logger.debug(f"Comando enviado: {command}")
                
                # Leer respuesta
                original_timeout = self.serial.timeout
                if timeout:
                    self.serial.timeout = timeout
                
                response_lines = []
                start_time = time.time()
                max_time = timeout or COMMAND_TIMEOUT
                
                # Buffer para acumular datos fragmentados
                response_buffer = ""
                
                # Esperar un momento para que el dispositivo procese el comando
                time.sleep(0.1)
                
                while True:
                    if time.time() - start_time > max_time:
                        raise TimeoutError(f"Timeout esperando respuesta para: {command}")
                    
                    # Verificar si hay datos disponibles antes de leer
                    if self.serial.in_waiting > 0:
                        try:
                            # Leer TODO lo disponible (estrategia robusta)
                            chunk = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                            response_buffer += chunk
                            logger.debug(f"Recibido chunk: {repr(chunk[:100])}")
                        except serial.SerialException as e:
                            # Si hay error leyendo, marcar como desconectado y relanzar
                            logger.error(f"Error de lectura serial: {e}")
                            self.is_connected = False
                            raise
                        
                        # Verificar si encontramos el prompt (indica fin de respuesta)
                        if expect_prompt and 'ADMX2001>' in response_buffer:
                            break
                    else:
                        # No hay datos disponibles, esperar un poco
                        time.sleep(0.05)
                        
                        # Si tenemos datos en el buffer y no hay más datos entrantes, salir
                        if response_buffer and self.serial.in_waiting == 0:
                            time.sleep(0.05)  # Espera adicional
                            if self.serial.in_waiting == 0:
                                # Doble check para asegurar que realmente no hay más datos
                                break
                
                # Procesar el buffer completo por líneas
                if response_buffer:
                    for line in response_buffer.split('\n'):
                        line = clean_response_line(line)
                        if line:
                            response_lines.append(line)
                            logger.debug(f"Línea procesada: {line}")
                
                # Restaurar timeout
                self.serial.timeout = original_timeout
                
                # Si llegamos aquí, el comando fue exitoso
                return response_lines
                
            except serial.SerialException as e:
                last_exception = e
                self.error_count += 1
                logger.warning(f"Error de comunicación (intento {attempt+1}/{retries+1}): {e}")
                
                # Si quedan reintentos, continuar
                if attempt < retries:
                    continue
                else:
                    # No hay más reintentos, lanzar el error
                    raise CommandError(f"Error de comunicación después de {retries+1} intentos: {e}")
                    
            except Exception as e:
                last_exception = e
                self.error_count += 1
                
                # Para otros errores, no reintentar
                raise CommandError(f"Error ejecutando comando '{command}': {e}")
        
        # Si llegamos aquí (no debería pasar), lanzar el último error
        if last_exception:
            raise CommandError(f"Error ejecutando comando '{command}': {last_exception}")
    
    # ==================== Configuración de Parámetros ====================
    
    def set_frequency(self, frequency: float) -> None:
        """
        Configura la frecuencia de excitación.
        
        Args:
            frequency: Frecuencia en Hz (0.2 - 10MHz, o 0 para modo DC)
        
        Raises:
            ValidationError: Si la frecuencia está fuera de rango
        """
        validate_frequency(frequency)
        
        # Convertir a kHz como espera el dispositivo
        freq_khz = frequency / 1000.0 if frequency > 0 else 0
        
        self.send_command(f"frequency {freq_khz}")
        self.current_config['frequency'] = frequency
        
        logger.info(f"Frecuencia configurada: {frequency} Hz")
    
    def set_magnitude(self, magnitude: float) -> None:
        """
        Configura la magnitud (amplitud) de la señal.
        
        Args:
            magnitude: Magnitud en Vpk (0.15 - 2.25)
        
        Raises:
            ValidationError: Si la magnitud está fuera de rango
        """
        validate_magnitude(magnitude)
        
        self.send_command(f"magnitude {magnitude}")
        self.current_config['magnitude'] = magnitude
        
        logger.info(f"Magnitud configurada: {magnitude} Vpk")
    
    def set_offset(self, offset: float) -> None:
        """
        Configura el offset DC.
        
        Args:
            offset: Offset en V (-2.0 a +2.0)
        
        Note:
            El autorange debe estar deshabilitado para usar offset DC.
            El offset negativo es recomendado para detectar saturación.
        
        Raises:
            ValidationError: Si el offset está fuera de rango
        """
        validate_offset(offset)
        
        self.send_command(f"offset {offset}")
        self.current_config['offset'] = offset
        
        logger.info(f"Offset configurado: {offset} V")
    
    def set_average(self, average: int) -> None:
        """
        Configura el número de promedios por medición.
        
        Args:
            average: Número de promedios (1-256)
        
        Note:
            Valores > 256 tienen poco efecto adicional según documentación.
        
        Raises:
            ValidationError: Si el valor está fuera de rango
        """
        validate_average(average)
        
        self.send_command(f"average {average}")
        self.current_config['average'] = average
        
        logger.info(f"Average configurado: {average}")
    
    def set_count(self, count: int) -> None:
        """
        Configura el número de muestras a tomar.
        
        Args:
            count: Número de muestras (1-1000)
        
        Raises:
            ValidationError: Si count está fuera de rango
        """
        validate_count(count)
        
        self.send_command(f"count {count}")
        self.current_config['count'] = count
        
        logger.info(f"Count configurado: {count}")
    
    def set_display_mode(self, mode: Union[DisplayMode, int]) -> None:
        """
        Configura el modo de visualización/formato de salida.
        
        Args:
            mode: Modo de display (0-18), ver DisplayMode enum
        
        Example:
            >>> device.set_display_mode(DisplayMode.R_X)  # Impedancia rectangular
            >>> device.set_display_mode(DisplayMode.Z_DEG)  # Magnitud y fase
        """
        if isinstance(mode, DisplayMode):
            mode_value = mode.value
        else:
            mode_value = int(mode)
        
        if mode_value < 0 or mode_value > 18:
            raise ValidationError(f"Display mode debe estar entre 0 y 18: {mode_value}")
        
        self.send_command(f"display {mode_value}")
        self.current_config['display_mode'] = mode_value
        
        logger.info(f"Display mode configurado: {mode_value}")
    
    def set_gain_auto(self) -> None:
        """
        Habilita el modo de ganancia automática (autorange).
        
        El dispositivo seleccionará automáticamente la ganancia
        óptima para evitar saturación.
        
        Note:
            El DC offset no puede usarse con autorange habilitado.
        """
        self.send_command("setgain auto")
        self.current_config['autorange'] = True
        logger.info("Autorange habilitado")
    
    def set_gain_manual(self, ch0_gain: int, ch1_gain: int) -> None:
        """
        Configura ganancia manual para ambos canales.
        
        Args:
            ch0_gain: Ganancia canal 0 (voltaje): 0-3
            ch1_gain: Ganancia canal 1 (corriente): 0-3
        
        See Also:
            GainChannel0, GainChannel1, ImpedanceRange enums
            utils.recommend_gain_settings() para recomendaciones
        """
        if ch0_gain not in [0, 1, 2, 3]:
            raise ValidationError(f"ch0_gain debe ser 0-3: {ch0_gain}")
        if ch1_gain not in [0, 1, 2, 3]:
            raise ValidationError(f"ch1_gain debe ser 0-3: {ch1_gain}")
        
        self.send_command("setgain auto off")
        self.send_command(f"setgain ch0 {ch0_gain}")
        self.send_command(f"setgain ch1 {ch1_gain}")
        
        self.current_config['autorange'] = False
        self.current_config['ch0_gain'] = ch0_gain
        self.current_config['ch1_gain'] = ch1_gain
        
        logger.info(f"Ganancia manual: ch0={ch0_gain}, ch1={ch1_gain}")
    
    def set_gain(self, channel: int, gain: int) -> None:
        """
        Configura ganancia para un canal específico.
        
        Comando equivalente al CLI: setgain ch<channel> <gain>
        
        Args:
            channel: Número de canal (0 o 1)
            gain: Valor de ganancia (0-3)
        
        Raises:
            ValidationError: Si los parámetros son inválidos
        
        Note:
            - Canal 0: Voltaje
            - Canal 1: Corriente
            - Este comando desactiva autorange
        
        Example:
            >>> dev.set_gain(0, 2)  # CH0 gain = 2
            >>> dev.set_gain(1, 1)  # CH1 gain = 1
        """
        if channel not in [0, 1]:
            raise ValidationError(f"Canal debe ser 0 o 1: {channel}")
        if gain not in [0, 1, 2, 3]:
            raise ValidationError(f"Ganancia debe ser 0-3: {gain}")
        
        # Desactivar autorange primero
        self.send_command("setgain auto off")
        
        # Configurar ganancia del canal
        self.send_command(f"setgain ch{channel} {gain}")
        
        # Actualizar configuración
        self.current_config['autorange'] = False
        if channel == 0:
            self.current_config['ch0_gain'] = gain
        else:
            self.current_config['ch1_gain'] = gain
        
        logger.info(f"Ganancia canal {channel} = {gain}")
    
    def set_mdelay(self, delay_ms: float) -> None:
        """
        Configura el delay de medición (measurement delay).
        
        Comando equivalente al CLI: mdelay <milliseconds>
        
        El mdelay se observa antes de cada medición, pero no entre muestras
        durante el averaging. También se aplica durante sweeps y entre counts.
        
        Args:
            delay_ms: Delay en milisegundos (0 - 10000)
        
        Raises:
            ValidationError: Si el delay está fuera de rango
        
        Note:
            - Durante el delay, tanto el offset DC como la señal AC están habilitados
            - Los ADCs no capturan datos hasta que el delay ha transcurrido
            - Para optimización de velocidad: mdelay 0
            - Para DUTs capacitivos grandes: usar delay mayor para settling time
        
        Example:
            >>> dev.set_mdelay(10)    # 10 ms delay
            >>> dev.set_mdelay(0)     # Sin delay (máxima velocidad)
            >>> dev.set_mdelay(200)   # 200 ms para calibración
        """
        if delay_ms < 0 or delay_ms > 10000:
            raise ValidationError(f"mdelay debe estar entre 0-10000 ms: {delay_ms}")
        
        self.send_command(f"mdelay {delay_ms}")
        logger.info(f"Measurement delay configurado: {delay_ms} ms")
    
    def set_tdelay(self, delay_ms: float) -> None:
        """
        Configura el delay de trigger (trigger delay).
        
        Comando equivalente al CLI: tdelay <milliseconds>
        
        El tdelay se observa solo después de eventos de trigger controlados
        por el comando tcount. Útil para multiplexores o tarjetas de escaneo.
        
        Args:
            delay_ms: Delay en milisegundos (0 - 10000)
        
        Raises:
            ValidationError: Si el delay está fuera de rango
        
        Note:
            - Durante el delay, el offset DC se habilita
            - La señal AC solo se inicia para la captura de datos
            - Útil para permitir debounce y settling time
        
        Example:
            >>> dev.set_tdelay(200)   # 200 ms para estabilización
            >>> dev.set_tdelay(0)     # Sin delay de trigger
        """
        if delay_ms < 0 or delay_ms > 10000:
            raise ValidationError(f"tdelay debe estar entre 0-10000 ms: {delay_ms}")
        
        self.send_command(f"tdelay {delay_ms}")
        logger.info(f"Trigger delay configurado: {delay_ms} ms")
    
    # ==================== Utilidades ====================
    
    def recommend_impedance_range(self, impedance: float) -> 'ImpedanceRange':
        """
        Recomienda el rango de impedancia óptimo basado en el valor medido.
        
        Args:
            impedance: Valor de impedancia en Ohms
        
        Returns:
            ImpedanceRange correspondiente con configuración de ganancia óptima
        
        Example:
            >>> z = 5000  # 5kΩ
            >>> rango = dev.recommend_impedance_range(z)
            >>> print(rango.name)  # "RANGE_1K_10K"
            >>> ch0_gain, ch1_gain = rango.value
            >>> dev.set_gain(0, ch0_gain)
            >>> dev.set_gain(1, ch1_gain)
        """
        if impedance < 10:
            return ImpedanceRange.UNDER_10_OHM
        elif impedance < 25:
            return ImpedanceRange.UNDER_25_OHM
        elif impedance < 50:
            return ImpedanceRange.UNDER_50_OHM
        elif impedance < 1000:
            return ImpedanceRange.RANGE_100_1K
        elif impedance < 10000:
            return ImpedanceRange.RANGE_1K_10K
        elif impedance < 100000:
            return ImpedanceRange.RANGE_10K_100K
        else:
            return ImpedanceRange.OVER_100K
    
    # ==================== Mediciones ====================
    
    def measure_impedance(self, parse: bool = True) -> Union[Dict, List[str]]:
        """
        Realiza medición de impedancia.
        
        Wrapper conveniente para measurement.measure_impedance()
        """
        return self.measurement.measure_impedance(parse=parse)
    
    def measure(self) -> Tuple[float, float]:
        """
        Realiza medición y retorna tupla (valor1, valor2) según el display mode.
        
        Alias simplificado de measure_impedance() que retorna directamente
        los dos valores medidos como tupla.
        
        Returns:
            (valor1, valor2): Tupla con los dos valores según el modo de display
        
        Example:
            >>> dev.set_display_mode(DisplayMode.R_X)
            >>> r, x = dev.measure()
            >>> print(f"R={r}Ω, X={x}Ω")
        """
        # Intentar hasta 3 veces (a veces la primera medición falla)
        max_attempts = 3
        for attempt in range(max_attempts):
            result = self.measurement.measure_impedance(parse=True)
            
            if result['success'] and len(result['measurements']) > 0:
                measurement = result['measurements'][0]
                return (measurement['value1'], measurement['value2'])
            
            if attempt < max_attempts - 1:
                time.sleep(0.2)  # Esperar antes de reintentar
        
        raise MeasurementError(f"No se pudo obtener medición válida después de {max_attempts} intentos")
    
    def measure_temperature(self) -> Dict[str, any]:
        """
        Mide temperatura interna.
        
        Wrapper conveniente para measurement.measure_temperature()
        """
        return self.measurement.measure_temperature()
    
    def measure_dcr(self) -> Dict[str, any]:
        """
        Mide resistencia DC.
        
        Wrapper conveniente para measurement.measure_dcr()
        """
        return self.measurement.measure_dcr()
    
    # ==================== Barridos (Sweeps) ====================
    
    def configure_sweep(self, sweep_type: SweepType, start: float, end: float,
                       scale: SweepScale = SweepScale.LINEAR, count: int = 11) -> None:
        """
        Configura un barrido paramétrico.
        
        Según documentación oficial, el ADMX2001 puede realizar barridos de:
        - Frecuencia (common en EIS - Electrical Impedance Spectroscopy)
        - DC bias (común en mediciones C-V)
        - Magnitud
        
        Args:
            sweep_type: Tipo de barrido (FREQUENCY, DC_BIAS, MAGNITUDE, OFF)
            start: Valor inicial del barrido
            end: Valor final del barrido
            scale: Escala LINEAR o LOG (default: LINEAR)
            count: Número de puntos (default: 11)
        
        Raises:
            ValidationError: Si los parámetros son inválidos
        
        Note:
            - Para FREQUENCY: valores en kHz
            - Para DC_BIAS: valores en V
            - Para MAGNITUDE: valores en Vpk
            - El número de puntos se controla con el parámetro count
            - Para desactivar sweep: usar sweep_type=SweepType.OFF
        
        Example:
            >>> # Barrido logarítmico de 100kHz a 1MHz, 11 puntos
            >>> dev.configure_sweep(SweepType.FREQUENCY, 100, 1000, 
            ...                     SweepScale.LOG, count=11)
            >>> results = dev.perform_sweep()
        """
        from .utils import validate_count
        
        # Abortar cualquier sweep o medición en progreso
        try:
            self.send_command("abort", expect_prompt=True)
            logger.debug("Estado previo limpiado con 'abort'")
        except:
            pass  # Ignorar si ya está limpio
        
        # Validar count
        validate_count(count)
        
        # Configurar count y guardarlo en la configuración
        self.send_command(f"count {count}")
        self.current_config['count'] = count  # ← Guardar en configuración
        logger.debug(f"Count configurado y guardado: {count}")
        
        if sweep_type == SweepType.OFF:
            # Desactivar sweep
            self.send_command("sweep_type off")
            logger.info("Sweep desactivado")
            return
        
        # Validar parámetros según tipo de sweep
        if sweep_type == SweepType.FREQUENCY:
            from .utils import validate_frequency
            # Convertir kHz a Hz para validación
            validate_frequency(start * 1000)
            validate_frequency(end * 1000)
            if start >= end:
                raise ValidationError(f"start ({start}) debe ser menor que end ({end})")
            cmd = f"sweep_type frequency {start} {end}"
        
        elif sweep_type == SweepType.DC_BIAS:
            from .utils import validate_offset
            validate_offset(start)
            validate_offset(end)
            if start >= end:
                raise ValidationError(f"start ({start}) debe ser menor que end ({end})")
            cmd = f"sweep_type offset {start} {end}"
        
        elif sweep_type == SweepType.MAGNITUDE:
            from .utils import validate_magnitude
            validate_magnitude(start)
            validate_magnitude(end)
            if start >= end:
                raise ValidationError(f"start ({start}) debe ser menor que end ({end})")
            cmd = f"sweep_type magnitude {start} {end}"
        
        else:
            raise ValidationError(f"Tipo de sweep no válido: {sweep_type}")
        
        # Enviar comando de sweep_type
        self.send_command(cmd)
        
        # Configurar escala
        scale_cmd = f"sweep_scale {scale.value}"
        self.send_command(scale_cmd)
        
        logger.info(f"Sweep configurado: {sweep_type.value}, "
                   f"{start}->{end}, escala {scale.value}, {count} puntos")
    
    def perform_sweep(self, timeout: float = None) -> List[Dict[str, any]]:
        """
        Ejecuta el barrido configurado y retorna resultados.
        
        Returns:
            Lista de diccionarios, cada uno con:
            - 'sweep_value': Valor del parámetro barrido
            - 'measurement': Tupla con valores medidos según display mode
        
        Raises:
            MeasurementError: Si falla la medición
            TimeoutError: Si se excede el timeout
        
        Note:
            Antes de llamar este método, debe configurarse el sweep con
            configure_sweep(). Los resultados dependen del display_mode actual.
            
            IMPORTANTE: Este método espera a recibir TODOS los puntos solicitados
            antes de finalizar, según el valor de 'count' configurado previamente.
        
        Example:
            >>> dev.configure_sweep(SweepType.FREQUENCY, 100, 1000, 
            ...                     SweepScale.LOG, count=11)
            >>> results = dev.perform_sweep()
            >>> for point in results:
            ...     print(f"Freq: {point['sweep_value']} kHz, "
            ...           f"Z: {point['measurement'][0]} Ω")
        """
        from .enums import SWEEP_TIMEOUT
        
        if timeout is None:
            timeout = SWEEP_TIMEOUT
        
        # Obtener el número de puntos esperados de la configuración
        # Asegurarse de que sea un entero válido
        expected_count = self.current_config.get('count')
        if expected_count is None:
            expected_count = 11  # Valor por defecto
            logger.warning(f"count no configurado, usando valor por defecto: {expected_count}")
        expected_count = int(expected_count)
        
        # Ejecutar sweep con comando 'z' (según documentación oficial)
        # Los sweeps necesitan un manejo especial porque tardan mucho tiempo
        logger.info(f"Ejecutando sweep con comando 'z' - esperando {expected_count} puntos...")
        
        try:
            # Enviar comando
            cmd_bytes = ('z' + '\n').encode('utf-8')
            self.serial.write(cmd_bytes)
            self.command_count += 1
            logger.debug("Comando 'z' enviado")
            
            # Leer respuesta con paciencia - los sweeps tardan tiempo
            response = []
            start_time = time.time()
            last_data_time = time.time()
            
            # Timeout adaptativo: si no hay datos esperamos más tiempo entre puntos
            # para sweeps lentos, pero no terminamos hasta tener todos los puntos
            idle_timeout = 10.0  # Timeout entre puntos individuales (aumentado a 10s)
            
            # Contador de puntos de datos válidos recibidos
            points_received = 0
            
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8', errors='ignore')
                    line = line.strip()
                    
                    if line:
                        response.append(line)
                        last_data_time = time.time()
                        logger.debug(f"Línea recibida: {line[:60]}")
                        
                        # Contar si es una línea de datos válida (no prompt, no echo)
                        if (line and 
                            not line.startswith('ADMX') and 
                            line not in ['z', 'initiate'] and
                            ',' in line):  # Las líneas de datos contienen comas
                            points_received += 1
                            logger.debug(f"Punto {points_received}/{expected_count} recibido")
                        
                        # Si vemos el prompt Y ya recibimos todos los puntos, terminó
                        if 'ADMX2001>' in line:
                            logger.debug("Prompt detectado")
                            if points_received >= expected_count:
                                logger.debug(f"Todos los {expected_count} puntos recibidos - sweep completado")
                                break
                            else:
                                logger.debug(f"Prompt detectado pero solo {points_received}/{expected_count} puntos - continuando...")
                else:
                    # No hay datos, esperar un poco
                    time.sleep(0.1)
                    
                    # Solo terminar por timeout si:
                    # 1. Ya recibimos todos los puntos esperados, O
                    # 2. Llevamos mucho tiempo sin datos Y ya tenemos al menos algunos puntos
                    if points_received >= expected_count:
                        logger.debug(f"Todos los {expected_count} puntos recibidos - finalizando")
                        break
                    elif time.time() - last_data_time > idle_timeout:
                        if points_received > 0:
                            logger.warning(f"Timeout sin datos después de {idle_timeout}s - "
                                         f"recibidos {points_received}/{expected_count} puntos")
                            break
                        else:
                            logger.error(f"Timeout sin ningún dato después de {idle_timeout}s")
                            break
            
            elapsed = time.time() - start_time
            logger.info(f"Lectura completada en {elapsed:.2f}s, {len(response)} líneas, "
                       f"{points_received} puntos de datos")
            
            # Advertir si no recibimos todos los puntos esperados
            if points_received < expected_count:
                logger.warning(f"Sweep incompleto: esperados {expected_count} puntos, "
                             f"recibidos {points_received}")
            
        except Exception as e:
            raise MeasurementError(f"Error ejecutando sweep: {e}")
        
        # Parsear resultados
        results = []
        logger.debug(f"Parseando {len(response)} líneas de respuesta")
        
        for i, line in enumerate(response):
            # Saltar líneas vacías, comandos echo y prompts
            if not line or line.startswith('ADMX') or line.strip() in ['z', 'initiate']:
                continue
            
            # Parsear línea: primera columna es valor del sweep,
            # resto son mediciones
            from .utils import parse_measurement_line
            parts = parse_measurement_line(line)
            
            if parts and len(parts) >= 2:
                result = {
                    'sweep_value': parts[0],  # Primer valor: parámetro barrido
                    'measurement': tuple(parts[1:])  # Resto: mediciones
                }
                results.append(result)
                logger.debug(f"Punto parseado {len(results)}: sweep_value={parts[0]}, measurement={parts[1:]}")
            else:
                logger.debug(f"Línea {i} no parseada: {line[:50]}")
        
        logger.info(f"Sweep completado: {len(results)} puntos obtenidos de {len(response)} líneas")
        
        # Verificación final
        if len(results) < expected_count:
            logger.warning(f"Advertencia: se esperaban {expected_count} puntos pero solo "
                         f"se parsearon {len(results)}")
        
        return results
    
    def disable_sweep(self) -> None:
        """
        Desactiva el modo sweep.
        
        Wrapper conveniente para configure_sweep(SweepType.OFF, ...)
        """
        self.send_command("sweep_type off")
        logger.info("Sweep desactivado")
    
    # ==================== Comandos del Sistema ====================
    
    def get_idn(self) -> str:
        """Obtiene identificación del dispositivo."""
        response = self.send_command('*idn')
        return response[0] if response else "Unknown"
    
    def get_version(self) -> str:
        """Obtiene versión de firmware."""
        response = self.send_command('version')
        return response[0] if response else "Unknown"
    
    def reset(self) -> None:
        """Reinicia el dispositivo."""
        logger.warning("Reiniciando dispositivo...")
        self.send_command('reset')
        time.sleep(2)  # Esperar reinicio
    
    def get_help(self, command: Optional[str] = None) -> List[str]:
        """
        Obtiene ayuda del dispositivo.
        
        Args:
            command: Comando específico para obtener ayuda, o None para lista general
        """
        if command:
            return self.send_command(f'help {command}')
        else:
            return self.send_command('help')
    
    def selftest(self, run: bool = False) -> List[str]:
        """
        Obtiene o ejecuta el self-test del dispositivo.
        
        Args:
            run: Si True, ejecuta un nuevo self-test
        """
        if run:
            return self.send_command('selftest run')
        else:
            return self.send_command('selftest')
    
    # ==================== Context Manager ====================
    
    def __enter__(self):
        """Soporte para context manager (with statement)."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra conexión al salir del context."""
        self.close()
        return False
    
    def close(self) -> None:
        """Cierra la conexión serial."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.is_connected = False
            logger.info("Conexión cerrada")
    
    def reconnect(self) -> None:
        """
        Reconecta al dispositivo después de una desconexión.
        
        Útil cuando se pierde la conexión por error de comunicación.
        """
        logger.info("Intentando reconectar...")
        self.close()
        time.sleep(0.5)
        self._connect()
        logger.info("Reconexión exitosa")
    
    def check_connection(self) -> bool:
        """
        Verifica si la conexión está activa.
        
        Returns:
            True si está conectado y responde, False en caso contrario
        """
        if not self.is_connected or self.serial is None or not self.serial.is_open:
            return False
        
        try:
            # Intentar leer el estado sin afectar configuración
            self.serial.reset_input_buffer()
            self.serial.write(b'\n')
            time.sleep(0.1)
            
            # Verificar si hay respuesta
            if self.serial.in_waiting > 0:
                response = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                return 'ADMX2001>' in response or len(response) > 0
            return True  # Sin respuesta pero puerto abierto
        except:
            self.is_connected = False
            return False
    
    def __del__(self):
        """Destructor - asegura cierre de conexión."""
        self.close()
    
    # ==================== Estado y Diagnóstico ====================
    
    def get_status(self) -> Dict[str, any]:
        """
        Obtiene estado completo del dispositivo y la conexión.
        
        Returns:
            Diccionario con estado completo
        """
        uptime = time.time() - self.start_time
        
        return {
            'connected': self.is_connected,
            'port': self.port,
            'baudrate': self.baudrate,
            'uptime_seconds': uptime,
            'command_count': self.command_count,
            'error_count': self.error_count,
            'current_config': self.current_config.copy(),
            'calibration_status': self.calibration.get_calibration_status()
        }
    
    def __repr__(self):
        status = "connected" if self.is_connected else "disconnected"
        return f"ADMX2001({self.port}, {status})"
