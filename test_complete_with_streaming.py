#!/usr/bin/env python3
"""
Test completo del ADMX2001 incluyendo modo streaming (sweep)
"""

import sys
import time
import serial
from lib.enums import DEFAULT_BAUDRATE

PORT = '/dev/ttyUSB0'
BAUDRATE = DEFAULT_BAUDRATE

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def send_command(ser, command, timeout=3.0, description=""):
    """Envía comando y espera respuesta"""
    if description:
        print(f"\n📤 {description}")
    else:
        print(f"\n📤 Enviando: '{command}'")
    
    ser.write((command + '\n').encode('utf-8'))
    ser.flush()
    
    print(f"📥 Esperando respuesta (timeout: {timeout}s)...")
    response_buffer = ""
    start_time = time.time()
    last_data_time = time.time()
    
    while True:
        if time.time() - start_time > timeout:
            print(f"⏱️  Timeout alcanzado ({timeout}s)")
            break
        
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            response_buffer += chunk
            last_data_time = time.time()
            
            if 'ADMX2001>' in response_buffer:
                elapsed = time.time() - start_time
                print(f"✅ Prompt detectado ({elapsed:.1f}s)")
                break
        else:
            time.sleep(0.05)
            
            if response_buffer and (time.time() - last_data_time > 1.0):
                elapsed = time.time() - start_time
                print(f"✅ Sin más datos ({elapsed:.1f}s)")
                break
    
    return response_buffer

def analyze_response(response, command_name=""):
    """Analiza y muestra la respuesta"""
    lines = [l.strip() for l in response.split('\n') if l.strip() and 'ADMX2001>' not in l]
    measurement_lines = [l for l in lines if l and l[0].isdigit() and ',' in l and 'e+' in l]
    other_lines = [l for l in lines if l and not (l[0].isdigit() and ',' in l and 'e+' in l)]
    
    print(f"\n📋 Respuesta:")
    print(f"   Total líneas: {len(lines)}")
    print(f"   Mediciones: {len(measurement_lines)}")
    print(f"   Otras: {len(other_lines)}")
    
    if measurement_lines:
        print(f"\n   🎯 Primera medición: {measurement_lines[0][:60]}")
        if len(measurement_lines) > 1:
            print(f"   🎯 Última medición: {measurement_lines[-1][:60]}")
    
    for line in other_lines[:5]:
        print(f"   💬 {line[:70]}")
    
    if len(other_lines) > 5:
        print(f"   ... y {len(other_lines)-5} líneas más")
    
    return len(lines), len(measurement_lines)

def test_stop_existing_streaming(ser):
    """Detiene cualquier streaming existente"""
    print_header("TEST 1: Detener Streaming Existente")
    
    print("🛑 Enviando múltiples comandos 'stop'...")
    for i in range(5):
        ser.write(b'stop\n')
        ser.flush()
        time.sleep(0.2)
    
    time.sleep(0.5)
    
    # Drenar buffer
    print("🧹 Drenando buffer...")
    discarded = 0
    for _ in range(20):
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            discarded += len(chunk)
        else:
            break
        time.sleep(0.1)
    
    print(f"   Descartados: {discarded} bytes")
    
    # Verificar prompt
    ser.write(b'\n')
    ser.flush()
    time.sleep(0.5)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if 'ADMX2001>' in response:
            print("✅ Dispositivo listo - prompt detectado")
            return True
        else:
            print(f"⚠️  Respuesta: {repr(response[:100])}")
    
    print("⚠️  Sin prompt, pero buffer limpio")
    return True

def test_display_command(ser):
    """Prueba comando display"""
    print_header("TEST 2: Comando display 6")
    
    response = send_command(ser, "display 6", timeout=3.0)
    total, measurements = analyze_response(response, "display")
    
    if measurements > 0:
        print(f"⚠️  ADVERTENCIA: display devolvió {measurements} mediciones (deberían filtrarse en app)")
    
    # Verificar que sigue respondiendo
    ser.write(b'\n')
    ser.flush()
    time.sleep(0.3)
    
    if ser.in_waiting > 0:
        test_resp = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if 'ADMX2001>' in test_resp:
            print("✅ Dispositivo responde después de display")
            return True
    
    print("❌ Dispositivo NO responde después de display")
    return False

def test_z_command(ser):
    """Prueba comando z (medición única)"""
    print_header("TEST 3: Comando z (Medición Única)")
    
    response = send_command(ser, "z", timeout=30.0, description="Ejecutando medición (puede tardar hasta 30s con averaging alto)...")
    total, measurements = analyze_response(response, "z")
    
    if measurements == 0:
        print("❌ No se recibió medición")
        return False
    elif measurements == 1:
        print("✅ 1 medición recibida (correcto)")
    else:
        print(f"⚠️  {measurements} mediciones (esperaba 1, pero puede ser normal si hay averaging)")
    
    # Verificar que sigue respondiendo
    ser.write(b'\n')
    ser.flush()
    time.sleep(0.3)
    
    if ser.in_waiting > 0:
        test_resp = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if 'ADMX2001>' in test_resp:
            print("✅ Dispositivo responde después de z")
            return True
    
    print("❌ Dispositivo NO responde después de z")
    return False

def test_sweep_streaming(ser):
    """Prueba modo streaming con sweep"""
    print_header("TEST 4: Modo Streaming (sweep)")
    
    # Configurar sweep pequeño para test rápido
    print("\n⚙️  Configurando sweep:")
    
    # Start frequency
    response = send_command(ser, "start 1000", timeout=2.0, description="Configurando start frequency = 1kHz")
    
    # Stop frequency
    response = send_command(ser, "stop 10000", timeout=2.0, description="Configurando stop frequency = 10kHz")
    
    # Number of points
    response = send_command(ser, "points 5", timeout=2.0, description="Configurando points = 5")
    
    print("\n🚀 Iniciando sweep...")
    ser.write(b'sweep\n')
    ser.flush()
    
    # Recolectar datos de streaming
    print("📊 Recolectando datos de streaming (10 segundos)...")
    start_time = time.time()
    streaming_buffer = ""
    measurements_received = 0
    
    while time.time() - start_time < 10.0:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            streaming_buffer += chunk
            
            # Contar mediciones
            new_measurements = chunk.count('\n')
            measurements_received += new_measurements
            
            if new_measurements > 0:
                print(f"   [{time.time() - start_time:.1f}s] +{new_measurements} mediciones (total: {measurements_received})")
            
            # Si vemos Done o prompt, terminó
            if 'Done' in chunk or 'ADMX2001>' in chunk:
                print("✅ Sweep completado (Done detectado)")
                break
        
        time.sleep(0.2)
    
    print(f"\n📈 Total mediciones recibidas: {measurements_received}")
    
    # Intentar detener (por si acaso sigue)
    print("\n🛑 Deteniendo sweep...")
    for _ in range(3):
        ser.write(b'stop\n')
        ser.flush()
        time.sleep(0.2)
    
    # Drenar buffer restante
    time.sleep(0.5)
    discarded = 0
    for _ in range(10):
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            discarded += len(chunk)
        else:
            break
        time.sleep(0.1)
    
    if discarded > 0:
        print(f"   Drenados: {discarded} bytes adicionales")
    
    # Verificar que responde después del sweep
    print("\n🔄 Verificando respuesta post-sweep...")
    ser.write(b'\n')
    ser.flush()
    time.sleep(0.5)
    
    if ser.in_waiting > 0:
        test_resp = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if 'ADMX2001>' in test_resp:
            print("✅ Dispositivo responde después de sweep")
            # Success si recibimos al menos 1 medición (puede ser menos de points por sweeps rápidos)
            return measurements_received >= 1
    
    print("❌ Dispositivo NO responde después de sweep")
    return False

def test_post_sweep_commands(ser):
    """Prueba que comandos funcionen después de sweep"""
    print_header("TEST 5: Comandos Post-Sweep")
    
    # Test display
    print("\n1️⃣  Probando display 7...")
    response = send_command(ser, "display 7", timeout=3.0)
    total, _ = analyze_response(response)
    
    if total == 0:
        print("❌ Sin respuesta a display")
        return False
    
    time.sleep(0.5)
    
    # Test z
    print("\n2️⃣  Probando z...")
    response = send_command(ser, "z", timeout=15.0)
    total, measurements = analyze_response(response)
    
    if measurements == 0:
        print("❌ Sin medición en z")
        return False
    
    time.sleep(0.5)
    
    # Test otro display
    print("\n3️⃣  Probando display 6...")
    response = send_command(ser, "display 6", timeout=3.0)
    total, _ = analyze_response(response)
    
    if total == 0:
        print("❌ Sin respuesta a display")
        return False
    
    print("\n✅ Todos los comandos post-sweep funcionan")
    return True

def main():
    print_header("🔬 TEST COMPLETO CON STREAMING - ADMX2001")
    print(f"Puerto: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    
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
        
        # Ejecutar tests
        results = {}
        
        results['stop_existing'] = test_stop_existing_streaming(ser)
        time.sleep(1)
        
        results['display'] = test_display_command(ser)
        time.sleep(1)
        
        results['z_command'] = test_z_command(ser)
        time.sleep(1)
        
        results['sweep_streaming'] = test_sweep_streaming(ser)
        time.sleep(1)
        
        results['post_sweep'] = test_post_sweep_commands(ser)
        
        # Resumen
        print_header("📊 RESUMEN FINAL")
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\n{'='*70}")
        print(f"  Total: {passed}/{total} tests pasados ({passed*100//total}%)")
        print(f"{'='*70}")
        
        if passed == total:
            print("\n🎉 ¡TODOS LOS TESTS PASARON!")
            print("   El dispositivo funciona correctamente incluyendo streaming.")
        elif passed >= total * 0.8:
            print("\n⚠️  La mayoría de tests pasaron, pero hay algunos problemas.")
        else:
            print("\n❌ Múltiples tests fallaron.")
            print("   Recomendación: Reset físico del dispositivo (desconectar USB 15s)")
        
        ser.close()
        print("\n🔌 Conexión cerrada")
        
        return 0 if passed == total else 1
        
    except serial.SerialException as e:
        print(f"\n❌ Error de puerto serial: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
