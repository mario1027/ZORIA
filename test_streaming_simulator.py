#!/usr/bin/env python3
"""
Script de prueba para simular y testear el streaming del terminal ADMX2001
Sin necesidad de hardware real.
"""

import io
import time
import threading
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimulatedSerialPort:
    """Simula el puerto serial del ADMX2001"""
    
    def __init__(self):
        self.buffer = io.BytesIO()
        self.write_pos = 0
        self.read_pos = 0
        self._lock = threading.Lock()
        
    def write(self, data):
        """Simula escribir al puerto (enviar comando)"""
        with self._lock:
            logger.info(f"[SIM] Comando enviado: {data.decode('utf-8').strip()}")
            
            # Simular respuesta del dispositivo según el comando
            cmd = data.decode('utf-8').strip()
            
            if cmd == 'z':
                # Simular respuesta con eco y datos
                response = "z\r\n"  # Eco del comando
                response += "0,5.677640e-13,8.062763e+07\r\n"
                response += "1,5.668012e-13,8.305672e+07\r\n"
                response += "2,5.675237e-13,8.208995e+07\r\n"
                response += "3,5.673763e-13,8.276912e+07\r\n"
                response += "4,5.683635e-13,8.463327e+07\r\n"
                response += "5,5.677640e-13,8.062763e+07\r\n"
                response += "6,5.668012e-13,8.305672e+07\r\n"
                response += "7,5.675237e-13,8.208995e+07\r\n"
                response += "8,5.673763e-13,8.276912e+07\r\n"
                response += "9,5.683635e-13,8.463327e+07\r\n"
                response += "\x1b[1mADMX2001>\x1b[0m "  # Prompt con códigos ANSI
                
                # Simular envío gradual (como hardware real)
                def send_gradually():
                    time.sleep(0.05)  # Simular latencia inicial
                    for chunk in [response[i:i+50] for i in range(0, len(response), 50)]:
                        time.sleep(0.02)  # Simular latencia entre chunks
                        self.buffer.write(chunk.encode('utf-8'))
                        self.write_pos += len(chunk)
                
                thread = threading.Thread(target=send_gradually, daemon=True)
                thread.start()
            
            elif cmd.startswith('display'):
                response = "Measurement model: 0 - Equivalent series capacitance and resistance (Cs,Rs)\r\nADMX2001> "
                self.buffer.write(response.encode('utf-8'))
                self.write_pos += len(response)
    
    def flush(self):
        """No-op para compatibilidad"""
        pass
    
    @property
    def in_waiting(self):
        """Retorna cantidad de bytes disponibles para leer"""
        with self._lock:
            available = self.write_pos - self.read_pos
            return max(0, available)
    
    def read(self, size):
        """Lee bytes del buffer"""
        with self._lock:
            self.buffer.seek(self.read_pos)
            data = self.buffer.read(size)
            self.read_pos += len(data)
            return data


class SimulatedADMX2001:
    """Simula el dispositivo ADMX2001"""
    
    def __init__(self):
        self.serial = SimulatedSerialPort()


def test_streaming_logic():
    """Prueba la lógica de streaming con dispositivo simulado"""
    
    print("\n" + "="*60)
    print("INICIANDO TESTS DE STREAMING - SIMULACIÓN ADMX2001")
    print("="*60 + "\n")
    
    # Crear dispositivo simulado
    device = SimulatedADMX2001()
    
    # Importar regex para códigos ANSI
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Test 1: Comando simple 'z' con count 10
    print("\n📝 TEST 1: Comando 'z' con 10 líneas de datos")
    print("-" * 60)
    
    command = 'z'
    device.serial.write((command + '\n').encode('utf-8'))
    
    response_buffer = ""
    line_count = 0
    cmd_echo = command.strip()
    first_line_processed = False
    prompt_seen = False
    lines_received = []
    
    start_time = time.time()
    max_time = 5.0  # 5 segundos para test
    
    time.sleep(0.1)  # Breve pausa inicial
    
    print(f"⏳ Esperando respuesta para comando '{cmd_echo}'...")
    
    while True:
        if time.time() - start_time > max_time:
            print(f"❌ TIMEOUT después de {line_count} líneas")
            break
        
        if device.serial.in_waiting > 0:
            chunk = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
            print(f"📦 Chunk recibido ({len(chunk)} bytes): {repr(chunk[:100])}")
            response_buffer += chunk
            
            # Detectar prompt en el chunk O en el buffer (puede no tener \n después)
            if 'ADMX2001>' in response_buffer:
                print(f"⏹️ Prompt detectado en buffer")
                prompt_seen = True
            
            # Procesar líneas completas
            while '\n' in response_buffer:
                line, response_buffer = response_buffer.split('\n', 1)
                
                # Limpiar códigos ANSI
                line_clean = ansi_escape.sub('', line).strip()
                
                print(f"🔍 Línea procesada: '{line_clean[:80]}'")
                
                # PRIMERA LÍNEA: Filtrar eco
                if not first_line_processed:
                    first_line_processed = True
                    if line_clean == cmd_echo:
                        print(f"✂️ Eco exacto detectado y filtrado: '{line_clean}'")
                        continue
                    elif line_clean.startswith(cmd_echo):
                        line_clean = line_clean[len(cmd_echo):].strip()
                        print(f"✂️ Eco removido del inicio: '{line_clean[:60]}'")
                        if not line_clean:
                            continue
                
                # Si la línea contiene el prompt, limpiarla
                if 'ADMX2001>' in line_clean:
                    print(f"⏹️ Prompt encontrado en línea - removiendo")
                    line_clean = line_clean.replace('ADMX2001>', '').strip()
                
                # Agregar línea
                if line_clean:
                    line_count += 1
                    lines_received.append(line_clean)
                    print(f"✅ Línea {line_count}: '{line_clean[:60]}'")
            
            # Si vimos el prompt, salir
            if prompt_seen:
                print(f"🏁 Finalizando - Total de líneas: {line_count}")
                break
        else:
            time.sleep(0.05)
    
    # Verificar resultados
    print("\n" + "="*60)
    print("RESULTADOS DEL TEST")
    print("="*60)
    print(f"✓ Líneas recibidas: {line_count}")
    print(f"✓ Líneas esperadas: 10")
    print(f"✓ Prompt detectado: {'SÍ' if prompt_seen else 'NO'}")
    
    if line_count == 10 and prompt_seen:
        print("\n✅ TEST EXITOSO - Streaming funciona correctamente")
    else:
        print(f"\n❌ TEST FALLIDO")
        if line_count != 10:
            print(f"   - Se esperaban 10 líneas pero se recibieron {line_count}")
        if not prompt_seen:
            print(f"   - No se detectó el prompt de finalización")
    
    print("\n📋 Líneas recibidas:")
    for i, line in enumerate(lines_received, 1):
        print(f"   {i}: {line}")
    
    # Test 2: Segunda ejecución (verificar reset)
    print("\n\n📝 TEST 2: Segunda ejecución del comando 'z'")
    print("-" * 60)
    
    # Resetear buffer del dispositivo simulado
    device.serial.buffer = io.BytesIO()
    device.serial.write_pos = 0
    device.serial.read_pos = 0
    
    # Ejecutar nuevamente
    device.serial.write((command + '\n').encode('utf-8'))
    
    response_buffer = ""
    line_count_2 = 0
    first_line_processed = False
    prompt_seen = False
    lines_received_2 = []
    
    start_time = time.time()
    time.sleep(0.1)
    
    while True:
        if time.time() - start_time > max_time:
            print(f"❌ TIMEOUT después de {line_count_2} líneas")
            break
        
        if device.serial.in_waiting > 0:
            chunk = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
            response_buffer += chunk
            
            # Detectar prompt en buffer
            if 'ADMX2001>' in response_buffer:
                prompt_seen = True
            
            while '\n' in response_buffer:
                line, response_buffer = response_buffer.split('\n', 1)
                line_clean = ansi_escape.sub('', line).strip()
                
                if not first_line_processed:
                    first_line_processed = True
                    if line_clean == cmd_echo or line_clean.startswith(cmd_echo):
                        continue
                
                if 'ADMX2001>' in line_clean:
                    line_clean = line_clean.replace('ADMX2001>', '').strip()
                
                if line_clean:
                    line_count_2 += 1
                    lines_received_2.append(line_clean)
            
            if prompt_seen:
                break
        else:
            time.sleep(0.05)
    
    print(f"✓ Segunda ejecución - Líneas: {line_count_2}, Prompt: {'SÍ' if prompt_seen else 'NO'}")
    
    if line_count_2 == 10 and prompt_seen:
        print("✅ Segunda ejecución EXITOSA")
    else:
        print(f"❌ Segunda ejecución FALLIDA")
    
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    if line_count == 10 and line_count_2 == 10 and prompt_seen:
        print("✅ TODOS LOS TESTS EXITOSOS")
        print("   - Primera ejecución: OK")
        print("   - Segunda ejecución: OK")
        print("   - Filtrado de eco: OK")
        print("   - Detección de prompt: OK")
        return True
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        return False


if __name__ == '__main__':
    success = test_streaming_logic()
    exit(0 if success else 1)
