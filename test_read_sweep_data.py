#!/usr/bin/env python3
"""
Prueba para ver cómo obtener datos después de initiate
"""

import serial
import time

port = '/dev/ttyUSB0'
ser = serial.Serial(port, 115200, timeout=5.0)
time.sleep(1)

def send(cmd, wait=0.5):
    print(f"\n→ {cmd}")
    ser.write((cmd + '\n').encode())
    ser.flush()
    time.sleep(wait)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(f"  ← {line}")

print("="*70)
print("PRUEBA: ¿Cómo obtener datos después de initiate?")
print("="*70)

# Limpiar y configurar
ser.reset_input_buffer()
send('abort')
send('count 3')  # Solo 3 puntos para rápido
send('sweep_type frequency 1 10')
send('sweep_scale linear')

print("\n" + "="*70)
print("Enviando 'initiate' y esperando...")
print("="*70)
send('initiate', wait=5.0)  # Esperar 5 segundos

print("\n" + "="*70)
print("¿Hay datos en el buffer?")
print("="*70)
print(f"Bytes disponibles: {ser.in_waiting}")

if ser.in_waiting > 0:
    print("Leyendo todo lo disponible...")
    for i in range(20):
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"  [{i}] {line}")
        else:
            break
else:
    print("No hay datos disponibles")
    print("\nProbando comandos para leer datos:")
    commands = ['read', 'fetch', 'data', 'result', 'output', '*trg', 'trigger', 'z']
    for cmd in commands:
        print(f"\n→ Probando '{cmd}'...")
        send(cmd, wait=2.0)

ser.close()
print("\n✓ Prueba completada")
