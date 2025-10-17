#!/usr/bin/env python3
"""
Optimizando el método oficial: 
Parece que SÍ llegan múltiples puntos, pero necesitamos leerlos mejor
"""

import serial
import time

port = '/dev/ttyUSB0'
ser = serial.Serial(port, 115200, timeout=0.5)  # Timeout corto para no bloquearse
time.sleep(1)

def send_command(cmd):
    """Solo envía el comando"""
    print(f"\n→ {cmd}")
    ser.write((cmd + '\n').encode())
    ser.flush()

def read_all_sweep_data(expected_points, max_wait=60.0):
    """Lee TODOS los datos del sweep con paciencia"""
    print(f"\n🔄 Leyendo datos del sweep (esperando {expected_points} puntos)...")
    
    all_lines = []
    data_lines = []
    start_time = time.time()
    last_data_time = time.time()
    
    while (time.time() - start_time) < max_wait:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    all_lines.append(line)
                    last_data_time = time.time()
                    
                    # Mostrar línea recibida
                    if len(all_lines) % 10 == 0 or ',' in line:
                        print(f"  [{len(data_lines)+1}] ← {line[:70]}")
                    
                    # Verificar si es línea de datos
                    if ',' in line and not line.startswith('ADMX') and line not in ['z', 'abort']:
                        try:
                            parts = line.split(',')
                            if len(parts) == 3:
                                float(parts[0])
                                float(parts[1]) 
                                float(parts[2])
                                data_lines.append(line)
                                print(f"  ✓ Punto {len(data_lines)}/{expected_points}")
                        except:
                            pass
                    
                    # Detectar prompt
                    if 'ADMX2001>' in line:
                        print(f"  → Prompt detectado con {len(data_lines)}/{expected_points} puntos")
                        # Si ya tenemos todos los puntos, terminar
                        if len(data_lines) >= expected_points:
                            print(f"  ✓ Todos los {expected_points} puntos recibidos!")
                            break
                        # Si no, esperar un poco más por si llegan más datos
                        time.sleep(0.5)
                        if ser.in_waiting == 0:
                            print(f"  → No hay más datos en buffer")
                            break
            except Exception as e:
                print(f"  ⚠ Error leyendo línea: {e}")
        else:
            # No hay datos, esperar
            time.sleep(0.05)
            
            # Timeout si llevamos mucho sin datos
            if (time.time() - last_data_time) > 5.0:
                if len(data_lines) > 0:
                    print(f"  ⏸ Timeout (5s sin datos) - recibidos {len(data_lines)}/{expected_points}")
                    break
                elif (time.time() - start_time) > 10.0:
                    print(f"  ✗ Timeout (10s sin ningún dato)")
                    break
    
    elapsed = time.time() - start_time
    print(f"\n📊 Resumen: {len(data_lines)}/{expected_points} puntos en {elapsed:.2f}s")
    return data_lines, all_lines

print("="*70)
print("OPTIMIZACIÓN: Método oficial con lectura mejorada")
print("="*70)

# Limpiar
ser.reset_input_buffer()
ser.reset_output_buffer()
send_command('abort')
time.sleep(0.5)
ser.readline()  # Leer respuesta de abort

print("\n" + "="*70)
print("Configurando sweep de 10 puntos")
print("="*70)
send_command('average 1')
time.sleep(0.3); ser.read_all()

send_command('count 10')
time.sleep(0.3); ser.read_all()

send_command('sweep_type frequency 1 100')
time.sleep(0.3); ser.read_all()

send_command('sweep_scale linear')
time.sleep(0.3); ser.read_all()

print("\n" + "="*70)
print("Enviando comando 'z' y leyendo TODO")
print("="*70)

send_command('z')
time.sleep(0.5)  # Dar tiempo al dispositivo

# Leer TODOS los datos
data_lines, all_lines = read_all_sweep_data(expected_points=10, max_wait=60.0)

# Mostrar resultados
print("\n" + "="*70)
print("RESULTADOS")
print("="*70)
print(f"Total líneas recibidas: {len(all_lines)}")
print(f"Líneas de datos: {len(data_lines)}/10")

if data_lines:
    print(f"\nPrimeros 3 puntos:")
    for i, line in enumerate(data_lines[:3], 1):
        parts = line.split(',')
        print(f"  {i}. freq={float(parts[0]):.1f} Hz, R={float(parts[1]):.2e}, X={float(parts[2]):.2e}")
    
    if len(data_lines) > 3:
        print(f"\nÚltimos 3 puntos:")
        for i, line in enumerate(data_lines[-3:], len(data_lines)-2):
            parts = line.split(',')
            print(f"  {i}. freq={float(parts[0]):.1f} Hz, R={float(parts[1]):.2e}, X={float(parts[2]):.2e}")

if len(data_lines) == 10:
    print("\n✓✓✓ MÉTODO OFICIAL FUNCIONA ✓✓✓")
    print("Un solo comando 'z' devolvió todos los puntos!")
else:
    print(f"\n⚠ Incompleto: {len(data_lines)}/10 puntos")
    print("Posibles causas:")
    print("  - Datos se generan más lento de lo esperado")
    print("  - Necesitamos esperar más tiempo entre puntos")
    print("  - Buffer serial se está llenando")

ser.close()
print("\n" + "="*70)
print("PRUEBA COMPLETADA")
print("="*70)
