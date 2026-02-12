#!/usr/bin/env python3
"""
Test completo del proceso de calibración ADMX2001:
1. Calibrate open
2. Calibrate short  
3. Calibrate load
4. Calibrate commit (con contraseña)
5. Verificación
"""

import sys
import time
import serial
from lib.enums import DEFAULT_BAUDRATE

PORT = '/dev/ttyUSB0'
BAUDRATE = DEFAULT_BAUDRATE

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def send_command_and_wait(ser, command, timeout=30.0, description=""):
    """Envía comando y espera respuesta completa"""
    if description:
        print(f"\n📤 {description}")
    else:
        print(f"\n📤 Enviando: '{command}'")
    
    ser.write((command + '\n').encode('utf-8'))
    ser.flush()
    
    response_buffer = ""
    start_time = time.time()
    last_data_time = time.time()
    
    print(f"📥 Esperando respuesta (timeout: {timeout}s)...")
    
    while True:
        if time.time() - start_time > timeout:
            print(f"⏱️  Timeout alcanzado ({timeout}s)")
            break
        
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            response_buffer += chunk
            last_data_time = time.time()
            
            # Mostrar progreso si hay algo importante
            if 'Done' in chunk:
                print(f"   ✅ 'Done' detectado")
            
            if 'ADMX2001>' in response_buffer:
                elapsed = time.time() - start_time
                print(f"✅ Prompt detectado ({elapsed:.1f}s)")
                break
        else:
            time.sleep(0.05)
            
            # Si no hay más datos por 3 segundos, terminamos
            if response_buffer and (time.time() - last_data_time > 3.0):
                elapsed = time.time() - start_time
                print(f"✅ Sin más datos ({elapsed:.1f}s)")
                break
    
    return response_buffer

def analyze_calibration_response(response, expected_type="open"):
    """Analiza respuesta de calibración"""
    lines = [l.strip() for l in response.split('\n') if l.strip() and 'ADMX2001>' not in l]
    
    print(f"\n📋 Análisis ({len(lines)} líneas):")
    
    # Buscar líneas importantes
    has_done = False
    has_data = False
    has_error = False
    
    for line in lines[:10]:
        print(f"   {line[:70]}")
        
        if 'Done' in line and expected_type in line.lower():
            has_done = True
        if ',' in line and 'e+' in line:
            has_data = True
        if 'error' in line.lower() or 'fail' in line.lower():
            has_error = True
    
    if len(lines) > 10:
        print(f"   ... y {len(lines)-10} líneas más")
    
    return {
        'has_done': has_done,
        'has_data': has_data,
        'has_error': has_error,
        'success': has_done and not has_error
    }

def main():
    print_section("🔬 TEST COMPLETO DE CALIBRACIÓN CON GUARDADO")
    print(f"Puerto: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    print("\n⚠️  IMPORTANTE: Este test requiere hardware real con loads conectados")
    print("   - Open: Sin conexión (aire)")
    print("   - Short: Conexión directa entre terminales")
    print("   - Load: Resistencia/impedancia conocida\n")
    
    input("Presiona ENTER para iniciar el test...")
    
    try:
        # Abrir puerto
        print("\n📡 Abriendo conexión serial...")
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            timeout=2.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        print("✅ Puerto abierto")
        
        # Detener streaming
        print_section("PASO 0: Preparación")
        print("🛑 Deteniendo operaciones...")
        for _ in range(5):
            ser.write(b'stop\n')
            ser.flush()
            time.sleep(0.2)
        
        # Limpiar buffer
        time.sleep(0.5)
        discarded = 0
        for _ in range(20):
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting)
                discarded += len(chunk)
            else:
                break
            time.sleep(0.1)
        
        if discarded > 0:
            print(f"   Buffer drenado: {discarded} bytes")
        
        # Verificar prompt
        ser.write(b'\n')
        ser.flush()
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if 'ADMX2001>' in response:
                print("✅ Dispositivo listo")
        
        # FASE 1: CALIBRATE OPEN
        print_section("PASO 1: Calibrate OPEN")
        print("📌 INSTRUCCIÓN: Asegúrate de que NO HAY NADA conectado al DUT")
        print("   (terminales al aire - circuito abierto)")
        input("\nPresiona ENTER cuando esté listo...")
        
        response = send_command_and_wait(ser, "calibrate open", timeout=30.0, 
                                        description="Ejecutando calibración OPEN...")
        result_open = analyze_calibration_response(response, "open")
        
        if not result_open['success']:
            print("❌ Calibración OPEN falló")
            ser.close()
            return 1
        
        print("✅ Calibración OPEN completada")
        time.sleep(2)
        
        # FASE 2: CALIBRATE SHORT
        print_section("PASO 2: Calibrate SHORT")
        print("📌 INSTRUCCIÓN: Conecta un corto circuito (cable/jumper) al DUT")
        print("   (conectar ambos terminales directamente)")
        input("\nPresiona ENTER cuando esté listo...")
        
        response = send_command_and_wait(ser, "calibrate short", timeout=30.0,
                                        description="Ejecutando calibración SHORT...")
        result_short = analyze_calibration_response(response, "short")
        
        if not result_short['success']:
            print("❌ Calibración SHORT falló")
            ser.close()
            return 1
        
        print("✅ Calibración SHORT completada")
        time.sleep(2)
        
        # FASE 3: CALIBRATE LOAD
        print_section("PASO 3: Calibrate LOAD")
        print("📌 INSTRUCCIÓN: Conecta la carga de referencia al DUT")
        print("   (resistencia/impedancia conocida - típicamente 1kΩ)")
        input("\nPresiona ENTER cuando esté listo...")
        
        response = send_command_and_wait(ser, "calibrate load", timeout=30.0,
                                        description="Ejecutando calibración LOAD...")
        result_load = analyze_calibration_response(response, "load")
        
        if not result_load['success']:
            print("❌ Calibración LOAD falló")
            ser.close()
            return 1
        
        print("✅ Calibración LOAD completada")
        time.sleep(2)
        
        # FASE 4: VERIFICAR ESTADO DE CALIBRACIÓN
        print_section("PASO 4: Verificar Estado")
        
        # Intentar comando que muestre el estado (ej: enviar z para ver si calibra)
        response = send_command_and_wait(ser, "z", timeout=10.0,
                                        description="Tomando medición de prueba...")
        
        lines = [l.strip() for l in response.split('\n') if l.strip() and 'ADMX2001>' not in l]
        if lines:
            print(f"   Medición obtenida: {lines[0][:50]}")
            print("✅ Dispositivo midiendo correctamente")
        
        # FASE 5: GUARDAR CALIBRACIÓN (calibrate commit)
        print_section("PASO 5: Guardar Calibración (commit)")
        print("🔐 Se iniciará el proceso de guardado con contraseña...")
        time.sleep(1)
        
        # Enviar calibrate commit
        print("\n📤 Enviando 'calibrate commit'...")
        ser.write(b'calibrate commit\n')
        ser.flush()
        time.sleep(1.5)
        
        # Leer respuesta (debe tener PASSWORD>)
        commit_response = ""
        if ser.in_waiting > 0:
            commit_response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        
        print(f"📥 Respuesta: {repr(commit_response[:200])}")
        
        # Verificar PASSWORD>
        if 'PASSWORD>' in commit_response:
            print("✅ PASSWORD> detectado")
            
            # Enviar contraseña
            print("\n🔐 Enviando contraseña 'Analog123'...")
            ser.write(b'Analog123\n')
            ser.flush()
            time.sleep(3.0)  # Esperar escritura en flash
            
            # Leer respuesta final
            final_response = ""
            max_attempts = 15
            for attempt in range(max_attempts):
                if ser.in_waiting > 0:
                    chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    final_response += chunk
                    
                    if chunk.strip():
                        print(f"   [{attempt+1}] {repr(chunk[:80])}")
                else:
                    time.sleep(0.3)
                
                # Si vemos prompt, terminamos
                if 'ADMX2001>' in final_response:
                    break
            
            # Analizar resultado
            print(f"\n📋 Respuesta completa:")
            lines = [l.strip() for l in final_response.split('\n') if l.strip() and 'ADMX2001>' not in l]
            for line in lines:
                print(f"   {line}")
            
            # Verificar success
            success_indicators = ['success', 'commit', 'done']
            has_success = any(indicator in final_response.lower() for indicator in success_indicators)
            
            if has_success:
                print("\n✅ ✅ ✅ CALIBRACIÓN GUARDADA EXITOSAMENTE ✅ ✅ ✅")
            else:
                print("\n⚠️  Respuesta inesperada - verificar manualmente")
        
        else:
            print("❌ No se recibió PASSWORD> - posible problema")
            print(f"   Respuesta: {commit_response}")
        
        # RESUMEN FINAL
        print_section("📊 RESUMEN FINAL")
        print(f"✅ Calibrate OPEN:  {'PASS' if result_open['success'] else 'FAIL'}")
        print(f"✅ Calibrate SHORT: {'PASS' if result_short['success'] else 'FAIL'}")
        print(f"✅ Calibrate LOAD:  {'PASS' if result_load['success'] else 'FAIL'}")
        print(f"✅ Calibrate COMMIT: {'PASS' if 'PASSWORD>' in commit_response else 'FAIL'}")
        
        all_passed = (result_open['success'] and 
                     result_short['success'] and 
                     result_load['success'] and 
                     'PASSWORD>' in commit_response)
        
        if all_passed:
            print("\n🎉 ¡PROCESO COMPLETO EXITOSO!")
            print("   La calibración fue realizada y guardada correctamente.")
        else:
            print("\n⚠️  Algunos pasos fallaron - revisar logs arriba")
        
        ser.close()
        print("\n🔌 Conexión cerrada")
        
        return 0 if all_passed else 1
        
    except serial.SerialException as e:
        print(f"\n❌ Error de puerto serial: {e}")
        return 1
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Test interrumpido por usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
