"""
Gestor de calibración para EVAL-ADMX2001.

Implementa el proceso completo de calibración según la documentación oficial,
incluyendo open, short y load calibration, con validaciones y verificaciones.
"""

import logging
import time
from typing import Optional, Dict, Tuple, List
from datetime import datetime

from .exceptions import CalibrationError, ValidationError
from .enums import GainChannel0, GainChannel1

logger = logging.getLogger(__name__)

# Valores recomendados por DOCUMENTACION_OFICIAL / wizard
CALIBRATION_AVERAGE = 200
CALIBRATION_TDELAY_MS = 200
DEFAULT_CALIBRATION_PASSWORD = "Analog123"


def _lines_from_password_buffer(text, password=None, omit_commands=()):
    """Extrae líneas útiles tras PASSWORD> (sin eco ni prompt)."""
    from .utils import clean_response_line, strip_serial_terminal_noise

    omit = {c.lower() for c in omit_commands if c}
    lines = []
    for raw in strip_serial_terminal_noise(text or '').replace('\r', '\n').split('\n'):
        line = clean_response_line(raw)
        if not line:
            continue
        low = line.lower()
        if password and line == password:
            continue
        if low.startswith('password>'):
            continue
        if low in omit:
            continue
        lines.append(line)
    return lines


def start_password_prompt_command(device, command, wait_timeout=8.0):
    """
    Envía un comando que solicita PASSWORD> y espera el prompt.

    Returns:
        (texto_crudo, prompt_recibido)
    """
    device.serial.reset_input_buffer()
    device.serial.reset_output_buffer()
    device.serial.write((command + '\n').encode('utf-8'))
    device.serial.flush()

    buffer = bytearray()
    start = time.time()
    got_prompt = False
    while (time.time() - start) < wait_timeout:
        if device.serial.in_waiting:
            buffer.extend(device.serial.read(device.serial.in_waiting))
            if 'PASSWORD>' in buffer.decode('utf-8', errors='ignore').upper():
                got_prompt = True
                time.sleep(0.05)
                if device.serial.in_waiting:
                    buffer.extend(device.serial.read(device.serial.in_waiting))
                break
        else:
            time.sleep(0.05)
    return buffer.decode('utf-8', errors='ignore'), got_prompt


def send_password_and_read(device, password, read_timeout=45.0):
    """
    Envía contraseña tras PASSWORD> y lee hasta resultado del firmware.

    El commit a flash puede tardar varios segundos sin enviar bytes; no cortar
    la lectura tras silencios breves.

    Returns:
        (lines, need_retry, success)
    """
    from .utils import strip_serial_terminal_noise

    device.serial.write((password + '\n').encode('utf-8'))
    device.serial.flush()

    buffer = bytearray()
    start = time.time()
    last_data = start
    no_data_limit = 10.0

    def _buffer_lower():
        return strip_serial_terminal_noise(
            buffer.decode('utf-8', errors='ignore')
        ).lower()

    while (time.time() - start) < read_timeout:
        if device.serial.in_waiting:
            buffer.extend(device.serial.read(device.serial.in_waiting))
            last_data = time.time()
        else:
            time.sleep(0.05)

        if not buffer:
            continue

        lower = _buffer_lower()
        if 'commit' in lower and 'success' in lower:
            time.sleep(0.1)
            if device.serial.in_waiting:
                buffer.extend(device.serial.read(device.serial.in_waiting))
            break
        if 'erase' in lower and 'success' in lower:
            time.sleep(0.1)
            if device.serial.in_waiting:
                buffer.extend(device.serial.read(device.serial.in_waiting))
            break
        if any(
            k in lower
            for k in ('invalid password', 'incorrect password', 'password invalid')
        ):
            time.sleep(0.1)
            if device.serial.in_waiting:
                buffer.extend(device.serial.read(device.serial.in_waiting))
            break

        idle = time.time() - last_data
        if idle > no_data_limit:
            break

    full_text = buffer.decode('utf-8', errors='ignore')
    lower = strip_serial_terminal_noise(full_text).lower()
    success = (
        ('commit' in lower and 'success' in lower)
        or ('erase' in lower and 'success' in lower)
    )
    need_retry = (
        not success
        and 'password>' in lower
        and not any(k in lower for k in ('invalid', 'incorrect', 'fail'))
    )
    lines = _lines_from_password_buffer(full_text, password=password)
    return lines, need_retry, success


def run_calibrate_commit_serial(
    device,
    password: Optional[str] = None,
    timestamp: Optional[int] = None,
) -> List[str]:
    """
    Ejecuta ``calibrate commit <ts>`` + PASSWORD> + contraseña (firmware ADMX2001).

    Usable desde terminal CLI sin estado del wizard.
    """
    if password is None:
        password = DEFAULT_CALIBRATION_PASSWORD

    parts = []
    if timestamp is not None:
        ts = int(float(timestamp))
        cmd = f"calibrate commit {ts}"
    else:
        ts = None
        cmd = "calibrate commit"

    logger.info(f"Commit calibración (cmd={cmd!r})...")

    first_text, got_prompt = start_password_prompt_command(device, cmd)
    if not got_prompt:
        raise CalibrationError(
            f"No se recibió PASSWORD> tras '{cmd}'. Respuesta: {first_text[:200]!r}"
        )

    lines, need_retry, success = send_password_and_read(device, password)
    if need_retry and not success:
        raise CalibrationError(
            "Contraseña rechazada o prompt expirado. "
            f"Respuesta: {' | '.join(lines) or first_text[:120]!r}"
        )
    if not lines and success:
        lines = ['commit : success']
    return lines


class CalibrationState:
    """
    Representa el estado de calibración para una configuración específica.
    
    Según documentación, cada combinación de (ch0_gain, ch1_gain, frequency)
    requiere calibración separada.
    """
    
    def __init__(self, ch0_gain: int, ch1_gain: int, frequency: float):
        self.ch0_gain = ch0_gain
        self.ch1_gain = ch1_gain
        self.frequency = frequency
        
        # Estados de calibración
        self.open_done = False
        self.short_done = False
        self.load_done = False
        
        # Valores de calibración
        self.load_r = None
        self.load_x = None
        
        # Metadata
        self.timestamp = None
        self.temperature = None
        
    def is_complete(self) -> bool:
        """Verifica si la calibración está completa (open + load mínimo)."""
        return self.open_done and self.load_done
    
    def __repr__(self):
        return (f"CalibrationState(ch0={self.ch0_gain}, ch1={self.ch1_gain}, "
                f"freq={self.frequency}Hz, open={self.open_done}, "
                f"short={self.short_done}, load={self.load_done})")


class CalibrationManager:
    """
    Gestiona todo el proceso de calibración del ADMX2001.
    
    Responsabilidades:
    - Guiar el proceso de calibración paso a paso
    - Validar condiciones antes de cada paso
    - Mantener registro de estados de calibración
    - Guardar y cargar calibraciones de la memoria flash
    
    La documentación especifica un proceso riguroso:
    1. Open calibration (conectores separados)
    2. Short calibration (todos los terminales juntos) - opcional para algunos gains
    3. Load calibration (resistencia conocida)
    4. Commit (guardar en flash con contraseña)
    
    Example:
        >>> cal_mgr = CalibrationManager(device)
        >>> cal_mgr.start_calibration_sequence(ch0_gain=0, ch1_gain=1, frequency=100000)
        >>> input("Coloque OPEN y presione Enter...")
        >>> cal_mgr.calibrate_open()
        >>> input("Coloque SHORT y presione Enter...")
        >>> cal_mgr.calibrate_short()
        >>> input("Coloque LOAD (1kΩ) y presione Enter...")
        >>> cal_mgr.calibrate_load(1000.019, 0.822)
        >>> cal_mgr.commit()
    """
    
    def __init__(self, device):
        """
        Inicializa el gestor de calibración.
        
        Args:
            device: Instancia de ADMX2001
        """
        self.device = device
        self.current_state: Optional[CalibrationState] = None
        self.calibration_history: List[CalibrationState] = []
        self.default_password = "Analog123"

    def _apply_calibration_measurement_setup(self) -> None:
        """
        Aplica promediado y retardo de trigger antes de cada medición OSL.

        La documentación exige ``average 200`` (y ``tdelay 200``) antes de
        calibrate open/short/rt.
        """
        from .utils import validate_average

        validate_average(CALIBRATION_AVERAGE)
        logger.info(
            f"Configurando medición de calibración: average={CALIBRATION_AVERAGE}, "
            f"tdelay={CALIBRATION_TDELAY_MS}ms"
        )
        self.device.send_command(f"average {CALIBRATION_AVERAGE}")
        self.device.send_command(f"tdelay {CALIBRATION_TDELAY_MS}")
        
    def start_calibration_sequence(self, ch0_gain: int, ch1_gain: int, 
                                   frequency: float, magnitude: float = 1.0) -> None:
        """
        Inicia una nueva secuencia de calibración.
        
        Configura el dispositivo y prepara el estado de calibración.
        
        Args:
            ch0_gain: Ganancia canal 0 (0-3)
            ch1_gain: Ganancia canal 1 (0-3)
            frequency: Frecuencia de calibración (Hz)
            magnitude: Magnitud de señal (Vpk)
        
        Raises:
            CalibrationError: Si no se puede iniciar la calibración
            ValidationError: Si los parámetros son inválidos
        """
        # Validar parámetros
        if ch0_gain not in [0, 1, 2, 3]:
            raise ValidationError(f"ch0_gain debe ser 0-3, recibido: {ch0_gain}")
        if ch1_gain not in [0, 1, 2, 3]:
            raise ValidationError(f"ch1_gain debe ser 0-3, recibido: {ch1_gain}")
        
        from .utils import validate_frequency, validate_magnitude
        validate_frequency(frequency)
        validate_magnitude(magnitude)
        
        logger.info(f"Iniciando calibración: ch0={ch0_gain}, ch1={ch1_gain}, "
                   f"freq={frequency}Hz, mag={magnitude}Vpk")
        
        # Desactivar autorange (requerido para calibración)
        self.device.send_command("setgain auto off")
        
        # Configurar parámetros
        self.device.send_command(f"setgain ch0 {ch0_gain}")
        self.device.send_command(f"setgain ch1 {ch1_gain}")
        self.device.send_command(f"frequency {frequency/1000}")  # En kHz
        self.device.send_command(f"magnitude {magnitude}")
        self.device.send_command("offset 0")

        self._apply_calibration_measurement_setup()

        # Crear nuevo estado de calibración
        self.current_state = CalibrationState(ch0_gain, ch1_gain, frequency)
        
        logger.info("Configuración de calibración completada")
        
    def calibrate_open(self) -> Dict[str, any]:
        """
        Ejecuta calibración OPEN.
        
        Instrucciones al usuario:
        - Conectar H_CUR con H_POT formando un par
        - Conectar L_CUR con L_POT formando otro par
        - Mantener ambos pares SEPARADOS
        - Si usa clips, cada clip debe sujetar un trozo pequeño de cable
        
        Returns:
            Diccionario con resultado de calibración
        
        Raises:
            CalibrationError: Si la calibración falla
        """
        if self.current_state is None:
            raise CalibrationError("Debe llamar start_calibration_sequence() primero")
        
        logger.info("Ejecutando calibración OPEN...")

        self._apply_calibration_measurement_setup()

        try:
            response = self.device.send_command("calibrate open", timeout=120.0)
            
            # Parsear respuesta
            result = self._parse_calibration_response(response)
            
            if "Done" in str(response) or result.get('success', False):
                self.current_state.open_done = True
                self.current_state.temperature = result.get('temperature')
                logger.info("Calibración OPEN completada exitosamente")
                return result
            else:
                raise CalibrationError(f"Calibración OPEN falló: {response}")
                
        except Exception as e:
            logger.error(f"Error en calibración OPEN: {e}")
            raise CalibrationError(f"Error en calibración OPEN: {e}")
    
    def calibrate_short(self) -> Dict[str, any]:
        """
        Ejecuta calibración SHORT.
        
        Instrucciones al usuario:
        - Conectar TODOS los terminales juntos (H_CUR, H_POT, L_CUR, L_POT)
        
        IMPORTANTE: Según documentación:
        - Solo posible cuando ch1_gain es 0 o 1
        - Si ch1_gain=1, magnitude debe ser < 0.2Vpk
        
        Returns:
            Diccionario con resultado de calibración
        
        Raises:
            CalibrationError: Si la calibración falla o no es posible
        """
        if self.current_state is None:
            raise CalibrationError("Debe llamar start_calibration_sequence() primero")
        
        # Verificar si short calibration es posible
        if self.current_state.ch1_gain > 1:
            logger.warning(
                f"Short calibration no recomendada con ch1_gain={self.current_state.ch1_gain}. "
                "Solo válida para gain 0 o 1"
            )
            raise CalibrationError(
                "Short calibration solo puede realizarse con ch1_gain 0 o 1"
            )
        
        # Si ch1_gain=1, verificar magnitude
        if self.current_state.ch1_gain == 1:
            # Reducir magnitude temporalmente
            logger.info("Reduciendo magnitude a 0.2Vpk para short calibration...")
            self.device.send_command("magnitude 0.2")
        
        logger.info("Ejecutando calibración SHORT...")

        self._apply_calibration_measurement_setup()

        try:
            response = self.device.send_command("calibrate short", timeout=120.0)
            
            # Parsear respuesta
            result = self._parse_calibration_response(response)
            
            if "Done" in str(response) or result.get('success', False):
                self.current_state.short_done = True
                logger.info("Calibración SHORT completada exitosamente")
                
                # Restaurar magnitude si fue reducida
                if self.current_state.ch1_gain == 1:
                    self.device.send_command("magnitude 1")
                
                return result
            else:
                raise CalibrationError(f"Calibración SHORT falló: {response}")
                
        except Exception as e:
            logger.error(f"Error en calibración SHORT: {e}")
            raise CalibrationError(f"Error en calibración SHORT: {e}")
    
    def calibrate_load(self, r_true: float, x_true: float) -> Dict[str, any]:
        """
        Ejecuta calibración LOAD con valores conocidos.
        
        Instrucciones al usuario:
        - Conectar resistencia/impedancia conocida entre los terminales
        
        Args:
            r_true: Resistencia real medida con LCR meter de referencia (Ohms)
            x_true: Reactancia real medida con LCR meter de referencia (Ohms)
        
        Note:
            Los valores r_true y x_true deben obtenerse de un instrumento
            calibrado (como Keysight E4980A) en el mismo modo Rs,Xs
            y a la misma frecuencia.
        
        Returns:
            Diccionario con resultado de calibración
        
        Raises:
            CalibrationError: Si la calibración falla
        """
        if self.current_state is None:
            raise CalibrationError("Debe llamar start_calibration_sequence() primero")
        
        if not self.current_state.open_done:
            logger.warning("Se recomienda hacer calibración OPEN antes de LOAD")
        
        logger.info(f"Ejecutando calibración LOAD con R={r_true}Ω, X={x_true}Ω...")

        self._apply_calibration_measurement_setup()

        try:
            from .utils import format_calibrate_load_command
            response = self.device.send_command(
                format_calibrate_load_command(r_true, x_true),
                timeout=120.0,
            )
            
            # Parsear respuesta
            result = self._parse_calibration_response(response)
            
            if "Done" in str(response) or result.get('success', False):
                self.current_state.load_done = True
                self.current_state.load_r = r_true
                self.current_state.load_x = x_true
                logger.info("Calibración LOAD completada exitosamente")
                return result
            else:
                raise CalibrationError(f"Calibración LOAD falló: {response}")
                
        except Exception as e:
            logger.error(f"Error en calibración LOAD: {e}")
            raise CalibrationError(f"Error en calibración LOAD: {e}")
    
    def commit(self, password: Optional[str] = None, 
              timestamp: Optional[int] = None) -> None:
        """
        Guarda la calibración actual en memoria flash.
        
        IMPORTANTE: Este paso es crítico. Sin commit, la calibración se
        pierde al apagar el dispositivo.
        
        Args:
            password: Contraseña de calibración (default: "Analog123")
            timestamp: Unix timestamp opcional (segundos desde 1970-01-01)
        
        Raises:
            CalibrationError: Si el commit falla o la calibración está incompleta
        """
        if self.current_state is None:
            raise CalibrationError("No hay calibración activa para guardar")
        
        if not self.current_state.is_complete():
            raise CalibrationError(
                "Calibración incompleta. Se requiere al menos OPEN y LOAD. "
                f"Estado actual: {self.current_state}"
            )
        
        if password is None:
            password = self.default_password

        try:
            ts = int(timestamp) if timestamp is not None else None
            lines = run_calibrate_commit_serial(
                self.device, password=password, timestamp=ts
            )
            final_response = "\n".join(lines)
            if "success" in final_response.lower():
                if ts is None:
                    ts = int(time.time())
                self.current_state.timestamp = ts
                self.calibration_history.append(self.current_state)
                logger.info(" Calibración guardada exitosamente en flash")
            else:
                raise CalibrationError(f"Commit falló. Respuesta: {final_response}")

        except CalibrationError:
            raise
        except Exception as e:
            logger.error(f"Error en commit: {e}")
            raise CalibrationError(f"Error guardando calibración: {e}")
    
    def list_calibrations(self) -> List[str]:
        """
        Lista todas las calibraciones guardadas en el dispositivo.
        
        Returns:
            Lista de strings con información de calibraciones
        """
        from zoria.lib.device_state import device_state

        if device_state.device is self.device and device_state.is_connected:
            return device_state.send_command(
                "calibrate list",
                timeout=30.0,
                lock_timeout=25.0,
                owner="calibration_ui",
            )
        response = self.device.send_command("calibrate list", timeout=30.0)
        return response

    def list_calibrations_at_frequency(self, freq_khz) -> List[str]:
        """Lista calibraciones para una frecuencia concreta (``calibrate list <kHz>``)."""
        from zoria.lib.calibration_parser import format_calibrate_list_khz

        cmd = f"calibrate list {format_calibrate_list_khz(freq_khz)}"
        from zoria.lib.device_state import device_state

        if device_state.device is self.device and device_state.is_connected:
            return device_state.send_command(
                cmd,
                timeout=30.0,
                lock_timeout=25.0,
                owner="calibration_ui",
            )
        return self.device.send_command(cmd, timeout=30.0)
    
    def reload_calibration(self) -> None:
        """
        Recarga la calibración desde flash.
        
        Útil después de cambiar configuración o reiniciar el dispositivo.
        """
        logger.info("Recargando calibración desde flash...")
        self.device.send_command("calibrate reload")
    
    def erase_all_calibrations(self, password: Optional[str] = None) -> None:
        """
        BORRA TODAS las calibraciones guardadas en flash.
        
        ADVERTENCIA: Esta operación no se puede deshacer.
        
        Args:
            password: Contraseña de calibración (default: "Analog123")
        
        Raises:
            CalibrationError: Si el borrado falla
        """
        if password is None:
            password = self.default_password
        
        logger.warning("BORRANDO TODAS LAS CALIBRACIONES - Esta acción no se puede deshacer")
        
        try:
            response = self.device.send_command("calibrate erase")
            time.sleep(0.5)
            
            # Enviar contraseña
            self.device.send_command(password, expect_prompt=False)
            time.sleep(0.5)
            
            logger.info("Calibraciones borradas")
            
        except Exception as e:
            raise CalibrationError(f"Error borrando calibraciones: {e}")
    
    def read_calibration_coefficients(self, ch0_gain: int, ch1_gain: int) -> Dict[str, float]:
        """
        Lee los coeficientes de calibración actuales para un gain específico.
        
        Args:
            ch0_gain: Ganancia canal 0
            ch1_gain: Ganancia canal 1
        
        Returns:
            Diccionario con coeficientes
        """
        response = self.device.send_command(f"rdcal {ch0_gain} {ch1_gain}")
        return self._parse_coefficients(response)
    
    def _parse_calibration_response(self, response: List[str]) -> Dict[str, any]:
        """
        Parsea la respuesta de un comando de calibración.
        
        Busca patrones como:
        - "open:Done"
        - "short:Done"
        - "load:Done"
        - "Cal Temp: XX.X deg C"
        - "Frequency = XXXX.XXXXkHz"
        """
        result = {
            'success': False,
            'raw_response': response,
            'temperature': None,
            'frequency': None
        }
        
        response_text = '\n'.join(response) if isinstance(response, list) else str(response)
        
        # Buscar "Done"
        if "Done" in response_text or "success" in response_text.lower():
            result['success'] = True
        
        # Buscar temperatura
        import re
        temp_match = re.search(r'Cal Temp:\s*([\d.]+)\s*deg C', response_text)
        if temp_match:
            result['temperature'] = float(temp_match.group(1))
        
        # Buscar frecuencia
        freq_match = re.search(r'Frequency\s*=\s*([\d.]+)kHz', response_text)
        if freq_match:
            result['frequency'] = float(freq_match.group(1)) * 1000  # Convertir a Hz
        
        return result
    
    def _parse_coefficients(self, response: List[str]) -> Dict[str, float]:
        """Parsea los coeficientes de calibración de la respuesta."""
        coefficients = {}
        
        for line in response:
            if '=' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    key = parts[0].strip()
                    try:
                        value = float(parts[1].strip())
                        coefficients[key] = value
                    except ValueError:
                        pass
        
        return coefficients
    
    def get_calibration_status(self) -> Dict[str, any]:
        """
        Obtiene el estado actual de calibración.
        
        Returns:
            Diccionario con información del estado
        """
        return {
            'active': self.current_state is not None,
            'current_state': self.current_state,
            'history_count': len(self.calibration_history),
            'last_calibration': self.calibration_history[-1] if self.calibration_history else None
        }
