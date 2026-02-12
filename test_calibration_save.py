#!/usr/bin/env python3
"""
Test: Verificar estado de calibración y hacer commit si está lista
"""

import sys
import time
import serial
from lib.enums import DEFAULT_BAUDRATE

PORT = '/dev/ttyUSB0'
BAUDRATE = DEFAULT_BAUDRATE

def send_command(ser, command, timeout=3.0):
    """Envía comando y espera respuesta"""
    ser.write((command + '\n').encode('utf-8'))
    ser.flush()
    
    response = ""
    start_time = time.time()
    last_data = time.time()
    
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            response += chunk
            last_data = time.time()
            
            if 'ADMX2001>' in response:
                break
        else:
            if response and (time.time() - last_data > 1.0):
                break
            time.sleep(0.05)
    
    return response

def main():
    print("="*70)
    print("  TEST: Verificar Calibración + Commit")
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
        print("✅ Puerto abierto")
        
        # Limpiar
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
            ser.read(ser.in_waiting)
        
        # PASO 1: Verificar estado con 'calibrate open'
        print("\n" + "="*70)
        print("PASO 1: Verificar estado de calibración")
        print("="*70)
        
        response = send_command(ser, "calibrate open", timeout=30.0)
        
        # Analizar respuesta
        lines = [l.strip() for l in response.split('\n') if l.strip() and 'ADMX2001>' not in l]
        
        print(f"\n📋 Respuesta de 'calibrate open':")
        for line in lines:
            print(f"   {line}")
        
        # Buscar estado de calibración
        open_done = any('open:Done' in l or 'open: Done' in l for l in lines)
        short_done = any('short:Done' in l or 'short: Done' in l for l in lines)
        load_done = any('load:Done' in l or 'load: Done' in l for l in lines)
        
        print(f"\n📊 Estado:")
        print(f"   Open:  {'✅ Done' if open_done else '❌ Not Done'}")
        print(f"   Short: {'✅ Done' if short_done else '❌ Not Done'}")
        print(f"   Load:  {'✅ Done' if load_done else '❌ Not Done'}")
        
        all_done = open_done and short_done and load_done
        
        if not all_done:
            print(f"\n⚠️  Calibración incompleta - no se puede hacer commit")
            if not open_done:
                print(f"   Falta: calibrate open")
            if not short_done:
                print(f"   Falta: calibrate short")
            if not load_done:
                print(f"   Falta: calibrate load")
            ser.close()
            return 1
        
        print(f"\n✅ Calibración completa - procediendo con commit...")
        
        # PASO 2: Hacer commit con timestamp
        print("\n" + "="*70)
        print("PASO 2: Ejecutar calibrate commit")
        print("="*70)
        
        timestamp = int(time.time())
        command = f'calibrate commit {timestamp}'
        print(f"\n📤 Enviando: {command}")
        
        ser.write((command + '\n').encode('utf-8'))
        ser.flush()
        
        # Esperar PASSWORD>
        response = ""
        start_time = time.time()
        
        while time.time() - start_time < 5.0:
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                response += chunk
                
                if 'PASSWORD>' in response:
                    print("   ✅ PASSWORD> detectado")
                    break
            time.sleep(0.1)
        
        if 'PASSWORD>' not in response:
            print(f"   ❌ No se recibió PASSWORD>")
            print(f"   Respuesta: {repr(response)}")
            ser.close()
            return 1
        
        # PASO 3: Enviar contraseña
        print("\n" + "="*70)
        print("PASO 3: Enviar contraseña")
        print("="*70)
        
        print("\n📤 Enviando: Analog123")
        ser.write(b'Analog123\n')
        ser.flush()
        
        # Esperar respuesta (escritura flash tarda varios segundos)
        final_response = ""
        start_time = time.time()
        
        print("\n⏳ Esperando respuesta (escritura en flash)...")
        
        while time.time() - start_time < 10.0:
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                final_response += chunk
                elapsed = time.time() - start_time
                print(f"   [{elapsed:.1f}s] {repr(chunk[:60])}")
                
                if 'ADMX2001>' in chunk or 'success' in chunk.lower() or 'Done' in chunk:
                    break
            time.sleep(0.2)
        
        # PASO 4: Verificar resultado
        print("\n" + "="*70)
        print("RESULTADO")
        print("="*70)
        
        print(f"\n📋 Respuesta completa:")
        lines = [l.strip() for l in final_response.split('\n') if l.strip() and 'ADMX2001>' not in l]
        for line in lines:
            print(f"   {line}")
        
        if 'success' in final_response.lower():
            print("\n✅ ¡CALIBRACIÓN GUARDADA EXITOSAMENTE!")
            ser.close()
            return 0
        elif 'Done' in final_response:
            print("\n✅ ¡COMANDO COMPLETADO!")
            ser.close()
            return 0
        else:
            print("\n⚠️  Respuesta no contiene 'success' o 'Done'")
            ser.close()
            return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
