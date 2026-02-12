#!/usr/bin/env python3
"""
Script de prueba para ver la salida cruda de 'calibrate open'
"""
import sys
import logging

# Configurar logging para ver TODO
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Importar las librerías necesarias
from lib.admx2001 import ADMX2001
from lib.device_state import DeviceState

def test_calibrate_open():
    """Probar comando calibrate open y mostrar salida cruda"""
    
    print("\n" + "="*60)
    print("TEST: Salida de 'calibrate open'")
    print("="*60 + "\n")
    
    device_state = DeviceState()
    
    if not device_state.is_connected or not device_state.device:
        print("❌ ERROR: No hay dispositivo conectado")
        print("   Por favor, conecte el dispositivo ADMX2001 primero")
        print("   desde el Dashboard web")
        sys.exit(1)
    
    device = device_state.device
    
    print(f"✓ Dispositivo conectado: {device.port}\n")
    
    # Enviar comando
    print("📤 Enviando comando: 'calibrate open'")
    print("-" * 60)
    
    try:
        response = device.send_command("calibrate open", timeout=30.0)
        
        print(f"\n📥 Respuesta recibida: {len(response) if response else 0} líneas")
        print("="*60)
        
        if response:
            print("\n🔍 LÍNEAS INDIVIDUALES:")
            print("-" * 60)
            for idx, line in enumerate(response):
                print(f"[{idx:2d}] '{line}'")
                print(f"      len={len(line)}, repr={repr(line)}")
            
            print("\n" + "="*60)
            print("📋 SALIDA COMPLETA (como se mostraría en terminal):")
            print("-" * 60)
            for line in response:
                print(line)
            print("-" * 60)
        else:
            print("\n⚠️  Respuesta VACÍA o None")
            
    except Exception as e:
        print(f"\n❌ ERROR ejecutando comando:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_calibrate_open()
