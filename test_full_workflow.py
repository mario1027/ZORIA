#!/usr/bin/env python3
"""
Test completo del flujo de comandos ADMX2001
Simula lo que pasa en el sistema y corrige problemas
"""

import sys
import time
import serial
from lib.admx2001 import ADMX2001
from lib.enums import DEFAULT_BAUDRATE

def print_section(title):
    """Imprime una sección del test"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_stop_streaming(device):
    """Prueba detener streaming activo"""
    print_section("TEST 1: Detener streaming activo")
    
    try:
        # Enviar múltiples comandos 'stop'
        print("📤 Enviando 5x 'stop' para detener streaming...")
        for i in range(5):
            device.serial.write(b'stop\n')  # Comando stop
            device.serial.flush()
            time.sleep(0.2)
        time.sleep(0.5)
        
        # Limpiar buffer
        print("🧹 Limpiando buffer...")
        discarded = 0
        time.sleep(0.5)
        while device.serial.in_waiting > 0:
            chunk = device.serial.read(device.serial.in_waiting)
            discarded += len(chunk)
            time.sleep(0.1)
        print(f"   Descartados: {discarded} bytes")
        while device.serial.in_waiting > 0:
            chunk = device.serial.read(device.serial.in_waiting)
            discarded += len(chunk)
            time.sleep(0.1)
        print(f"   Descartados: {discarded} bytes")
        
        # Enviar Enter y verificar prompt
        print("📤 Enviando Enter para obtener prompt...")
        device.serial.write(b'\n')
        device.serial.flush()
        time.sleep(0.5)
        
        if device.serial.in_waiting > 0:
            response = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
            print(f"📥 Respuesta: {repr(response)}")
            
            if 'ADMX2001>' in response:
                print("✅ Prompt detectado - dispositivo listo")
                return True
            else:
                print("⚠️  No se detectó prompt")
                return False
        else:
            print("❌ Sin respuesta")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_display_command(device):
    """Prueba comando display 6"""
    print_section("TEST 2: Comando display 6")
    
    try:
        print("📤 Enviando: 'display 6'")
        device.serial.write(b'display 6\n')
        device.serial.flush()
        
        # Leer respuesta con timeout razonable
        print("📥 Leyendo respuesta...")
        response_buffer = ""
        start_time = time.time()
        last_data_time = time.time()
        
        while True:
            # Timeout total: 5 segundos
            if time.time() - start_time > 5.0:
                print("⏱️  Timeout alcanzado")
                break
            
            if device.serial.in_waiting > 0:
                chunk = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
                response_buffer += chunk
                last_data_time = time.time()
                print(f"   Chunk recibido: {len(chunk)} bytes")
                
                # Si vemos el prompt, terminamos
                if 'ADMX2001>' in response_buffer:
                    print("✅ Prompt detectado - respuesta completa")
                    break
            else:
                time.sleep(0.05)
                
                # Si tenemos datos y no llegan más por 0.5s, terminamos
                if response_buffer and (time.time() - last_data_time > 0.5):
                    print("✅ Sin más datos - asumiendo respuesta completa")
                    break
        
        # Mostrar resultado
        lines = [l.strip() for l in response_buffer.split('\n') if l.strip() and 'ADMX2001>' not in l]
        print(f"\n📋 Respuesta ({len(lines)} líneas):")
        for i, line in enumerate(lines[:10], 1):
            # Filtrar líneas que parecen mediciones
            if line and line[0].isdigit() and ',' in line:
                print(f"   [{i}] ⚠️  MEDICIÓN (debería filtrarse): {line[:50]}...")
            else:
                print(f"   [{i}] ✓ {line}")
        
        if len(lines) > 10:
            print(f"   ... y {len(lines)-10} líneas más")
        
        # Verificar que podemos enviar otro comando
        print("\n🔄 Verificando que el dispositivo responde...")
        device.serial.write(b'\n')
        device.serial.flush()
        time.sleep(0.3)
        
        if device.serial.in_waiting > 0:
            test_response = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
            if 'ADMX2001>' in test_response:
                print("✅ Dispositivo responde correctamente")
                return True
        
        print("⚠️  Dispositivo no responde al prompt")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_z_command(device):
    """Prueba comando z (medición)"""
    print_section("TEST 3: Comando z")
    
    try:
        print("📤 Enviando: 'z'")
        device.serial.write(b'z\n')
        device.serial.flush()
        
        # Leer respuesta (z puede tardar varios segundos con averaging)
        print("📥 Leyendo respuesta (puede tardar hasta 30s con averaging alto)...")
        response_buffer = ""
        start_time = time.time()
        last_data_time = time.time()
        
        while True:
            # Timeout total: 30 segundos para averaging alto
            if time.time() - start_time > 30.0:
                print("⏱️  Timeout alcanzado (30s)")
                break
            
            if device.serial.in_waiting > 0:
                chunk = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
                response_buffer += chunk
                last_data_time = time.time()
                
                if 'ADMX2001>' in response_buffer:
                    elapsed = time.time() - start_time
                    print(f"✅ Prompt detectado ({elapsed:.1f}s)")
                    break
            else:
                time.sleep(0.05)
                
                # timeout sin datos: 3 segundos (comandos lentos)
                if response_buffer and (time.time() - last_data_time > 3.0):
                    elapsed = time.time() - start_time
                    print(f"✅ Sin más datos ({elapsed:.1f}s)")
                    break
        
        # Analizar resultado
        lines = [l.strip() for l in response_buffer.split('\n') if l.strip() and 'ADMX2001>' not in l]
        measurement_lines = [l for l in lines if l and l[0].isdigit() and ',' in l]
        other_lines = [l for l in lines if l and not (l[0].isdigit() and ',' in l)]
        
        print(f"\n📋 Resultado:")
        print(f"   Líneas de medición: {len(measurement_lines)}")
        print(f"   Otras líneas: {len(other_lines)}")
        
        if measurement_lines:
            print(f"\n   🎯 Última medición: {measurement_lines[-1]}")
            if len(measurement_lines) > 1:
                print(f"   ⚠️  {len(measurement_lines)-1} mediciones adicionales (deberían filtrarse)")
        else:
            print(f"   ❌ No se recibió medición - posible timeout")
        
        for line in other_lines:
            print(f"   💬 {line}")
        
        # Verificar dispositivo responde
        print("\n🔄 Verificando respuesta...")
        device.serial.write(b'\n')
        device.serial.flush()
        time.sleep(0.3)
        
        if device.serial.in_waiting > 0:
            test_response = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
            if 'ADMX2001>' in test_response:
                print("✅ Dispositivo listo para siguiente comando")
                return len(measurement_lines) > 0  # Success si recibimos al menos una medición
        
        print("⚠️  Dispositivo no responde")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rapid_commands(device):
    """Prueba envío rápido de comandos"""
    print_section("TEST 4: Comandos rápidos consecutivos")
    
    commands = ['display 6', 'z', 'display 7']
    
    for i, cmd in enumerate(commands, 1):
        try:
            print(f"\n[{i}/{len(commands)}] Enviando: '{cmd}'")
            device.serial.write((cmd + '\n').encode('utf-8'))
            device.serial.flush()
            
            # Leer respuesta rápida
            response_buffer = ""
            start_time = time.time()
            last_data_time = time.time()
            
            while True:
                if time.time() - start_time > 3.0:
                    break
                
                if device.serial.in_waiting > 0:
                    chunk = device.serial.read(device.serial.in_waiting).decode('utf-8', errors='ignore')
                    response_buffer += chunk
                    last_data_time = time.time()
                    
                    if 'ADMX2001>' in response_buffer:
                        break
                else:
                    time.sleep(0.05)
                    if response_buffer and (time.time() - last_data_time > 0.5):
                        break
            
            lines = len([l for l in response_buffer.split('\n') if l.strip()])
            print(f"   ✓ Respuesta recibida: {lines} líneas")
            time.sleep(0.2)  # Pequeña pausa entre comandos
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    print("\n✅ Todos los comandos completados")
    return True

def main():
    """Ejecuta todos los tests"""
    print_section("🔬 TEST COMPLETO DE FLUJO ADMX2001")
    print(f"Puerto: /dev/ttyUSB0")
    print(f"Baudrate: {DEFAULT_BAUDRATE}")
    
    # Conectar
    try:
        print("\n📡 Abriendo conexión serial...")
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=DEFAULT_BAUDRATE,
            timeout=2.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        print("✅ Puerto abierto")
        
        # Crear objeto device mock con serial
        class MockDevice:
            def __init__(self, serial_obj):
                self.serial = serial_obj
        
        device = MockDevice(ser)
        
        # Ejecutar tests
        results = {
            'stop_streaming': test_stop_streaming(device),
            'display': test_display_command(device),
            'z_command': test_z_command(device),
            'rapid_commands': test_rapid_commands(device)
        }
        
        # Resumen
        print_section("📊 RESUMEN DE RESULTADOS")
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\n{'='*60}")
        print(f"  Total: {passed}/{total} tests pasados")
        print(f"{'='*60}")
        
        # Cerrar
        ser.close()
        print("\n🔌 Conexión cerrada")
        
        return 0 if passed == total else 1
        
    except serial.SerialException as e:
        print(f"\n❌ Error abriendo puerto: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
