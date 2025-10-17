#!/usr/bin/env python3
"""
Secuencia completa de sweep con trigger
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
print("SECUENCIA COMPLETA: abort → config → initiate → trigger por punto")
print("="*70)

# Limpiar y configurar
ser.reset_input_buffer()
send('abort')
send('count 5')  # 5 puntos
send('sweep_type frequency 1 100')  # 1 kHz a 100 kHz
send('sweep_scale linear')

print("\n" + "="*70)
print("Enviando 'initiate' para preparar sweep...")
print("="*70)
send('initiate', wait=1.0)

print("\n" + "="*70)
print("Enviando 'trigger' para cada punto del sweep...")
print("="*70)

points = []
for i in range(5):
    print(f"\n--- Punto {i+1}/5 ---")
    response = send('trigger', wait=1.5)
    
    # Buscar línea con datos (formato: freq,real,imag)
    for line in response:
        if line and not line.startswith('ADMX') and not line.startswith('Error') and not line.startswith('Warn'):
            parts = line.split(',')
            if len(parts) == 3:
                try:
                    freq = float(parts[0])
                    real = float(parts[1])
                    imag = float(parts[2])
                    points.append((freq, real, imag))
                    print(f"  ✓ Datos: freq={freq:.1f} Hz, Z=({real:.2f}, {imag:.2f})")
                except:
                    pass

print("\n" + "="*70)
print(f"RESULTADO: {len(points)}/5 puntos recibidos")
print("="*70)

if len(points) == 5:
    print("\n✓✓✓ SWEEP COMPLETO ✓✓✓")
    print("\nDatos recibidos:")
    for i, (f, r, im) in enumerate(points, 1):
        print(f"  {i}. {f:.1f} Hz → Z = {r:.2f} + j{im:.2f}")
else:
    print(f"\n✗ Sweep incompleto: solo {len(points)}/5 puntos")

ser.close()
