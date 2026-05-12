"""
Estado global compartido del dispositivo ADMX2001.
Permite que todas las páginas accedan al dispositivo conectado.
"""
import threading
import time
import logging

logger = logging.getLogger(__name__)

class DeviceState:
    """Singleton para mantener el estado del dispositivo"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._device = None
                    cls._instance._is_connected = threading.Event()
                    cls._instance._callbacks = []
                    cls._instance._last_check = 0
                    cls._instance._port_info = None
                    cls._instance._connection_errors = 0
                    cls._instance._operation_lock = threading.Lock()  # Lock para operaciones de I/O
                    # Streaming de comandos en tiempo real
                    cls._instance._streaming_buffer = []  # Buffer de líneas que van llegando
                    cls._instance._streaming_lock = threading.Lock()
                    cls._instance._command_in_progress = False
                    cls._instance._streaming_complete = threading.Event()
                    cls._instance._stop_requested = threading.Event()
                    cls._instance._stop_requested_at = None
                    # Buffer de streaming para sweeps (puntos de gráfico)
                    cls._instance._sweep_buffer = []  # Buffer de puntos (freq, z_real, z_imag, z_mag, phase)
                    cls._instance._sweep_lock = threading.Lock()
                    cls._instance._sweep_in_progress = False
                    cls._instance._sweep_total_points = 0
                    cls._instance._sweep_current_point = 0
        return cls._instance
    
    @property
    def device(self):
        return self._device
    
    @property
    def is_connected(self):
        return self._is_connected.is_set()
    
    @property
    def port_info(self):
        """Devuelve información del puerto (ej: /dev/ttyUSB0, COM3)"""
        return self._port_info
    
    def set_device(self, device, connected=False):
        """Establece el dispositivo y notifica a los listeners"""
        self._device = device
        if connected:
            self._is_connected.set()
            self._connection_errors = 0
            # Guardar información del puerto
            if device and hasattr(device, 'port'):
                self._port_info = device.port
            else:
                self._port_info = None
        else:
            self._is_connected.clear()
            self._port_info = None
        
        # Notificar callbacks registrados
        for callback in self._callbacks:
            try:
                callback(device, connected)
            except Exception as e:
                logger.error(f"Error en callback de estado: {e}")
    
    def register_callback(self, callback):
        """Registra un callback para cambios de estado"""
        self._callbacks.append(callback)
    
    def verify_connection(self, force=False):
        """
        Verifica activamente si el dispositivo sigue conectado y respondiendo.
        
        Args:
            force: Si True, fuerza verificación inmediata sin importar caché
            
        Returns:
            tuple: (is_connected: bool, status_message: str, port: str)
        """
        # Caché de verificación (no verificar más de una vez por segundo)
        now = time.time()
        if not force and (now - self._last_check) < 1.0:
            return (self._is_connected.is_set(), 
                    "Conectado" if self._is_connected.is_set() else "Desconectado",
                    self._port_info)
        
        # Intentar obtener el lock - si hay otra operación en curso, usar estado cacheado
        if not self._operation_lock.acquire(blocking=False):
            # Hay otra operación en curso (ej: sweep), retornar estado actual sin verificar
            return (self._is_connected.is_set(), 
                    "Conectado" if self._is_connected.is_set() else "Desconectado",
                    self._port_info)
        
        try:
            self._last_check = now
            
            # Si no hay dispositivo, claramente no está conectado
            if not self._device:
                if self._is_connected.is_set():
                    logger.warning("Estado inconsistente: marcado como conectado pero sin dispositivo")
                    self._is_connected.clear()
                return False, "Desconectado", None
            
            # Verificar si el dispositivo responde con un comando simple
            try:
                # Verificar si el puerto serial sigue abierto
                if hasattr(self._device, 'serial') and hasattr(self._device.serial, 'is_open'):
                    if not self._device.serial.is_open:
                        logger.warning("Puerto serial cerrado, desconectando...")
                        self._is_connected.clear()
                        self._connection_errors += 1
                        return False, "Puerto cerrado", self._port_info
                
                # Verificación rápida: enviar un comando simple
                # Usar timeout corto para no bloquear el monitor
                response = self._device.send_command('*idn')
                logger.debug(f"[Monitor] *idn respuesta: {len(response) if response else 0} líneas")
                
                if response and len(response) > 0:
                    # Dispositivo responde correctamente
                    if not self._is_connected.is_set():
                        logger.info("Dispositivo reconectado")
                        self._is_connected.set()
                    self._connection_errors = 0
                    return True, "Conectado", self._port_info
                else:
                    # No hay respuesta
                    logger.warning("Dispositivo no responde a *idn")
                    self._connection_errors += 1
                    if self._connection_errors >= 5:
                        logger.error("Múltiples errores de conexión, marcando como desconectado")
                        self._is_connected.clear()
                        return False, "Sin respuesta", self._port_info
                    return True, "Conexión débil", self._port_info
                    
            except Exception as e:
                logger.error(f"Error verificando conexión: {e}")
                self._connection_errors += 1
                
                # Después de varios errores, marcar como desconectado
                if self._connection_errors >= 5:
                    logger.error("Múltiples errores, marcando como desconectado")
                    self._is_connected.clear()
                    return False, f"Error: {str(e)[:50]}", self._port_info
                
                return self._is_connected.is_set(), "Error de comunicación", self._port_info
        
        finally:
            self._operation_lock.release()
    
    def send_command(self, command, timeout=None, lock_timeout=90.0):
        """
        Envía un comando al dispositivo si está conectado.
        
        Args:
            command: Comando a enviar
            timeout: Timeout opcional para este comando (en segundos)
        """
        if not self._device or not self._is_connected.is_set():
            raise ConnectionError("Dispositivo no conectado")

        # Si hay streaming activo, solicitar stop antes de enviar otro comando
        cmd_lower = (command or "").strip().lower()
        if cmd_lower and cmd_lower != 'stop' and self._command_in_progress:
            self.stop_streaming_command(wait_timeout=3.0)
        
        # Usar lock para evitar comandos simultáneos
        # Timeout muy largo (90s) para dar tiempo a comandos lentos + overhead
        # (comandos pueden tardar hasta 60s con averaging alto)
        if not self._operation_lock.acquire(blocking=True, timeout=lock_timeout):
            raise TimeoutError("No se pudo obtener acceso al dispositivo (ocupado)")
        
        try:
            logger.info(f"[DeviceState] >>> Enviando: '{command}'")
            
            # Pasar timeout al dispositivo si se especificó
            if timeout:
                response = self._device.send_command(command, timeout=timeout)
            else:
                response = self._device.send_command(command)
                
            logger.info(f"[DeviceState] <<< Respuesta: {len(response) if response else 0} líneas")
            # Log de las primeras líneas para debug
            if response:
                for i, line in enumerate(response[:5]):
                    logger.info(f"[DeviceState]     Línea {i}: '{line.strip()}'")
                if len(response) > 5:
                    logger.info(f"[DeviceState]     ... y {len(response)-5} líneas más")
            self._connection_errors = 0  # Reset en comando exitoso
            return response
        except Exception as e:
            self._connection_errors += 1
            if self._connection_errors >= 3:
                logger.error("Múltiples errores de comando, verificar conexión")
                self._is_connected.clear()
            raise e
        finally:
            self._operation_lock.release()
    
    def start_streaming_command(self, command, timeout=None):
        """
        Inicia un comando en modo streaming.
        Las líneas se van agregando al buffer a medida que llegan.
        """
        if not self._device or not self._is_connected.is_set():
            raise ConnectionError("Dispositivo no conectado")
        
        # Limpiar buffer anterior
        with self._streaming_lock:
            self._streaming_buffer.clear()
            self._command_in_progress = True
            self._streaming_complete.clear()
            self._stop_requested.clear()
            self._stop_requested_at = None
        
        # Iniciar comando en un thread separado
        def _execute_streaming():
            try:
                if not self._operation_lock.acquire(blocking=True, timeout=30.0):
                    with self._streaming_lock:
                        self._streaming_buffer.append({
                            'type': 'error',
                            'line': 'No se pudo obtener acceso al dispositivo (ocupado)'
                        })
                        self._command_in_progress = False
                        self._streaming_complete.set()
                    return
                
                try:
                    logger.info(f"[Streaming] >>> Iniciando: '{command}'")
                    
                    # Enviar comando
                    device = self._device
                    cmd_bytes = (command + '\n').encode('utf-8')
                    device.serial.write(cmd_bytes)
                    device.serial.flush()
                    
                    start_time = time.time()
                    max_time = timeout or 30.0
                    response_buffer = ""
                    line_count = 0
                    cmd_echo = command.strip()
                    first_line_processed = False
                    prompt_seen = False
                    
                    # Regex para códigos ANSI - captura TODOS los tipos
                    import re
                    # Matches: CSI, OSC, y single-character escapes (including VT100 escapes like ESC 7, ESC 8)
                    ansi_escape = re.compile(r'''
                        \x1B  # ESC
                        (?:   # Opciones:
                            [0-9@-_]  # Single character escapes (includes digits for VT100 codes)
                        |
                            \[[0-?]*[ -/]*[@-~]  # CSI sequences
                        |
                            \][^\a]*(?:\a|\x1b\\)  # OSC sequences
                        )
                    ''', re.VERBOSE)
                    
                    logger.info(f"[Streaming] Esperando datos del comando '{cmd_echo}'...")
                    time.sleep(0.1)  # Breve pausa inicial
                    
                    while True:
                        # Timeout global
                        if time.time() - start_time > max_time:
                            # Solo reportar timeout si NO vimos el prompt (no terminamos correctamente)
                            if not prompt_seen:
                                logger.error(f"[Streaming] ⏱ Timeout global después de {line_count} líneas (sin ver prompt)")
                                with self._streaming_lock:
                                    self._streaming_buffer.append({
                                        'type': 'error',
                                        'line': f'⏱ Timeout: esperaba prompt después de {line_count} líneas'
                                    })
                            break
                        
                        # Leer datos disponibles
                        if device.serial.in_waiting > 0:
                            chunk = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
                            logger.info(f"[Streaming]  Chunk ({len(chunk)} bytes): {repr(chunk[:200])}")
                            response_buffer += chunk
                            
                            # Detectar prompt EN EL BUFFER (puede no tener \n después)
                            if 'ADMX2001>' in response_buffer:
                                logger.info(f"[Streaming] ⏹ Prompt detectado en el buffer")
                                prompt_seen = True
                            
                            # Procesar líneas completas
                            while '\n' in response_buffer:
                                line, response_buffer = response_buffer.split('\n', 1)
                                
                                # Limpiar códigos ANSI y espacios
                                line_clean = ansi_escape.sub('', line).strip()
                                
                                logger.info(f"[Streaming]  Procesando línea: '{line_clean[:100]}'")
                                
                                # PRIMERA LÍNEA: Filtrar eco del comando
                                if not first_line_processed:
                                    first_line_processed = True
                                    # Caso 1: Línea completa es el eco
                                    if line_clean == cmd_echo:
                                        logger.info(f"[Streaming]  Eco exacto detectado y filtrado: '{line_clean}'")
                                        continue
                                    # Caso 2: Línea empieza con el eco (sin salto de línea después del eco)
                                    elif line_clean.startswith(cmd_echo):
                                        line_clean = line_clean[len(cmd_echo):].strip()
                                        logger.info(f"[Streaming]  Eco removido del inicio, línea resultante: '{line_clean[:80]}'")
                                        # Si después de remover el eco queda vacío, continuar
                                        if not line_clean:
                                            continue
                                
                                # Si la línea contiene el prompt, removerlo pero continuar procesando
                                if 'ADMX2001>' in line_clean:
                                    logger.info(f"[Streaming] Removiendo prompt de línea: '{line_clean[:100]}'")
                                    line_clean = line_clean.replace('ADMX2001>', '').strip()
                                
                                # Agregar línea al buffer si tiene contenido
                                if line_clean:
                                    with self._streaming_lock:
                                        self._streaming_buffer.append({
                                            'type': 'data',
                                            'line': line_clean,
                                            'index': line_count
                                        })
                                    line_count += 1
                                    logger.info(f"[Streaming]  Línea {line_count} agregada: '{line_clean[:80]}'")
                                else:
                                    # Log líneas vacías para debugging
                                    logger.warning(f"[Streaming]  Línea vacía detectada y OMITIDA (después de limpieza). Línea original: {repr(line)}")
                            
                            # Si vimos el prompt, procesar buffer restante ANTES de salir
                            if prompt_seen and response_buffer:
                                buffer_clean = ansi_escape.sub('', response_buffer).strip()
                                buffer_clean = buffer_clean.replace('ADMX2001>', '').strip()
                                if buffer_clean:
                                    with self._streaming_lock:
                                        self._streaming_buffer.append({
                                            'type': 'data',
                                            'line': buffer_clean,
                                            'index': line_count
                                        })
                                    line_count += 1
                                    logger.info(f"[Streaming]  Línea final {line_count} agregada desde buffer restante")
                                logger.info(f"[Streaming]  Finalizado correctamente - Total: {line_count} líneas")
                                break

                        # Si se pidió detener, salir cuando no haya datos pendientes
                        if self._stop_requested.is_set() and self._stop_requested_at:
                            if time.time() - self._stop_requested_at > 1.5:
                                logger.info("[Streaming]  Stop solicitado - timeout de salida")
                                break
                        if self._stop_requested.is_set() and device.serial.in_waiting == 0:
                            logger.info("[Streaming]  Stop solicitado - finalizando lectura")
                            break
                        else:
                            # No hay datos, esperar
                            time.sleep(0.05)
                    
                    self._connection_errors = 0
                    
                except Exception as e:
                    logger.error(f"[Streaming] Error: {e}")
                    with self._streaming_lock:
                        self._streaming_buffer.append({
                            'type': 'error',
                            'line': str(e)
                        })
                    self._connection_errors += 1
                finally:
                    self._operation_lock.release()
            finally:
                with self._streaming_lock:
                    self._command_in_progress = False
                    self._streaming_complete.set()
                logger.info("[Streaming] Comando completado")
        
        # Iniciar thread
        thread = threading.Thread(target=_execute_streaming, daemon=True)
        thread.start()
    
    def get_streaming_lines(self):
        """
        Obtiene nuevas líneas del buffer de streaming y las elimina del buffer.
        Retorna lista de diccionarios con 'type' y 'line'.
        """
        with self._streaming_lock:
            lines = self._streaming_buffer.copy()
            self._streaming_buffer.clear()
            if lines:
                logger.info(f"[Streaming GET] Recuperando {len(lines)} líneas del buffer")
            return lines
    
    def is_streaming_in_progress(self):
        """Retorna True si hay un comando en progreso."""
        return self._command_in_progress
    
    def is_streaming_complete(self):
        """Retorna True si el comando de streaming ha terminado."""
        return self._streaming_complete.is_set()

    def stop_streaming_command(self, wait_timeout=3.0):
        """
        Solicita detener el streaming enviando 'stop' y espera finalización.
        Retorna True si el streaming terminó dentro del timeout.
        """
        if not self._command_in_progress or not self._device:
            return True

        self._stop_requested.set()
        self._stop_requested_at = time.time()

        try:
            # Enviar varios 'stop' para asegurar que el dispositivo lo reciba
            try:
                self._device.serial.write(b'abort\n')
                self._device.serial.flush()
                time.sleep(0.05)
            except Exception as e:
                logger.warning(f"[Streaming] No se pudo enviar abort: {e}")
            for _ in range(3):
                self._device.serial.write(b'stop\n')
                self._device.serial.flush()
                time.sleep(0.05)
        except Exception as e:
            logger.warning(f"[Streaming] No se pudo enviar stop: {e}")

        stopped = self._streaming_complete.wait(timeout=wait_timeout)
        if not stopped:
            logger.warning("[Streaming] Stop solicitado pero no finalizó a tiempo")
        return stopped
    
    # ===== MÉTODOS PARA STREAMING DE SWEEP =====
    
    def clear_sweep_buffer(self):
        """Limpia el buffer de sweep sin cambiar el estado."""
        with self._sweep_lock:
            self._sweep_buffer.clear()
            logger.info("[Sweep] Buffer limpiado")
    
    def start_sweep_streaming(self, total_points):
        """Inicia el streaming de un sweep."""
        with self._sweep_lock:
            self._sweep_buffer.clear()
            self._sweep_in_progress = True
            self._sweep_total_points = total_points
            self._sweep_current_point = 0
    
    def rollback_sweep_points(self, n: int):
        """
        Elimina los últimos N puntos del buffer de sweep.
        Útil para revertir puntos parciales antes de reintentar un segmento
        que falló por saturación ADC.
        """
        with self._sweep_lock:
            if n > 0:
                removed = min(n, len(self._sweep_buffer))
                if removed > 0:
                    del self._sweep_buffer[-removed:]
                    self._sweep_current_point = max(0, self._sweep_current_point - removed)
                    logger.info(f"[Sweep] Rollback: revertidos {removed} puntos parciales del buffer")

    def add_sweep_point(self, freq, z_real, z_imag, z_mag, phase):
        """Agrega un punto al buffer de streaming del sweep."""
        with self._sweep_lock:
            self._sweep_buffer.append({
                'freq': freq,
                'z_real': z_real,
                'z_imag': z_imag,
                'z_mag': z_mag,
                'phase': phase,
                'index': self._sweep_current_point
            })
            self._sweep_current_point += 1
            # Log cada 10 puntos para no saturar
            if self._sweep_current_point % 10 == 0 or self._sweep_current_point == 1:
                logger.info(f"[Sweep Buffer] Punto {self._sweep_current_point}/{self._sweep_total_points} agregado ({len(self._sweep_buffer)} en buffer)")
    
    def get_sweep_points(self):
        """Obtiene nuevos puntos del buffer sweep y los elimina."""
        with self._sweep_lock:
            points = self._sweep_buffer.copy()
            self._sweep_buffer.clear()
            if points:
                logger.info(f"[Sweep GET] Recuperando {len(points)} puntos del buffer")
            return points
    
    def get_sweep_progress(self):
        """Retorna progreso del sweep como (current, total, percentage)."""
        with self._sweep_lock:
            pct = int((self._sweep_current_point / self._sweep_total_points) * 100) if self._sweep_total_points > 0 else 0
            return (self._sweep_current_point, self._sweep_total_points, pct)
    
    def end_sweep_streaming(self):
        """Finaliza el streaming del sweep."""
        with self._sweep_lock:
            self._sweep_in_progress = False
    
    def is_sweep_in_progress(self):
        """Retorna True si hay un sweep en progreso."""
        return self._sweep_in_progress

# Instancia global
device_state = DeviceState()    
