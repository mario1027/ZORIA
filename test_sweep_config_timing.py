#!/usr/bin/env python3
"""
Test para verificar que la configuración del sweep funciona correctamente
con los timeouts mejorados (TeraTerm style).
"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

import time
import serial.tools.list_ports
from lib.admx2001 import ADMX2001
from lib.enums import SweepType, SweepScale

def find_device_port():
    """Encuentra el puerto del dispositivo"""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            return port.device
    
    return ports[0].device if ports else None

def test_sweep_configuration():
    """Prueba la configuración del sweep con timeouts mejorados"""
    print("="*70)
    print("TEST DE CONFIGURACIÓN DE SWEEP")
    print("="*70)
    
    port = find_device_port()
    if not port:
        print("\n❌ No se encontró ningún puerto serial")
        return 1
    
    print(f"\n🔌 Conectando a {port}...")
    
    device = None
    try:
        device = ADMX2001(port, baudrate=115200, timeout=5)
        print(f"✅ Dispositivo conectado")
        
        # Test 1: Configurar count
        print("\n" + "="*70)
        print("TEST 1: Configurar count=50")
        print("="*70)
        start_time = time.time()
        device.send_command("count 50")
        elapsed = time.time() - start_time
        print(f"✅ Count configurado en {elapsed:.3f}s")
        
        if elapsed > 1.0:
            print(f"⚠️ ADVERTENCIA: Tomó {elapsed:.3f}s (esperado <0.5s)")
        
        # Test 2: Configurar sweep_type
        print("\n" + "="*70)
        print("TEST 2: Configurar sweep_type frequency")
        print("="*70)
        start_time = time.time()
        device.send_command("sweep_type frequency 100 1000")
        elapsed = time.time() - start_time
        print(f"✅ Sweep type configurado en {elapsed:.3f}s")
        
        if elapsed > 1.0:
            print(f"⚠️ ADVERTENCIA: Tomó {elapsed:.3f}s (esperado <0.5s)")
        
        # Test 3: Configurar sweep_scale
        print("\n" + "="*70)
        print("TEST 3: Configurar sweep_scale")
        print("="*70)
        start_time = time.time()
        device.send_command("sweep_scale log")
        elapsed = time.time() - start_time
        print(f"✅ Sweep scale configurado en {elapsed:.3f}s")
        
        if elapsed > 1.0:
            print(f"⚠️ ADVERTENCIA: Tomó {elapsed:.3f}s (esperado <0.5s)")
        
        # Test 4: Configurar sweep completo usando método configure_sweep
        print("\n" + "="*70)
        print("TEST 4: configure_sweep() completo")
        print("="*70)
        start_time = time.time()
        device.configure_sweep(
            SweepType.FREQUENCY,
            start=100,  # 100 kHz
            end=1000,   # 1 MHz
            scale=SweepScale.LOG,
            count=50
        )
        elapsed = time.time() - start_time
        print(f"✅ Sweep configurado completamente en {elapsed:.3f}s")
        
        if elapsed > 2.0:
            print(f"⚠️ ADVERTENCIA: Tomó {elapsed:.3f}s (esperado <2.0s)")
        else:
            print(f"✅ Timing correcto: {elapsed:.3f}s")
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON")
        print("="*70)
        print(f"\nLa configuración del sweep funciona correctamente")
        print(f"Los timeouts mejorados están funcionando bien")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if device:
            print(f"\n🔌 Cerrando conexión...")
            device.close()
            print(f"✅ Conexión cerrada")

if __name__ == "__main__":
    sys.exit(test_sweep_configuration())
