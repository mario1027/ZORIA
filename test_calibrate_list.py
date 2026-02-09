#!/usr/bin/env python3
"""
Script de prueba para verificar el comando 'calibrate list'
y su procesamiento en el terminal.
"""
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from lib.device_state import device_state
from lib import ADMX2001

def test_calibrate_list():
    """Prueba el comando calibrate list"""
    print("=" * 60)
    print("TEST: calibrate list")
    print("=" * 60)
    
    # Listar puertos disponibles
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ No se encontraron puertos serie")
        return False
    
    print("\n📡 Puertos disponibles:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    
    # Si hay argumentos, usar el primer argumento como puerto
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
    else:
        # Intentar usar el primer puerto que parezca ADMX2001
        port_name = None
        for port in ports:
            if 'USB' in port.description or 'ACM' in port.device:
                port_name = port.device
                break
        
        if not port_name:
            port_name = ports[0].device
    
    print(f"\n🔌 Conectando a: {port_name}")
    
    try:
        # Intentar conectar usando device_state
        device_state.connect(port_name)
        
        if not device_state.is_connected or not device_state.device:
            print("❌ No se pudo conectar")
            return False
        
        print("✅ Conectado exitosamente")
        
        # Enviar comando calibrate list
        print("\n📤 Enviando: calibrate list")
        response = device_state.send_command("calibrate list", timeout=30.0)
        
        print(f"\n📥 Respuesta recibida: {len(response) if response else 0} líneas")
        print("=" * 60)
        
        if response:
            for idx, line in enumerate(response):
                print(f"  [{idx:2d}] '{line}'")
        else:
            print("  (respuesta vacía o None)")
        
        print("=" * 60)
        
        # Simular el procesamiento que hace el terminal
        print("\n🔧 PROCESAMIENTO DEL TERMINAL:")
        print("=" * 60)
        
        if response:
            cleaned_lines = []
            skip_next_empty = False
            command = "calibrate list"
            
            for idx, line in enumerate(response):
                line_stripped = line.strip()
                
                print(f"  Línea {idx}: '{line}' -> stripped: '{line_stripped}'")
                
                # Saltar líneas completamente vacías
                if not line_stripped:
                    if command.startswith('calibrate') and cleaned_lines:
                        cleaned_lines.append("")
                        print(f"    -> Agregada como separador")
                    else:
                        print(f"    -> Saltada (vacía)")
                    continue
                
                # Filtrar eco (solo primeras 2 líneas)
                if idx < 2 and line_stripped.lower() == command.lower():
                    print(f"    -> Saltada (eco del comando)")
                    skip_next_empty = True
                    continue
                
                # Saltar línea vacía después del eco
                if skip_next_empty and not line_stripped:
                    print(f"    -> Saltada (vacía post-eco)")
                    skip_next_empty = False
                    continue
                
                skip_next_empty = False
                
                # Agregar línea con contenido
                cleaned_lines.append(line_stripped)
                print(f"    -> Agregada a cleaned_lines")
            
            print(f"\n✅ Líneas finales procesadas: {len(cleaned_lines)}")
            for idx, line in enumerate(cleaned_lines):
                if line:
                    print(f"  [{idx:2d}] '{line}'")
                else:
                    print(f"  [{idx:2d}] (separador vacío)")
        
        # Desconectar
        print("\n🔌 Desconectando...")
        device_state.disconnect()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEST: Comando 'calibrate list' - Procesamiento Terminal")
    print("=" * 60)
    print("\nUso: python test_calibrate_list.py [puerto]")
    print("Ejemplo: python test_calibrate_list.py /dev/ttyACM0\n")
    
    success = test_calibrate_list()
    
    sys.exit(0 if success else 1)
