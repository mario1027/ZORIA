#!/usr/bin/env python3
"""
Script de diagnóstico para analizar el parseo de comandos de calibración.
Muestra paso a paso cómo se procesan las respuestas del dispositivo.
"""
import sys
import logging
import re

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from lib.device_state import device_state
from lib import ADMX2001

def print_separator(title="", char="="):
    """Imprime un separador visual"""
    width = 70
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(f"\n{char * width}")

def test_calibration_command(command):
    """
    Testea un comando de calibración mostrando el procesamiento paso a paso.
    """
    print_separator(f"TEST: {command}", "=")
    
    if not device_state.is_connected or not device_state.device:
        print("❌ Dispositivo no conectado")
        return None
    
    print(f"\n📤 Enviando comando: '{command}'")
    
    try:
        # Enviar comando con timeout extendido
        response = device_state.send_command(command, timeout=30.0)
        
        print(f"\n📥 Respuesta recibida: {len(response) if response else 0} líneas")
        print_separator("LÍNEAS CRUDAS RECIBIDAS", "-")
        
        if response:
            for idx, line in enumerate(response):
                # Mostrar representación cruda
                print(f"  [{idx:2d}] {repr(line)}")
                # Mostrar versión limpia
                clean = line.strip()
                if clean != line:
                    print(f"       -> stripped: {repr(clean)}")
        else:
            print("  (respuesta None o vacía)")
        
        # Simular el procesamiento del terminal
        print_separator("PROCESAMIENTO TIPO TERMINAL", "-")
        
        if response:
            cleaned_lines = []
            
            for idx, line in enumerate(response):
                line_stripped = line.strip()
                
                print(f"\n  Línea {idx}: {repr(line)}")
                print(f"    stripped: {repr(line_stripped)}")
                
                # Saltar líneas completamente vacías
                if not line_stripped:
                    if command.startswith('calibrate') and cleaned_lines:
                        cleaned_lines.append("")
                        print(f"    ✓ Agregada como separador (calibrate + hay contenido previo)")
                    else:
                        print(f"    ✗ Saltada (vacía)")
                    continue
                
                # Filtrar eco: puede estar al inicio (líneas 0-1) o al final (última línea)
                is_first_lines = idx < 2
                is_last_line = idx == len(response) - 1
                
                if line_stripped.lower() == command.lower():
                    if is_first_lines:
                        print(f"    ✗ Saltada (eco del comando en líneas 0-1)")
                        continue
                    elif is_last_line:
                        print(f"    ✗ Saltada (eco del comando en última línea)")
                        continue
                
                # Agregar línea con contenido
                cleaned_lines.append(line_stripped)
                print(f"    ✓ AGREGADA a cleaned_lines")
            
            print_separator("LÍNEAS FINALES PROCESADAS", "-")
            print(f"\nTotal: {len(cleaned_lines)} líneas\n")
            
            if cleaned_lines:
                for idx, line in enumerate(cleaned_lines):
                    if line:
                        print(f"  [{idx:2d}] '{line}'")
                    else:
                        print(f"  [{idx:2d}] (separador vacío)")
            else:
                print("  (ninguna línea después del filtrado)")
            
            return cleaned_lines
        else:
            print("\n  Respuesta None o vacía desde el dispositivo")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_calibration_list_parsing(lines):
    """
    Testea el parseo específico de 'calibrate list'.
    """
    if not lines:
        print("\n❌ No hay líneas para parsear")
        return
    
    print_separator("PARSEO PARA TABLA DE CALIBRACIONES", "=")
    
    # Palabras clave inválidas
    invalid_keywords = ['idn', 'admx', 'firmware', 'hardware', 'error', 'command', 
                       'unknown', 'invalid', 'not found', 'failed']
    
    frequencies_with_configs = {}
    
    for idx, line in enumerate(lines):
        print(f"\n--- Procesando línea {idx}: '{line}' ---")
        
        if not line:
            print("  ✗ Línea vacía, saltando")
            continue
        
        if line.startswith('#'):
            print("  ✗ Línea de comentario (#), saltando")
            continue
        
        # Filtrar palabras clave inválidas
        line_lower = line.lower()
        invalid_found = [kw for kw in invalid_keywords if kw in line_lower]
        if invalid_found:
            print(f"  ✗ Contiene palabras inválidas: {invalid_found}")
            continue
        
        # Detectar formato
        has_equals = '=' in line
        print(f"  Contiene '=': {has_equals}")
        
        if has_equals:
            # Formato con clave=valor
            print("  → Formato: CLAVE=VALOR")
            
            parts = line.split()
            parsed_data = {}
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    parsed_data[key.upper()] = value
            
            print(f"  Datos parseados: {parsed_data}")
            
            freq = parsed_data.get('FREQ', parsed_data.get('FREQUENCY', None))
            ch0 = parsed_data.get('CH0', '?')
            ch1 = parsed_data.get('CH1', '?')
            
            if freq:
                try:
                    freq_value = float(freq)
                    print(f"  Frecuencia: {freq_value} Hz")
                    
                    # Validar rango
                    if freq_value < 0.2 or freq_value > 10000000:
                        print(f"  ✗ Frecuencia fuera de rango (0.2 Hz - 10 MHz)")
                        continue
                    else:
                        print(f"  ✓ Frecuencia válida")
                except ValueError:
                    print(f"  ✗ Frecuencia no numérica: {freq}")
                    continue
                
                if freq not in frequencies_with_configs:
                    frequencies_with_configs[freq] = []
                frequencies_with_configs[freq].append({
                    'ch0': ch0,
                    'ch1': ch1,
                    'raw': line
                })
                print(f"  ✓ AGREGADA: FREQ={freq}, CH0={ch0}, CH1={ch1}")
            else:
                print(f"  ✗ No se encontró frecuencia en los datos")
        else:
            # Formato simple: solo frecuencia
            print("  → Formato: SOLO FRECUENCIA")
            
            # Regex estricto
            freq_match = re.search(r'^(\d+\.?\d*)\s*(Hz|kHz|MHz)?$', line, re.IGNORECASE)
            
            if freq_match:
                freq_value = float(freq_match.group(1))
                unit = freq_match.group(2) if freq_match.group(2) else 'Hz'
                
                print(f"  Match: {freq_value} {unit}")
                
                # Convertir a Hz
                if unit.lower() == 'khz':
                    freq_value *= 1000
                elif unit.lower() == 'mhz':
                    freq_value *= 1000000
                
                print(f"  Frecuencia en Hz: {freq_value}")
                
                # Validar rango
                if freq_value < 0.2 or freq_value > 10000000:
                    print(f"  ✗ Frecuencia fuera de rango (0.2 Hz - 10 MHz)")
                    continue
                
                freq_str = str(int(freq_value))
                if freq_str not in frequencies_with_configs:
                    frequencies_with_configs[freq_str] = []
                if not frequencies_with_configs[freq_str]:
                    frequencies_with_configs[freq_str] = [{'placeholder': True}]
                
                print(f"  ✓ AGREGADA: {freq_str} Hz (placeholder)")
            else:
                print(f"  ✗ No coincide con regex de frecuencia")
                print(f"     Regex esperada: ^(\\d+\\.?\\d*)\\s*(Hz|kHz|MHz)?$")
    
    print_separator("RESULTADO FINAL", "-")
    print(f"\nFrecuencias encontradas: {len(frequencies_with_configs)}")
    
    if frequencies_with_configs:
        for freq, configs in sorted(frequencies_with_configs.items(),
                                   key=lambda x: float(x[0]) if x[0].isdigit() else 0):
            print(f"\n  FREQ={freq} Hz:")
            for config in configs:
                if config.get('placeholder'):
                    print(f"    - (sin configuraciones específicas)")
                else:
                    print(f"    - CH0={config.get('ch0')}, CH1={config.get('ch1')}")
                    print(f"      Raw: {config.get('raw')}")
    else:
        print("  (ninguna frecuencia válida)")

def main():
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO DE PARSEO DE CALIBRACIÓN")
    print("=" * 70)
    
    # Listar puertos
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ No se encontraron puertos serie")
        return 1
    
    print("\n📡 Puertos disponibles:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    
    # Seleccionar puerto
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
    else:
        port_name = None
        for port in ports:
            if 'USB' in port.description or 'ACM' in port.device:
                port_name = port.device
                break
        if not port_name:
            port_name = ports[0].device
    
    print(f"\n🔌 Usando puerto: {port_name}")
    
    try:
        # Conectar creando instancia de ADMX2001
        print("📡 Creando instancia ADMX2001...")
        device = ADMX2001(port_name, baudrate=115200, timeout=5.0)
        device_state.set_device(device, True)
        
        if not device_state.is_connected:
            print("❌ No se pudo conectar")
            return 1
        
        print("✅ Conectado exitosamente\n")
        
        # Menú interactivo
        while True:
            print("\n" + "=" * 70)
            print("MENÚ DE OPCIONES:")
            print("  1. Testear 'calibrate list'")
            print("  2. Testear 'calibrate open'")
            print("  3. Testear 'calibrate short'")
            print("  4. Testear comando personalizado")
            print("  5. Salir")
            print("=" * 70)
            
            choice = input("\nSeleccione opción (1-5): ").strip()
            
            if choice == '1':
                lines = test_calibration_command("calibrate list")
                if lines:
                    test_calibration_list_parsing(lines)
            elif choice == '2':
                test_calibration_command("calibrate open")
            elif choice == '3':
                test_calibration_command("calibrate short")
            elif choice == '4':
                cmd = input("Ingrese comando: ").strip()
                if cmd:
                    test_calibration_command(cmd)
            elif choice == '5':
                break
            else:
                print("Opción inválida")
        
        # Desconectar
        if device_state.device:
            device_state.device.disconnect()
        device_state.set_device(None, False)
        print("\n✅ Desconectado")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por usuario")
        if device_state.device:
            device_state.device.disconnect()
        device_state.set_device(None, False)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
