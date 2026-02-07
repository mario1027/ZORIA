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
            response = self._device.send_command('*idn')
            
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
    
    def send_command(self, command):
        """Envía un comando al dispositivo si está conectado"""
        if self._device and self._is_connected.is_set():
            try:
                return self._device.send_command(command)
            except Exception as e:
                self._connection_errors += 1
                if self._connection_errors >= 3:
                    logger.error("Múltiples errores de comando, verificar conexión")
                    self._is_connected.clear()
                raise e
        else:
            raise ConnectionError("Dispositivo no conectado")

# Instancia global
device_state = DeviceState()
