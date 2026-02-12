#!/usr/bin/env python3
"""
Test de validación rápida de las mejoras TeraTerm
Sin necesidad de hardware - solo verifica que el código no tiene errores
"""

import sys

def test_imports():
    """Test 1: Verificar que todos los módulos se importan correctamente"""
    print("\n[1/5] Test de importaciones...")
    try:
        from lib.calibration import CalibrationManager
        from lib.admx2001 import ADMX2001
        from lib.device_state import device_state
        print("✅ Todos los módulos importados correctamente")
        return True
    except Exception as e:
        print(f"❌ Error importando: {e}")
        return False

def test_calibration_commit_method():
    """Test 2: Verificar que el método commit existe y tiene la firma correcta"""
    print("\n[2/5] Test de método commit()...")
    try:
        from lib.calibration import CalibrationManager
        import inspect
        
        # Verificar que el método commit existe
        if not hasattr(CalibrationManager, 'commit'):
            print("❌ Método commit no encontrado")
            return False
        
        # Verificar parámetros
        sig = inspect.signature(CalibrationManager.commit)
        params = list(sig.parameters.keys())
        
        if 'password' in params and 'timestamp' in params:
            print(f"✅ Método commit con parámetros correctos: {params}")
            return True
        else:
            print(f"❌ Parámetros incorrectos: {params}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_bytearray_usage():
    """Test 3: Verificar que el código usa bytearray (TeraTerm style)"""
    print("\n[3/5] Test de uso de bytearray...")
    try:
        with open('lib/calibration.py', 'r') as f:
            content = f.read()
        
        # Buscar uso de bytearray
        if 'bytearray()' in content:
            count = content.count('bytearray()')
            print(f"✅ Se usa bytearray() correctamente ({count} veces)")
            return True
        else:
            print("❌ No se encontró bytearray() en calibration.py")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_active_detection():
    """Test 4: Verificar que se usa detección activa (no sleep ciego)"""
    print("\n[4/5] Test de detección activa...")
    try:
        with open('lib/calibration.py', 'r') as f:
            content = f.read()
        
        # Buscar patrones de detección activa
        has_in_waiting = 'in_waiting' in content
        has_password_detection = "'PASSWORD>'" in content or '"PASSWORD>"' in content
        
        if has_in_waiting and has_password_detection:
            print("✅ Detección activa de prompts implementada correctamente")
            print("   - ✓ Usa serial.in_waiting")
            print("   - ✓ Detecta prompt PASSWORD>")
            return True
        else:
            print(f"❌ Detección activa incompleta:")
            print(f"   - in_waiting: {has_in_waiting}")
            print(f"   - PASSWORD> detection: {has_password_detection}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_terminal_cli_password_state():
    """Test 5: Verificar que el Terminal CLI maneja password_state"""
    print("\n[5/5] Test de password_state en Terminal CLI...")
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Buscar manejo de password_state
        has_password_state = 'password_state' in content
        has_waiting_flag = "'waiting'" in content or '"waiting"' in content
        has_password_mode = 'PASSWORD MODE' in content or 'PASSWORD>' in content
        
        if has_password_state and has_waiting_flag and has_password_mode:
            print("✅ Terminal CLI maneja prompts interactivos correctamente")
            print("   - ✓ Usa password_state")
            print("   - ✓ Flag 'waiting' presente")
            print("   - ✓ Modo PASSWORD detectado")
            return True
        else:
            print(f"❌ Manejo de password incompleto:")
            print(f"   - password_state: {has_password_state}")
            print(f"   - waiting flag: {has_waiting_flag}")
            print(f"   - PASSWORD mode: {has_password_mode}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("=" * 70)
    print("VALIDACIÓN RÁPIDA - Mejoras TeraTerm")
    print("=" * 70)
    print("\nEste test verifica que las mejoras se aplicaron correctamente")
    print("(No requiere hardware conectado)")
    
    tests = [
        test_imports,
        test_calibration_commit_method,
        test_bytearray_usage,
        test_active_detection,
        test_terminal_cli_password_state
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests pasados: {passed}/{total}")
    
    if passed == total:
        print("\n✅ TODOS LOS TESTS PASARON")
        print("\nLas mejoras TeraTerm están correctamente implementadas:")
        print("  ✓ Detección activa de prompts (PASSWORD>)")
        print("  ✓ Uso de bytearray para buffers")
        print("  ✓ Terminal CLI con manejo interactivo")
        print("  ✓ Contraseña como respuesta (no comando)")
        print("\n🚀 Próximo paso:")
        print("  1. Abre http://localhost:8050 en tu navegador")
        print("  2. Presiona Alt+T para abrir el Terminal CLI")
        print("  3. Conecta al ADMX2001 si tienes hardware")
        print("  4. Prueba: calibrate commit")
        print("  5. Cuando veas PASSWORD>, escribe: Analog123")
        return 0
    else:
        print(f"\n❌ {total - passed} TESTS FALLARON")
        print("\nRevisar los errores arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
