#!/usr/bin/env python3
"""
Test del flujo interactivo de contraseña para calibrate commit
"""

import sys
import time
import serial
from lib.enums import DEFAULT_BAUDRATE

PORT = '/dev/ttyUSB0'
BAUDRATE = DEFAULT_BAUDRATE

def main():
    print("="*70)
    print("  TEST: Flujo Interactivo de calibrate commit")
    print("="*70)
    print(f"Puerto: {PORT} @ {BAUDRATE} baud\n")
    
    try:
        # Abrir puerto
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            timeout=2.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        print("✅ Puerto abierto")
        
        # Detener cualquier operación en curso
        print("\n1️⃣  Deteniendo operaciones...")
        for _ in range(3):
            ser.write(b'stop\n')
            ser.flush()
            time.sleep(0.2)
        
        # Limpiar buffer
        time.sleep(0.5)
        while ser.in_waiting > 0:
            ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        print("   Buffer limpio")
        
        # Enviar Enter para obtener prompt
        ser.write(b'\n')
        ser.flush()
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if 'ADMX2001>' in response:
                print("   ✅ Prompt detectado")
        
        # FASE 1: Enviar calibrate commit
        print("\n2️⃣  Enviando 'calibrate commit'...")
        ser.write(b'calibrate commit\n')
        ser.flush()
        time.sleep(1.0)
        
        # Leer respuesta
        response = ""
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        
        print(f"   Respuesta: {repr(response)}")
        
        # Verificar PASSWORD>
        if 'PASSWORD>' in response:
            print("   ✅ PASSWORD> detectado")
            
            # FASE 2: Enviar contraseña
            print("\n3️⃣  Enviando contraseña 'Analog123'...")
            ser.write(b'Analog123\n')
            ser.flush()
            time.sleep(3.0)  # Esperar más tiempo para escribir en flash
            
            # Leer respuesta final
            final_response = ""
            max_attempts = 10
            for attempt in range(max_attempts):
                if ser.in_waiting > 0:
                    chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    final_response += chunk
                    print(f"   [{attempt+1}] Chunk: {repr(chunk[:80])}")
                else:
                    time.sleep(0.3)
                    
                # Si vemos prompt o Done, terminamos
                if 'ADMX2001>' in final_response or 'Done' in final_response:
                    break
            
            print(f"\n   Respuesta completa: {repr(final_response)}")
            
            # Verificar success/commit
            if 'success' in final_response.lower() or 'commit' in final_response.lower():
                print("   ✅ Calibración guardada exitosamente")
                ser.close()
                return 0
            else:
                print("   ⚠️  Respuesta inesperada")
        else:
            print("   ❌ No se recibió PASSWORD>")
        
        ser.close()
        return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
