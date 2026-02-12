#!/usr/bin/env python3
"""
Encuentra el comando que detiene el streaming del ADMX2001
"""

import sys
import time
import serial

PORT = '/dev/ttyUSB0'
BAUDRATE = 115200

# Comandos a probar para detener streaming
STOP_COMMANDS = [
    ('Ctrl-C', b'\x03'),
    ('Ctrl-D', b'\x04'),
    ('Ctrl-Z', b'\x1A'),
    ('ESC', b'\x1B'),
    ('Space', b' '),
    ('Enter', b'\n'),
    ('stop', b'stop\n'),
    ('halt', b'halt\n'),
    ('abort', b'abort\n'),
    ('q', b'q\n'),
    ('x', b'x\n'),
]

def count_measurements_per_second(ser, duration=2.0):
    """Cuenta cuántas líneas de medición llegan por segundo"""
    start_time = time.time()
    lines = 0
    
    while time.time() - start_time < duration:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            lines += data.count('\n')
        time.sleep(0.1)
    
    return lines / duration

def test_stop_command(ser, name, command):
    """Prueba si un comando detiene el streaming"""
    print(f"\n🧪 Probando: {name}")
    
    # Medir velocidad antes
    print("   Midiendo mediciones antes... ", end='', flush=True)
    before_rate = count_measurements_per_second(ser)
    print(f"{before_rate:.1f} líneas/s")
    
    # Si no hay streaming, no podemos probar
    if before_rate < 0.5:
        print("   ⚠️  No hay streaming activo, saltando...")
        return False
    
    # Enviar comando de detención múltiples veces
    print(f"   Enviando {name} (5x)...")
    for _ in range(5):
        ser.write(command)
        ser.flush()
        time.sleep(0.1)
    
    # Limpiar buffer
    time.sleep(0.5)
    while ser.in_waiting > 0:
        ser.read(ser.in_waiting)
        time.sleep(0.1)
    
    # Medir velocidad después
    print("   Midiendo mediciones después... ", end='', flush=True)
    time.sleep(0.3)  # Pausa antes de medir
    after_rate = count_measurements_per_second(ser)
    print(f"{after_rate:.1f} líneas/s")
    
    # Verificar si se detuvo
    if after_rate < 0.5 and before_rate > 0.5:
        print(f"   ✅ ¡FUNCIONA! Streaming detenido")
        
        # Verificar si podemos obtener prompt
        ser.write(b'\n')
        ser.flush()
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if 'ADMX2001>' in response:
                print(f"   ✅ Prompt detectado: dispositivo listo")
                return True
            else:
                print(f"   ⚠️  Sin prompt pero streaming detenido")
                print(f"      Respuesta: {repr(response[:50])}")
                return True
    else:
        print(f"   ❌ No detuvo (antes: {before_rate:.1f}, después: {after_rate:.1f})")
        return False

def main():
    print("="*70)
    print("  🔍 BUSCANDO COMANDO PARA DETENER STREAMING")
    print("="*70)
    print(f"Puerto: {PORT} @ {BAUDRATE} baud\n")
    
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            timeout=0.5,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        
        print("📡 Puerto abierto")
        
        # Verificar si hay streaming activo
        print("\n📊 Verificando estado inicial...")
        initial_rate = count_measurements_per_second(ser, duration=3.0)
        print(f"   Velocidad: {initial_rate:.1f} líneas/s")
        
        if initial_rate < 0.5:
            print("\n⚠️  No hay streaming activo.")
            print("   El dispositivo puede estar ya en modo normal.")
            print("\n   Probando obtener prompt...")
            ser.write(b'\n')
            ser.flush()
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if 'ADMX2001>' in response:
                    print("   ✅ Dispositivo responde con prompt - funcionando normalmente")
                    ser.close()
                    return 0
                else:
                    print(f"   ⚠️  Respuesta: {repr(response[:100])}")
        else:
            print(f"\n⚡ Streaming detectado: {initial_rate:.1f} líneas/s")
            print("   Iniciando pruebas de comandos de detención...\n")
        
        # Probar cada comando
        working_commands = []
        for name, command in STOP_COMMANDS:
            if test_stop_command(ser, name, command):
                working_commands.append(name)
                break  # Encontramos uno que funciona, no seguir
            
            # Esperar un poco entre pruebas
            time.sleep(0.5)
        
        # Resultados
        print("\n" + "="*70)
        if working_commands:
            print(f"  ✅ COMANDO(S) EFECTIVO(S): {', '.join(working_commands)}")
            print("="*70)
            print(f"\n🎯 Usar {working_commands[0]} para detener streaming en _connect()")
        else:
            print("  ❌ NINGÚN COMANDO DETUVO EL STREAMING")
            print("="*70)
            print("\n💡 El dispositivo puede estar en un modo especial.")
            print("   Requiere: Reset físico (desconectar/reconectar USB)")
        
        ser.close()
        return 0 if working_commands else 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
