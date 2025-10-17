#!/usr/bin/env python3
"""
Investigación profunda: ¿Cómo hacer que el método oficial funcione?
Según la documentación, un solo 'z' debería devolver TODOS los puntos del sweep.
"""

import serial
import time

port = '/dev/ttyUSB0'
ser = serial.Serial(port, 115200, timeout=5.0)
time.sleep(1)

def send_and_read(cmd, wait=0.5, read_timeout=30.0):
    """Envía comando y lee TODA la respuesta"""
    print(f"\n→ {cmd}")
    ser.write((cmd + '\n').encode())
    ser.flush()
    
    start_time = time.time()
    response = []
    
    # Leer TODO lo que llegue durante el timeout
    while (time.time() - start_time) < read_timeout:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                response.append(line)
                print(f"  ← {line[:80]}")
        else:
            time.sleep(0.05)
            # Si llevamos más de 2 segundos sin datos y ya tenemos algo, terminar
            if response and (time.time() - start_time) > 2.0:
                # Verificar si el último es el prompt
                if response and 'ADMX2001>' in response[-1]:
                    break
    
    return response

print("="*70)
print("INVESTIGACIÓN: Método oficial de sweeps")
print("="*70)

# Limpiar estado
ser.reset_input_buffer()
send_and_read('abort', wait=0.5, read_timeout=2.0)

print("\n" + "="*70)
print("TEST 1: Verificar configuración de 'average'")
print("="*70)
resp = send_and_read('average', read_timeout=2.0)
print(f"→ Configuración actual de average")

print("\n" + "="*70)
print("TEST 2: Configurar average a 1 (sin promediado)")
print("="*70)
send_and_read('average 1', read_timeout=2.0)

print("\n" + "="*70)
print("TEST 3: Configurar sweep pequeño (5 puntos)")
print("="*70)
send_and_read('count 5', read_timeout=2.0)
send_and_read('sweep_type frequency 1 10', read_timeout=2.0)
send_and_read('sweep_scale linear', read_timeout=2.0)

print("\n" + "="*70)
print("TEST 4: Verificar estado antes de 'z'")
print("="*70)
resp = send_and_read('count', read_timeout=2.0)
print(f"→ Count actual: {resp}")

print("\n" + "="*70)
print("TEST 5: Enviar 'z' y esperar TODOS los datos (30 segundos)")
print("="*70)
print("Esperando respuesta completa...")
response = send_and_read('z', read_timeout=30.0)

# Analizar respuesta
print("\n" + "="*70)
print("ANÁLISIS DE RESPUESTA")
print("="*70)
print(f"Total de líneas recibidas: {len(response)}")

# Contar líneas de datos
data_lines = []
for line in response:
    if ',' in line and not line.startswith('ADMX') and line not in ['z', 'abort']:
        try:
            parts = line.split(',')
            if len(parts) == 3:
                float(parts[0])
                float(parts[1])
                float(parts[2])
                data_lines.append(line)
        except:
            pass

print(f"Líneas de datos válidas: {len(data_lines)}")

if data_lines:
    print(f"\nPrimera línea de datos: {data_lines[0]}")
    if len(data_lines) > 1:
        print(f"Segunda línea de datos: {data_lines[1]}")
    if len(data_lines) > 2:
        print(f"Tercera línea de datos: {data_lines[2]}")
    if len(data_lines) > 3:
        print(f"...")
        print(f"Última línea de datos: {data_lines[-1]}")

print("\n" + "="*70)
print("TEST 6: Verificar si hay modo 'continuous' o similar")
print("="*70)
send_and_read('help sweep', read_timeout=5.0)

print("\n" + "="*70)
print("TEST 7: Probar con 'trig_mode'")
print("="*70)
send_and_read('trig_mode', read_timeout=2.0)

print("\n" + "="*70)
print("TEST 8: Ver comando 'initiate' con 'fetch' o 'read'")
print("="*70)
send_and_read('abort', read_timeout=2.0)
send_and_read('count 3', read_timeout=2.0)
send_and_read('sweep_type frequency 1 10', read_timeout=2.0)
send_and_read('sweep_scale linear', read_timeout=2.0)
print("\nEnviando 'initiate'...")
send_and_read('initiate', read_timeout=2.0)

print("\nEsperando 2 segundos y verificando buffer...")
time.sleep(2)
if ser.in_waiting > 0:
    print("¡Hay datos en el buffer!")
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(f"  ← {line[:80]}")
else:
    print("No hay datos en el buffer después de 'initiate'")

ser.close()
print("\n" + "="*70)
print("INVESTIGACIÓN COMPLETADA")
print("="*70)
