#!/usr/bin/env python3
"""
Recuperación agresiva del dispositivo ADMX2001
Intenta todas las estrategias para sacar al dispositivo de estados bloqueados
"""

import sys
import time
import serial

PORT = '/dev/ttyUSB0'
BAUDRATES = [230400, 115200]  # Probar los dos más comunes

def aggressive_recovery(baudrate):
    """Intenta recuperar el dispositivo con todas las estrategias"""
    print(f"\n{'='*70}")
    print(f"  Intentando recuperación @ {baudrate} baud")
    print(f"{'='*70}\n")
    
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=baudrate,
            timeout=0.5,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        
        # ESTRATEGIA 1: Múltiples Ctrl-C
        print("1️⃣  Enviando 10x Ctrl-C (detener comandos)...")
        for i in range(10):
            ser.write(b'\x03')
            ser.flush()
            time.sleep(0.05)
        time.sleep(0.5)
        
        # Limpiar buffer
        discarded = 0
        while ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            discarded += len(chunk)
            time.sleep(0.1)
        print(f"   Descartados: {discarded} bytes")
        
        # ESTRATEGIA 2: Ctrl-Z (suspender)
        print("2️⃣  Enviando Ctrl-Z (suspender proceso)...")
        ser.write(b'\x1A')  # Ctrl-Z
        ser.flush()
        time.sleep(0.3)
        
        # Limpiar
        while ser.in_waiting > 0:
            ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        # ESTRATEGIA 3: ESC múltiples veces
        print("3️⃣  Enviando 5x ESC (salir de menús)...")
        for _ in range(5):
            ser.write(b'\x1B')  # ESC
            ser.flush()
            time.sleep(0.05)
        time.sleep(0.3)
        
        # Limpiar
        while ser.in_waiting > 0:
            ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        # ESTRATEGIA 4: Ctrl-D (EOF)
        print("4️⃣  Enviando Ctrl-D (EOF)...")
        ser.write(b'\x04')  # Ctrl-D
        ser.flush()
        time.sleep(0.3)
        
        # Limpiar
        while ser.in_waiting > 0:
            ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        # ESTRATEGIA 5: Reset completo de buffers
        print("5️⃣  Reset completo de buffers...")
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.5)
        
        # ESTRATEGIA 6: Múltiples enters
        print("6️⃣  Enviando 5x Enter (obtener prompt)...")
        for _ in range(5):
            ser.write(b'\n')
            ser.flush()
            time.sleep(0.2)
            
            # Ver si hay respuesta
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if 'ADMX2001>' in response:
                    print(f"   ✅ PROMPT DETECTADO!")
                    print(f"   Respuesta: {repr(response)}")
                    ser.close()
                    return True
        
        # Leer cualquier respuesta pendiente
        time.sleep(0.5)
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"   Respuesta: {repr(response[:200])}")
            if 'ADMX2001>' in response:
                print("   ✅ PROMPT DETECTADO!")
                ser.close()
                return True
        
        # ESTRATEGIA 7: Comando *idn (identificación)
        print("7️⃣  Enviando *idn (identificación)...")
        ser.write(b'*idn\n')
        ser.flush()
        time.sleep(1.0)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"   Respuesta: {repr(response[:200])}")
            if 'Analog' in response or 'ADMX' in response or 'ADMX2001>' in response:
                print("   ✅ DISPOSITIVO RESPONDE!")
                ser.close()
                return True
        
        # ESTRATEGIA 8: Comando help
        print("8️⃣  Enviando 'help'...")
        ser.write(b'help\n')
        ser.flush()
        time.sleep(1.0)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"   Respuesta: {repr(response[:200])}")
            if 'command' in response.lower() or 'ADMX2001>' in response:
                print("   ✅ DISPOSITIVO RESPONDE!")
                ser.close()
                return True
        
        ser.close()
        print("\n❌ No se pudo recuperar el dispositivo")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("  🚑 RECUPERACIÓN AGRESIVA DE ADMX2001")
    print("="*70)
    print(f"Puerto: {PORT}")
    print("\n⚠️  Este script intentará TODAS las estrategias para recuperar")
    print("    el dispositivo de estados bloqueados/corruptos.\n")
    
    for baudrate in BAUDRATES:
        if aggressive_recovery(baudrate):
            print("\n" + "="*70)
            print(f"  ✅ RECUPERACIÓN EXITOSA @ {baudrate} baud")
            print("="*70)
            print(f"\n🎯 Dispositivo funcionando correctamente")
            print(f"💡 Configurar DEFAULT_BAUDRATE = {baudrate} en lib/enums.py")
            return 0
    
    print("\n" + "="*70)
    print("  ❌ RECUPERACIÓN FALLIDA")
    print("="*70)
    print("\n🔴 El dispositivo NO responde a ninguna estrategia\n")
    print("📋 INSTRUCCIONES DE RESET FÍSICO:")
    print("   1. Desconectar el cable USB del ADMX2001")
    print("   2. Esperar 15 segundos completos")
    print("   3. Reconectar el cable USB")
    print("   4. Esperar 5 segundos más")
    print("   5. Ejecutar: python test_find_baudrate.py")
    print("\n💡 Si aún no funciona:")
    print("   - Verificar que el LED de alimentación está encendido")
    print("   - Probar con otro cable USB")
    print("   - Probar con otro puerto USB de la computadora")
    print("   - Verificar que no hay otros programas usando /dev/ttyUSB0")
    
    return 1

if __name__ == '__main__':
    sys.exit(main())
