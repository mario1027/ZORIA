#!/usr/bin/env python3
"""
Prueba siguiendo EXACTAMENTE la documentación oficial
"""

import serial
import time

port = '/dev/ttyUSB0'
ser = serial.Serial(port, 115200, timeout=5.0)
time.sleep(1)

def send(cmd, wait=0.5):
    print(f"→ {cmd}")
    ser.write((cmd + '\n').encode())
    ser.flush()
    time.sleep(wait)
    response = []
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(f"  ← {line}")
            response.append(line)
    return response

print("="*70)
print("PRUEBA SEGÚN DOCUMENTACIÓN OFICIAL")
print("="*70)

ser.reset_input_buffer()
send('abort')

print("\n--- Configuración EXACTA de la documentación ---")
send('count 5')
send('sweep_type frequency 1 100')  # 1 kHz a 100 kHz
send('sweep_scale linear')

print("\n--- Método 1: Solo 'z' (según documentación) ---")
print("Enviando 'z' y esperando TODOS los datos...")
send('z', wait=30.0)  # Esperar 30 segundos

# Leer cualquier cosa que quede en el buffer
print("\nLeyendo buffer restante...")
time.sleep(2)
remaining = []
while ser.in_waiting > 0:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line:
        print(f"  [extra] ← {line}")
        remaining.append(line)

print(f"\n→ Total de líneas recibidas después de 'z': {len(remaining)}")

print("\n" + "="*70)
print("--- Método 2: Usando 'tcount' + 'initiate' + 'trigger' ---")
print("="*70)

ser.reset_input_buffer()
send('abort')
send('count 5')
send('sweep_type frequency 1 100')
send('sweep_scale linear')
send('tcount 5')  # Trigger count = número de puntos

print("\nEnviando 'initiate' para entrar en modo trigger...")
send('initiate', wait=1.0)

print("\nEnviando 'trigger' para cada punto...")
points = []
for i in range(5):
    print(f"\n  Punto {i+1}/5:")
    resp = send('trigger', wait=2.0)
    for line in resp:
        if ',' in line and not line.startswith('ADMX'):
            try:
                parts = line.split(',')
                if len(parts) == 3:
                    float(parts[0])
                    points.append(line)
                    print(f"    ✓ Datos: {line[:60]}...")
            except:
                pass

print(f"\n→ Total de puntos recibidos: {len(points)}/5")

print("\n" + "="*70)
print("--- Método 3: Usando 'tcount' + solo 'z' ---")
print("="*70)

ser.reset_input_buffer()
send('abort')
send('count 5')
send('sweep_type frequency 1 100')
send('sweep_scale linear')
send('tcount 5')

print("\nEnviando 'z' con tcount configurado...")
resp = send('z', wait=30.0)

# Buscar líneas de datos
data_lines = []
for line in resp:
    if ',' in line and not line.startswith('ADMX') and line != 'z':
        try:
            parts = line.split(',')
            if len(parts) == 3:
                float(parts[0])
                data_lines.append(line)
                print(f"  ✓ {line[:60]}...")
        except:
            pass

print(f"\n→ Total de puntos: {len(data_lines)}/5")

ser.close()
print("\n" + "="*70)
print("PRUEBA COMPLETADA")
print("="*70)
