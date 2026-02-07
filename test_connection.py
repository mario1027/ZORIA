#!/usr/bin/env python3
"""Script de prueba para verificar la conexión con ADMX2001"""

import serial.tools.list_ports
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

from lib import ADMX2001

def test_connection():
    """Prueba la conexión con el ADMX2001"""
    
    print("=" * 60)
    print("TEST DE CONEXIÓN ADMX2001")
    print("=" * 60)
    
    # Listar puertos
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ No se encontraron puertos seriales")
        return
    
    print(f"\n📋 Puertos encontrados: {len(ports)}")
    for p in ports:
        print(f"  - {p.device}: {p.description} ({p.manufacturer})")
    
    # Buscar candidatos
    print("\n🔍 Buscando candidatos ADMX2001...")
    candidates = []
    
    for port in ports:
        desc = port.description.upper() if port.description else ""
        manufacturer = port.manufacturer.upper() if port.manufacturer else ""
        
        is_candidate = any([
            'FTDI' in manufacturer,
            'CP210' in desc,
            'SILICON' in manufacturer,
            'USB' in desc and 'SERIAL' in desc,
            'TTL232' in desc,
            'FT232' in desc,
        ])
        
        if is_candidate:
            candidates.append(port)
            print(f"  ✓ Candidato: {port.device}")
    
    # Probar conexión
    print("\n🔌 Probando conexiones...")
    
    for port in candidates:
        try:
            print(f"\n  Probando {port.device}...")
            
            device = ADMX2001(port.device, baudrate=115200, timeout=3.0)
            
            import time
            time.sleep(0.5)
            
            print(f"    Enviando *idn...")
            response = device.send_command('*idn')
            
            if response:
                print(f"    ✅ RESPUESTA: {response}")
                
                # Verificar que sea ADMX2001
                response_str = str(response).upper()
                if any(x in response_str for x in ['ADMX', '2001', 'ANALOG']):
                    print(f"    ✅ DISPOSITIVO ADMX2001 CONFIRMADO")
                    device.close()
                    return True
                else:
                    print(f"    ⚠️ Dispositivo responde pero no es ADMX2001")
            else:
                print(f"    ❌ Sin respuesta")
            
            device.close()
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            continue
    
    print("\n❌ No se pudo conectar al ADMX2001")
    return False

if __name__ == "__main__":
    test_connection()
