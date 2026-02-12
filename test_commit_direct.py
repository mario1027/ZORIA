#!/usr/bin/env python3
"""
Script para ejecutar calibrate rt 1000 xt 0 y luego COMMIT directamente
Sin verificar con calibrate open (que sobrescribe el estado)
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
    print("  TEST: Calibrate rt 1000 xt 0 + COMMIT INMEDIATO")
    print("="*70)
    
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
        print("PASO 1: Ejecutar calibrate rt 1000 xt 0")
        print("="*70)
        print()
        
        response = send_command(ser, "calibrate rt 1000 xt 0", timeout=30.0)
        
        # Verificar si reportó load:Done
        if 'load:Done' in response:
            print("\n✅ Calibración load completada\n")
        else:
            print("\n⚠️  No se ve 'load:Done' en la respuesta\n")
            return 1
        
        print("="*70)
        print("PASO 2: COMMIT inmediato (sin verificar con calibrate open)")
        print("="*70)
        print()
        
        # Generar timestamp (Unix epoch - número entero)
        timestamp = int(time.time())
        commit_command = f"calibrate commit {timestamp}"
        
        print(f"📤 Enviando: {commit_command}")
        ser.reset_input_buffer()
        ser.write(f"{commit_command}\n".encode('utf-8'))
        time.sleep(0.2)
        
        # Esperar PASSWORD>
        print("⏳ Esperando prompt PASSWORD>...")
        start_time = time.time()
        password_prompt_found = False
        
        while (time.time() - start_time) < 5.0:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"   {line}")
                    if 'PASSWORD>' in line or 'password>' in line.lower():
                        password_prompt_found = True
                        break
            else:
                time.sleep(0.05)
        
        if not password_prompt_found:
            print("⚠️  No se detectó prompt PASSWORD>")
            # Leer cualquier respuesta pendiente
            remaining = send_command(ser, "", timeout=2.0)
            if remaining:
                print("Respuesta recibida:")
                print(remaining)
            return 1
        
        print("\n✅ Prompt PASSWORD> detectado\n")
        
        print("="*70)
        print("PASO 3: Enviar contraseña 'Analog123'")
        print("="*70)
        print()
        
        password = "Analog123"
        print(f"🔐 Enviando contraseña: {'*' * len(password)}")
        ser.write(f"{password}\n".encode('utf-8'))
        
        # Esperar respuesta (puede tardar hasta 10s por escritura a flash)
        print("⏳ Esperando confirmación (hasta 15s por escritura a flash)...")
        time.sleep(0.5)
        
        response_lines = []
        start_time = time.time()
        
        while (time.time() - start_time) < 15.0:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    response_lines.append(line)
                    print(f"   {line}")
                    
                    # Buscar indicadores de éxito
                    if 'success' in line.lower() or 'done' in line.lower():
                        print("\n✅ ¡COMMIT EXITOSO!")
                        return 0
            else:
                time.sleep(0.1)
        
        # Verificar si hubo éxito en alguna línea
        response_text = '\n'.join(response_lines)
        if 'success' in response_text.lower() or 'done' in response_text.lower():
            print("\n✅ ¡COMMIT EXITOSO!")
            return 0
        else:
            print("\n⚠️  No se detectó confirmación de éxito")
            print(f"Respuesta completa:\n{response_text}")
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
