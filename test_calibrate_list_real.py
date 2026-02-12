#!/usr/bin/env python3
"""
Test con dispositivo real: captura la salida de calibrate list y la parsea.
"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

from lib.calibration_parser import parse_calibrate_list_lines
from lib.device_state import device_state

def main():
    print("="*70)
    print("TEST: calibrate list con dispositivo REAL")
    print("="*70)
    
    if not device_state.is_connected or not device_state.device:
        print("\n❌ Dispositivo no conectado")
        print("   Inicia el dashboard primero y conecta el dispositivo.")
        return 1
    
    device = device_state.device
    print(f"\n✅ Dispositivo conectado: {device.port}")
    
    # Ejecutar calibrate list
    print("\n📤 Enviando: calibrate list")
    try:
        response = device.send_command("calibrate list", timeout=30.0)
        
        print(f"\n📥 Respuesta: {len(response) if response else 0} líneas")
        print("\n" + "="*70)
        print("LÍNEAS CRUDAS")
        print("="*70)
        
        if response:
            for idx, line in enumerate(response):
                print(f"[{idx:2d}] {repr(line)}")
        else:
            print("(vacío)")
        
        # Parsear
        print("\n" + "="*70)
        print("PARSEANDO CON parse_calibrate_list_lines()")
        print("="*70)
        
        freqs = parse_calibrate_list_lines(response if response else [])
        
        print(f"\nFrecuencias encontradas: {len(freqs)}")
        
        if freqs:
            for freq_key in sorted(freqs.keys(), key=lambda x: float(x) if x.isdigit() else 0):
                configs = freqs[freq_key]
                print(f"\n  FREQ={freq_key} Hz ({len(configs)} configs)")
                for cfg in configs:
                    if cfg.get('placeholder'):
                        print(f"    - (placeholder, sin detalles)")
                    else:
                        print(f"    - CH0={cfg.get('ch0')}, CH1={cfg.get('ch1')}, RES={cfg.get('res')}")
                        print(f"      raw: {cfg.get('raw')}")
        else:
            print("\n  ❌ No se parseó nada")
            print("\n  Posibles causas:")
            print("    1. No hay calibraciones guardadas en el dispositivo")
            print("    2. El formato de salida no coincide con el parser")
            print("    3. Todas las líneas fueron filtradas como inválidas")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
