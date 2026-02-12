#!/usr/bin/env python3
"""
Test rápido del flujo de calibrate commit con contraseña
(asume que ya hay calibración en memoria)
"""

import sys
import time
import serial
from lib.enums import DEFAULT_BAUDRATE

PORT = '/dev/ttyUSB0'
BAUDRATE = DEFAULT_BAUDRATE

def main():
    print("="*70)
    print("  TEST RÁPIDO: calibrate commit con contraseña")
    print("="*70)
    print(f"Puerto: {PORT} @ {BAUDRATE} baud\n")
    
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            timeout=2.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        print("✅ Puerto abierto\n")
        
        # Limpiar
        print("🧹 Limpiando buffer...")
        for _ in range(3):
            ser.write(b'stop\n')
            ser.flush()
            time.sleep(0.2)
        
        time.sleep(0.5)
        while ser.in_waiting > 0:
            ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        # Obtener prompt
        ser.write(b'\n')
        ser.flush()
        time.sleep(0.5)
        if ser.in_waiting > 0:
            r = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if 'ADMX2001>' in r:
                print("✅ Prompt detectado\n")
        
        # === FLUJO INTERACTIVO ===
        
        # 1. Enviar calibrate commit
        print("=" * 70)
        print("PASO 1: Enviando 'calibrate commit'")
        print("=" * 70)
        ser.write(b'calibrate commit\n')
        ser.flush()
        time.sleep(1.5)
        
        response1 = ""
        if ser.in_waiting > 0:
            response1 = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        
        print(f"\n📥 Respuesta:")
        for line in response1.split('\n'):
            if line.strip():
                print(f"   {line}")
        
        # 2. Verificar PASSWORD>
        if 'PASSWORD>' in response1:
            print("\n✅ PASSWORD> DETECTADO - dispositivo esperando contraseña\n")
            
            # 3. Enviar contraseña
            print("=" * 70)
            print("PASO 2: Enviando contraseña 'Analog123'")
            print("=" * 70)
            ser.write(b'Analog123\n')
            ser.flush()
            print("📤 Contraseña enviada\n")
            
            # 4. Esperar respuesta (escritura en flash tarda)
            print("⏳ Esperando respuesta (puede tardar hasta 5s - escritura en flash)...")
            time.sleep(3.0)
            
            # Leer respuesta con polling
            final_response = ""
            for attempt in range(15):
                if ser.in_waiting > 0:
                    chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    final_response += chunk
                else:
                    time.sleep(0.3)
                
                if 'ADMX2001>' in final_response:
                    break
            
            print(f"\n📥 Respuesta final:")
            for line in final_response.split('\n'):
                if line.strip() and 'ADMX2001>' not in line:
                    print(f"   {line}")
            
            # 5. Analizar resultado
            print("\n" + "=" * 70)
            if 'success' in final_response.lower():
                print("✅ ✅ ✅ ¡CALIBRACIÓN GUARDADA EXITOSAMENTE! ✅ ✅ ✅")
                print("=" * 70)
                ser.close()
                return 0
            elif 'not done' in final_response.lower():
                print("⚠️  ADVERTENCIA: Calibración no completada")
                print("=" * 70)
                print("\n💡 Esto significa que falta algún paso de calibración:")
                print("   - calibrate open")
                print("   - calibrate short")
                print("   - calibrate load")
                print("\nDebes completar los 3 pasos antes de hacer commit.")
                ser.close()
                return 1
            else:
                print("⚠️  RESPUESTA INESPERADA")
                print("=" * 70)
                print(f"\nRespuesta completa: {repr(final_response[:200])}")
                ser.close()
                return 1
            
        elif 'not done' in response1.lower():
            print("\n⚠️  Calibración NO completada - no se puede guardar")
            print("\n💡 Debes hacer primero:")
            print("   1. calibrate open")
            print("   2. calibrate short")
            print("   3. calibrate load")
            print("\n   Luego podrás hacer calibrate commit")
            ser.close()
            return 1
        else:
            print("\n❌ No se recibió PASSWORD> ni mensaje de error")
            print(f"Respuesta: {repr(response1[:200])}")
            ser.close()
            return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
