#!/usr/bin/env python3
"""
Test simplificado: simula exactamente lo que hace el callback de calibration_page
"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

import serial.tools.list_ports
from lib.admx2001 import ADMX2001
from lib.calibration_parser import parse_calibrate_list_lines

def find_device_port():
    """Encuentra el puerto del dispositivo"""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    
    # Buscar ADMX o usar el primero disponible
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            return port.device
    
    return ports[0].device if ports else None

def test_callback_simulation():
    """Simula el callback refresh_calibrations_table"""
    print("="*70)
    print("SIMULACIÓN DEL CALLBACK DE CALIBRACIÓN")
    print("="*70)
    
    # Buscar y conectar al dispositivo
    port = find_device_port()
    if not port:
        print("\n❌ No se encontró ningún puerto serial")
        print("\nVerifica:")
        print("  1. Dispositivo ADMX2001 conectado por USB")
        print("  2. Cable USB funcional")
        print("  3. Permisos de puerto serial (sudo usermod -a -G dialout $USER)")
        return 1
    
    print(f"\n🔌 Conectando a {port}...")
    
    device = None
    try:
        device = ADMX2001(port, baudrate=115200, timeout=5)
        print(f"✅ Dispositivo conectado: {port}")
    
        # Paso 1: Obtener calibraciones (igual que el callback)
        print("\n" + "="*70)
        print("PASO 1: device.calibration.list_calibrations()")
        print("="*70)
    
        calibrations_raw = device.calibration.list_calibrations()
        
        print(f"\nResultado:")
        print(f"  Tipo: {type(calibrations_raw)}")
        print(f"  Cantidad líneas: {len(calibrations_raw) if calibrations_raw else 0}")
        
        if not calibrations_raw or len(calibrations_raw) == 0:
            print("\n❌ PROBLEMA ENCONTRADO: No se recibieron líneas")
            print("   La tabla quedará vacía porque no hay datos para parsear")
            print("\n   Posibles causas:")
            print("   1. El dispositivo no tiene calibraciones guardadas")
            print("   2. El comando 'calibrate list' no está funcionando")
            print("   3. Hay un error de comunicación")
            return 1
        
        print("\n" + "="*70)
        print("LÍNEAS CRUDAS RECIBIDAS:")
        print("="*70)
        for idx, line in enumerate(calibrations_raw):
            print(f"[{idx:2d}] {repr(line)}")
        
        # Paso 2: Parsear (igual que el callback)
        print("\n" + "="*70)
        print("PASO 2: parse_calibrate_list_lines()")
        print("="*70)
        
        frequencies_with_configs = parse_calibrate_list_lines(calibrations_raw)
        
        print(f"\nResultado del parseo:")
        print(f"  Frecuencias encontradas: {len(frequencies_with_configs)}")
        
        if not frequencies_with_configs:
            print("\n❌ PROBLEMA ENCONTRADO: El parseo no detectó ninguna frecuencia")
            print("   La tabla se llenará con mensaje de 'No hay calibraciones'")
            print("\n   Esto significa que:")
            print("   1. El formato de las líneas NO coincide con el parser")
            print("   2. Todas las líneas fueron filtradas como inválidas")
            print("\n   Revisa las líneas crudas arriba y compáralas con:")
            print("   - Formatos esperados en lib/calibration_parser.py")
            return 1
        
        print("\n" + "="*70)
        print("FRECUENCIAS PARSEADAS:")
        print("="*70)
        
        for freq_key in sorted(frequencies_with_configs.keys(), key=lambda x: float(x) if x.isdigit() else 0):
            configs = frequencies_with_configs[freq_key]
            print(f"\nFREQ={freq_key} Hz ({len(configs)} configuraciones):")
            for idx, config in enumerate(configs):
                if config.get('placeholder'):
                    print(f"  [{idx}] PLACEHOLDER (sin detalles)")
                else:
                    print(f"  [{idx}] CH0={config.get('ch0')}, CH1={config.get('ch1')}, RES={config.get('res')}")
                    print(f"       raw: {config.get('raw')}")
        
        # Paso 3: Generar filas (simplificado)
        print("\n" + "="*70)
        print("PASO 3: Generación de filas para tabla")
        print("="*70)
        
        row_num = 1
        total_rows = 0
        
        for freq, configs in sorted(frequencies_with_configs.items(), 
                                   key=lambda x: float(x[0]) if x[0].isdigit() else 0):
            
            if configs and configs[0].get('placeholder'):
                print(f"\nFila {row_num}: FREQ={freq} Hz (placeholder)")
                print(f"  -> Mostrará: 'Usar calibrate list {freq} para detalles'")
                row_num += 1
                total_rows += 1
            else:
                for config in configs:
                    print(f"\nFila {row_num}: FREQ={freq} Hz")
                    print(f"  CH0={config.get('ch0')}, CH1={config.get('ch1')}, RES={config.get('res')}")
                    row_num += 1
                    total_rows += 1
        
        print(f"\n" + "="*70)
        print(f"✅ Se generarían {total_rows} filas en la tabla")
        print("="*70)
        
        if total_rows == 0:
            print("\n❌ PROBLEMA: No se generaron filas")
        else:
            print("\n✅ TODO CORRECTO")
            print("Si la tabla sigue vacía en la web, el problema está en:")
            print("  1. El callback no se está ejecutando")
            print("  2. Hay un error en el renderizado HTML")
            print("  3. El botón 'Actualizar' no está conectado al callback")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        if device:
            print("\n🔌 Cerrando conexión...")
            try:
                device.close()
                print("✅ Conexión cerrada")
            except:
                pass

if __name__ == "__main__":
    sys.exit(test_callback_simulation())
