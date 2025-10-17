#!/usr/bin/env python3
"""
Script para identificar la secuencia de inicialización correcta
El problema es "Invalid command for the state" - necesitamos poner el dispositivo en el estado correcto
"""

import serial
import serial.tools.list_ports
import time

def find_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'USB' in port.description or 'USB' in port.device:
            return port.device
    return None

def test_initialization():
    print("="*70)
    print("PRUEBA DE SECUENCIA DE INICIALIZACIÓN")
    print("="*70)
    
    port = find_port()
    if not port:
        print("✗ No se encontró dispositivo")
        return
    
    print(f"✓ Puerto: {port}")
    
    ser = serial.Serial(port, baudrate=115200, timeout=2.0)
    time.sleep(1)
    
    def send(cmd):
        print(f"\n→ {cmd}")
        ser.write((cmd + '\n').encode())
        ser.flush()
        time.sleep(0.5)
        lines = []
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                lines.append(line)
                print(f"  ← {line}")
        return lines
    
    # Limpiar
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    print("\n" + "="*70)
    print("PASO 1: INTENTAR RESET/INIT")
    print("="*70)
    
    # Probar diferentes comandos de inicialización
    init_commands = ['reset', '*rst', 'init', 'initialize', 'abort', 'stop', 'idle', 'mode idle']
    
    for cmd in init_commands:
        print(f"\n{'─'*70}")
        print(f"Probando: {cmd}")
        resp = send(cmd)
        time.sleep(0.5)
        
        # Después de cada init, probar *idn
        print("  Verificando con *idn:")
        idn_resp = send('*idn')
        
        # Si *idn funciona, este comando de init funcionó
        if any('Warn' not in line and 'ADMX' not in line and line != '*idn' for line in idn_resp):
            print(f"\n✓✓✓ POSIBLE SOLUCIÓN: '{cmd}' permite comandos después ✓✓✓")
            
            # Probar configurar sweep
            print("\n  Probando configurar sweep después de '{}'...".format(cmd))
            send('count 5')
            send('sweep_type frequency 1 10')
            send('sweep_scale linear')
            resp = send('initiate')
            
            if resp and any(',' in line for line in resp):
                print(f"\n✓✓✓ ¡SWEEP FUNCIONA DESPUÉS DE '{cmd}'! ✓✓✓")
                break
    
    print("\n" + "="*70)
    print("PASO 2: PROBAR COMANDOS DE MODO/ESTADO")
    print("="*70)
    
    mode_commands = [
        'mode measure',
        'mode sweep', 
        'state measure',
        'state sweep',
        'select sweep',
        'select measure'
    ]
    
    for cmd in mode_commands:
        print(f"\n{'─'*70}")
        resp = send(cmd)
        if resp and 'not found' not in str(resp).lower():
            print(f"  → '{cmd}' reconocido, probando sweep...")
            send('count 5')
            send('sweep_type frequency 1 10')
            resp = send('initiate')
            if resp and any(',' in line for line in resp):
                print(f"\n✓✓✓ SWEEP FUNCIONA CON '{cmd}'! ✓✓✓")
                break
    
    print("\n" + "="*70)
    print("PASO 3: PROBAR HELP PARA VER COMANDOS DISPONIBLES")
    print("="*70)
    
    print("\nComandos 'help':")
    send('help')
    
    print("\nComandos 'help sweep':")
    send('help sweep')
    
    ser.close()
    print("\n✓ Prueba completada")

if __name__ == "__main__":
    try:
        test_initialization()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
