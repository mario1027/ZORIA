#!/usr/bin/env python3
"""
Test de conexión directa al ADMX2001
"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

from lib.admx2001 import ADMX2001
import logging

# Activar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s %(name)-15s %(message)s'
)

def test_direct_connection():
    """Prueba conexión directa usando la clase ADMX2001"""
    
    print("\n" + "="*70)
    print("TEST DE CONEXIÓN DIRECTA - ADMX2001")
    print("="*70 + "\n")
    
    try:
        print("📡 Intentando conectar a /dev/ttyUSB0...")
        print("   Baudrate: 230400")
        print("   Timeout: 2.0s")
        print()
        
        # Crear instancia (esto debería conectar automáticamente)
        device = ADMX2001(port='/dev/ttyUSB0', timeout=2.0)
        
        print("\n✅ ¡CONEXIÓN EXITOSA!")
        print(f"   Puerto: {device.port}")
        print(f"   Conectado: {device.is_connected}")
        print()
        
        # Probar comando simple
        print("📤 Enviando comando: *idn")
        response = device.send_command('*idn')
        
        print(f"📥 Respuesta ({len(response)} líneas):")
        for line in response:
            print(f"   {line}")
        
        # Cerrar conexión
        device.disconnect()
        print("\n✓ Desconectado correctamente")
        
    except ConnectionError as e:
        print(f"\n❌ ERROR DE CONEXIÓN:")
        print(f"   {e}")
        print()
        print("💡 Causas posibles:")
        print("   1. Baudrate incorrecto (debe ser 230400)")
        print("   2. Dispositivo no responde")
        print("   3. Cable USB defectuoso")
        print("   4. Puerto serial bloqueado por otra app")
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        print("\n📋 Stack trace:")
        traceback.print_exc()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_direct_connection()
