#!/usr/bin/env python3
"""
Script de prueba directa de comandos de calibración
para ver exactamente qué responde el dispositivo.
"""

import sys
import serial

def test_calibration_commands():
    """Prueba comandos de calibración directamente"""
    
    port = '/dev/ttyUSB1'
    
    print("="*70)
    print("PRUEBA DIRECTA DE COMANDOS DE CALIBRACIÓN")
    print("="*70)
    
    try:
        # Conectar
        ser = serial.Serial(port, 115200, timeout=3)
        print(f"\n✓ Conectado a {port}\n")
        
        # Limpiar buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        commands = [
            "*IDN?",
            "calibrate list",
            "help",
        ]
        
        for cmd in commands:
            print(f"\n{'='*70}")
            print(f"COMANDO: {cmd}")
            print(f"{'='*70}")
            
            # Enviar comando
            ser.write(f"{cmd}\r\n".encode('utf-8'))
            print(f"→ Enviado: {cmd}")
            
            # Esperar y leer respuesta
            import time
            time.sleep(0.5)
            
            response_lines = []
            timeout_start = time.time()
            
            while time.time() - timeout_start < 2:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        response_lines.append(line)
                        print(f"← {line}")
                        timeout_start = time.time()  # Reset timeout
                time.sleep(0.05)
            
            if not response_lines:
                print("← (Sin respuesta)")
            
            print(f"\nTotal líneas recibidas: {len(response_lines)}")
        
        ser.close()
        print("\n✓ Prueba completada")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calibration_commands()
