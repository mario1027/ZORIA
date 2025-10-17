#!/usr/bin/env python3
"""
Script de prueba RAW para identificar el comando correcto de sweep
Este script prueba diferentes comandos directamente en el puerto serial
"""

import serial
import serial.tools.list_ports
import time

def find_admx2001_port():
    """Busca el puerto del ADMX2001"""
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        print(f"Puerto encontrado: {port.device} - {port.description}")
        if 'USB' in port.description or 'ACM' in port.device or 'USB' in port.device:
            return port.device
    return None

def test_raw_commands():
    """Prueba comandos raw en el dispositivo"""
    
    print("="*70)
    print("PRUEBA RAW DE COMANDOS SERIAL")
    print("="*70)
    
    # Encontrar puerto
    port = find_admx2001_port()
    if not port:
        print("✗ No se encontró el dispositivo")
        return
    
    print(f"\n✓ Puerto encontrado: {port}")
    
    # Abrir puerto
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=2.0)
        print("✓ Puerto abierto")
    except Exception as e:
        print(f"✗ Error abriendo puerto: {e}")
        return
    
    time.sleep(1)
    
    # Limpiar buffer
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    print("✓ Buffers limpiados")
    
    # Función para enviar comando y leer respuesta
    def send_and_read(cmd, wait_time=1.0, max_lines=20):
        print(f"\n{'─'*70}")
        print(f"Enviando: '{cmd}'")
        ser.write((cmd + '\n').encode('utf-8'))
        ser.flush()
        time.sleep(wait_time)
        
        lines = []
        while ser.in_waiting > 0 and len(lines) < max_lines:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                lines.append(line)
                print(f"  ← {line[:100]}")
        
        if not lines:
            print("  (sin respuesta)")
        
        return lines
    
    # 1. Verificar conexión con *idn
    print("\n" + "="*70)
    print("1. VERIFICAR CONEXIÓN")
    print("="*70)
    send_and_read('*idn')
    
    # 2. Configurar sweep simple
    print("\n" + "="*70)
    print("2. CONFIGURAR SWEEP SIMPLE")
    print("="*70)
    send_and_read('count 5')  # Solo 5 puntos para prueba rápida
    send_and_read('sweep_type frequency 1 10')  # 1-10 kHz
    send_and_read('sweep_scale linear')
    
    # 3. Intentar diferentes comandos de ejecución
    print("\n" + "="*70)
    print("3. PROBAR COMANDOS DE EJECUCIÓN")
    print("="*70)
    
    commands_to_test = [
        ('initiate', 10.0, 50),  # Comando completo, esperar 10s, leer hasta 50 líneas
        ('z', 10.0, 50),          # Shortcut
        ('start', 5.0, 50),       # Alternativa
        ('run', 5.0, 50),         # Alternativa
        ('execute', 5.0, 50),     # Alternativa
        ('sweep', 5.0, 50),       # Alternativa
    ]
    
    for cmd, wait, max_lines in commands_to_test:
        print(f"\n{'='*70}")
        print(f"Probando comando: '{cmd}'")
        print(f"{'='*70}")
        
        # Limpiar antes de cada prueba
        ser.reset_input_buffer()
        time.sleep(0.2)
        
        lines = send_and_read(cmd, wait_time=wait, max_lines=max_lines)
        
        # Analizar respuesta
        data_lines = [l for l in lines if ',' in l and not l.startswith('ADMX')]
        
        if data_lines:
            print(f"\n✓✓✓ ÉXITO CON '{cmd}' ✓✓✓")
            print(f"    Recibidas {len(data_lines)} líneas de datos:")
            for i, line in enumerate(data_lines[:3]):
                print(f"    [{i+1}] {line[:80]}")
            if len(data_lines) > 3:
                print(f"    ... y {len(data_lines) - 3} más")
            break
        else:
            print(f"✗ '{cmd}' no produjo datos")
    else:
        print("\n✗✗✗ NINGÚN COMANDO FUNCIONÓ ✗✗✗")
    
    # Cerrar puerto
    ser.close()
    print("\n✓ Puerto cerrado")
    
    print("\n" + "="*70)
    print("PRUEBA COMPLETADA")
    print("="*70)

if __name__ == "__main__":
    print("""
    Este script prueba diferentes comandos directamente en el puerto serial
    para identificar cuál comando ejecuta el sweep correctamente.
    
    REQUISITOS:
    - Dispositivo ADMX2001 conectado
    - Muestra conectada (resistor simple sirve)
    
    El script probará:
    1. initiate (comando estándar SCPI)
    2. z (shortcut documentado)
    3. start, run, execute, sweep (alternativas)
    """)
    
    input("Presione ENTER para comenzar...")
    
    try:
        test_raw_commands()
    except KeyboardInterrupt:
        print("\n\n⚠ Prueba cancelada")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
