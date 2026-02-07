#!/usr/bin/env python3
"""
Test script to identify the real format of 'calibrate list' command
from ADMX2001 hardware.
"""

import sys
import serial.tools.list_ports
from lib.admx2001 import ADMX2001

def find_admx_port():
    """Auto-detect ADMX2001 device port"""
    print("Buscando dispositivo ADMX2001...")
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        print(f"  Probando: {port.device} - {port.description}")
        try:
            device = ADMX2001(port.device, baudrate=115200, timeout=2)
            # Try to get ID to confirm it's ADMX2001
            response = device.send_command("*IDN?")
            if response and "ADMX" in response:
                print(f"✓ Dispositivo encontrado: {port.device}")
                print(f"  ID: {response}")
                return port.device
            device.close()
        except Exception as e:
            pass
    
    return None

def test_calibration_list():
    """Test 'calibrate list' command and show raw output"""
    
    # Find device
    port = find_admx_port()
    if not port:
        print("\n❌ No se encontró dispositivo ADMX2001")
        print("Asegúrate de que:")
        print("  1. El dispositivo está conectado por USB")
        print("  2. Tienes permisos para acceder al puerto serial")
        print("  3. Ninguna otra aplicación está usando el puerto")
        return False
    
    # Connect
    print(f"\nConectando a {port}...")
    device = ADMX2001(port, baudrate=115200, timeout=5)
    
    try:
        print("\n" + "="*60)
        print("COMANDO: calibrate list")
        print("="*60)
        
        # Execute command
        response = device.send_command("calibrate list")
        
        print(f"\nTIPO DE RESPUESTA: {type(response)}")
        print(f"LONGITUD: {len(response) if response else 0}")
        
        if response:
            print("\n--- RESPUESTA CRUDA ---")
            print(repr(response))
            
            print("\n--- RESPUESTA FORMATEADA ---")
            print(response)
            
            # If it's a list, show each element
            if isinstance(response, list):
                print(f"\n--- ELEMENTOS DE LA LISTA ({len(response)} elementos) ---")
                for idx, item in enumerate(response, 1):
                    print(f"[{idx}] {repr(item)}")
                    print(f"    → {item}")
            
            # Try to parse as expected format
            print("\n--- INTENTO DE PARSEO ---")
            if isinstance(response, list):
                for line in response:
                    try:
                        parts = line.strip().split()
                        parsed = {}
                        for part in parts:
                            if '=' in part:
                                key, value = part.split('=', 1)
                                parsed[key.upper()] = value
                        print(f"Parseado: {parsed}")
                    except Exception as e:
                        print(f"Error parseando '{line}': {e}")
            else:
                print(f"Respuesta no es lista, es: {type(response)}")
        else:
            print("❌ RESPUESTA VACÍA O NINGUNA")
        
        # Also try 'calibrate list' with example frequency
        print("\n" + "="*60)
        print("COMANDO: calibrate list 1000")
        print("="*60)
        
        response2 = device.send_command("calibrate list 1000")
        if response2:
            print("\n--- RESPUESTA ---")
            print(response2)
        else:
            print("❌ Sin respuesta (probablemente no hay calibración a 1000 Hz)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        device.close()
        print("\n✓ Conexión cerrada")

if __name__ == "__main__":
    print("="*60)
    print("TEST: Formato de salida de 'calibrate list'")
    print("="*60)
    
    success = test_calibration_list()
    
    if success:
        print("\n" + "="*60)
        print("✓ Test completado")
        print("="*60)
        print("\nAhora analiza la salida de arriba para:")
        print("  1. Confirmar el formato real del comando")
        print("  2. Ajustar el parseo en calibration_page.py si es necesario")
        sys.exit(0)
    else:
        print("\n❌ Test falló")
        sys.exit(1)
