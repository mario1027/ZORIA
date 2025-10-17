#!/usr/bin/env python3
"""
Probando diferentes métodos para obtener múltiples puntos
"""

import serial
import time

port = '/dev/ttyUSB0'
ser = serial.Serial(port, 115200, timeout=5.0)
time.sleep(1)

def send(cmd, wait=0.5):
    ser.write((cmd + '\n').encode())
    ser.flush()
    time.sleep(wait)
    response = []
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            response.append(line)
    return response

def try_method(name, setup_cmds, read_cmd, count=3):
    print("\n" + "="*70)
    print(f"MÉTODO: {name}")
    print("="*70)
    
    ser.reset_input_buffer()
    send('abort')
    
    for cmd in setup_cmds:
        print(f"→ {cmd}")
        resp = send(cmd, wait=0.5)
        for line in resp:
            print(f"  ← {line}")
    
    print(f"\nObteniendo {count} puntos con '{read_cmd}':")
    points = 0
    for i in range(count):
        print(f"\n  Punto {i+1}/{count}:")
        resp = send(read_cmd, wait=1.5)
        got_data = False
        for line in resp:
            print(f"    ← {line}")
            if ',' in line and not line.startswith('ADMX') and not line.startswith('Error') and not line.startswith('Warn'):
                try:
                    parts = line.split(',')
                    if len(parts) == 3:
                        float(parts[0])
                        got_data = True
                        points += 1
                except:
                    pass
        if not got_data:
            break
    
    print(f"\n  → Resultado: {points}/{count} puntos")
    return points

print("="*70)
print("PRUEBA DE DIFERENTES MÉTODOS PARA MÚLTIPLES PUNTOS")
print("="*70)

# Método 1: initiate una vez, z múltiples veces
try_method(
    "initiate una vez, luego z por cada punto",
    ['count 3', 'sweep_type frequency 1 10', 'sweep_scale linear', 'initiate'],
    'z',
    count=3
)

# Método 2: Sin initiate, solo z
try_method(
    "Solo z (sin initiate)",
    ['count 3', 'sweep_type frequency 1 10', 'sweep_scale linear'],
    'z',
    count=3
)

# Método 3: initiate + trigger
try_method(
    "initiate, luego trigger por cada punto",
    ['count 3', 'sweep_type frequency 1 10', 'sweep_scale linear', 'initiate'],
    'trigger',
    count=3
)

# Método 4: z después de cada trigger
print("\n" + "="*70)
print("MÉTODO: initiate, alternando trigger/z")
print("="*70)
ser.reset_input_buffer()
send('abort')
send('count 3')
send('sweep_type frequency 1 10')
send('sweep_scale linear')
send('initiate')

points = 0
for i in range(3):
    print(f"\n  Punto {i+1}/3 con 'trigger':")
    resp = send('trigger', wait=1.5)
    for line in resp:
        print(f"    ← {line}")
        if ',' in line and not line.startswith('ADMX'):
            try:
                parts = line.split(',')
                if len(parts) == 3:
                    float(parts[0])
                    points += 1
            except:
                pass
    
    if i < 2:  # No en el último
        print(f"  Enviando 'initiate' de nuevo...")
        send('initiate', wait=0.5)

print(f"\n  → Resultado: {points}/3 puntos")

ser.close()
print("\n" + "="*70)
print("PRUEBA COMPLETADA")
print("="*70)
