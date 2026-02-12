#!/usr/bin/env python3
"""
Test de baudrates para encontrar el correcto
"""

import sys
import time
import serial

BAUDRATES = [230400, 115200, 57600, 38400, 19200, 9600]
PORT = '/dev/ttyUSB0'

def test_baudrate(baudrate):
    """Prueba un baudrate específico"""
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=baudrate,
            timeout=1.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        
        # Intentar detener streaming
        for _ in range(3):
            ser.write(b'\x03')  # Ctrl-C
            ser.flush()
            time.sleep(0.1)
        
        # Limpiar buffer
        time.sleep(0.3)
        while ser.in_waiting > 0:
            ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        # Resetear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.2)
        
        # Enviar Enter
        ser.write(b'\n')
        ser.flush()
        time.sleep(0.5)
        
        # Leer respuesta
        response = ""
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        
        # Si no hay prompt, intentar *idn
        if 'ADMX2001>' not in response:
            ser.write(b'*idn\n')
            ser.flush()
            time.sleep(0.5)
            if ser.in_waiting > 0:
                idn_response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                response += idn_response
        
        ser.close()
        
        # Analizar respuesta
        has_prompt = 'ADMX2001>' in response
        has_analog = 'Analog' in response
        is_readable = all(c.isprintable() or c in '\r\n\t' for c in response)
        
        return {
            'baudrate': baudrate,
            'response': response,
            'has_prompt': has_prompt,
            'has_analog': has_analog,
            'is_readable': is_readable,
            'success': has_prompt or has_analog
        }
        
    except Exception as e:
        return {
            'baudrate': baudrate,
            'error': str(e),
            'success': False
        }

def main():
    print("="*70)
    print("  🔍 BUSCANDO BAUDRATE CORRECTO")
    print("="*70)
    print(f"Puerto: {PORT}\n")
    
    results = []
    for baudrate in BAUDRATES:
        print(f"Probando {baudrate:>6} baud... ", end='', flush=True)
        result = test_baudrate(baudrate)
        results.append(result)
        
        if result['success']:
            print(f"✅ FUNCIONA!")
            print(f"   Respuesta: {repr(result['response'][:100])}")
        elif 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            is_garbage = not result.get('is_readable', False)
            if is_garbage:
                print(f"⚠️  Datos corruptos")
            else:
                print(f"⚠️  Sin prompt (respuesta: {repr(result['response'][:50])})")
    
    # Resumen
    print("\n" + "="*70)
    print("  📊 RESULTADOS")
    print("="*70)
    
    working = [r for r in results if r['success']]
    if working:
        print(f"\n✅ Baudrates funcionales: {[r['baudrate'] for r in working]}")
        print(f"\n🎯 RECOMENDACIÓN: Usar {working[0]['baudrate']} baud")
    else:
        print("\n❌ Ningún baudrate funcionó")
        print("\n💡 Posibles causas:")
        print("   1. Dispositivo en estado corrupto - requiere reset físico")
        print("   2. Cable USB defectuoso")
        print("   3. Dispositivo en modo bootloader o firmware corrupto")
        print("\n🔧 Solución:")
        print("   1. Desconectar USB del ADMX2001")
        print("   2. Esperar 10 segundos")
        print("   3. Reconectar USB")
        print("   4. Volver a ejecutar este test")
    
    return 0 if working else 1

if __name__ == '__main__':
    sys.exit(main())
