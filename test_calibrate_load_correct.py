#!/usr/bin/env python3
"""
Script para ejecutar calibrate rt 1000 xt 0
Calibración de carga con 1001Ω conectado
"""

import serial
import time

def send_command(ser, command, timeout=3.0):
    """Envía comando y lee respuesta completa"""
    print(f"📤 Enviando: {command}")
    ser.reset_input_buffer()
    ser.write(f"{command}\n".encode('utf-8'))
    time.sleep(0.1)
    
    lines = []
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    lines.append(line)
                    print(f"   {line}")
            except Exception as e:
                print(f"⚠️  Error leyendo: {e}")
        else:
            time.sleep(0.05)
    
    return '\n'.join(lines)

def main():
    print("="*70)
    print("  EJECUTAR: calibrate rt 1000 xt 0")
    print("="*70)
    print("⚠️  Asegúrate que la carga de 1001Ω esté conectada al DUT")
    print()
    
    # Abrir puerto
    port = '/dev/ttyUSB0'
    baudrate = 115200
    
    print(f"🔌 Abriendo {port} @ {baudrate} baud...")
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1,
            write_timeout=1
        )
        time.sleep(0.5)
        print("✅ Puerto abierto\n")
        
        # Limpiar buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        print("="*70)
        print("Ejecutando: calibrate rt 1000 xt 0")
        print("="*70)
        print()
        
        # Enviar calibrate rt 1000 xt 0 (puede tardar varios segundos)
        response = send_command(ser, "calibrate rt 1000 xt 0", timeout=30.0)
        
        print()
        print("="*70)
        print("Verificando estado")
        print("="*70)
        print()
        
        # Verificar estado
        response = send_command(ser, "calibrate open", timeout=5.0)
        
        # Parsear estado
        lines = response.split('\n')
        open_done = any('open:Done' in line for line in lines)
        short_done = any('short:Done' in line for line in lines)
        load_done = any('load:Done' in line for line in lines)
        
        print()
        print("📊 Estado final:")
        print(f"   Open:  {'✅ Done' if open_done else '❌ Not Done'}")
        print(f"   Short: {'✅ Done' if short_done else '❌ Not Done'}")
        print(f"   Load:  {'✅ Done' if load_done else '❌ Not Done'}")
        
        if all([open_done, short_done, load_done]):
            print()
            print("✅ ¡Calibración completa! Ahora puedes hacer commit.")
            print("   Ejecuta: python test_calibration_save.py")
            return 0
        else:
            print()
            print("⚠️  Calibración aún incompleta")
            return 1
            
    except serial.SerialException as e:
        print(f"❌ Error de puerto serial: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print()
            print("🔌 Puerto cerrado")

if __name__ == '__main__':
    exit(main())
