#!/usr/bin/env python3
"""
Script para respaldar calibraciones del ADMX2001 antes de actualizar firmware.
Guarda todas las calibraciones en un archivo de texto con timestamp.
"""

import sys
from datetime import datetime
from pathlib import Path

try:
    from lib.admx2001 import ADMX2001
    import serial.tools.list_ports
except ImportError:
    print("Error: No se pueden importar módulos necesarios")
    print("Ejecuta este script desde la carpeta raíz de ZORIA")
    sys.exit(1)

def find_device():
    """Busca y conecta al ADMX2001"""
    print("Buscando ADMX2001...")
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        try:
            device = ADMX2001(port.device, baudrate=115200, timeout=3)
            response = device.send_command("*IDN?")
            if response and isinstance(response, list):
                response = '\n'.join(response)
            
            if response and "ADMX2001" in response:
                print(f"✓ Dispositivo encontrado: {port.device}")
                print(f"  {response.strip()}")
                return device
            device.close()
        except:
            pass
    
    print("✗ No se encontró ADMX2001")
    return None

def backup_calibrations(device):
    """Respalda todas las calibraciones"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"calibration_backup_{timestamp}.txt"
    
    print(f"\n{'='*70}")
    print("RESPALDO DE CALIBRACIONES")
    print(f"{'='*70}\n")
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("="*70 + "\n")
        f.write("RESPALDO DE CALIBRACIONES - ADMX2001\n")
        f.write("="*70 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Generado por: ZORIA Calibration Backup Script\n")
        f.write("="*70 + "\n\n")
        
        # Device info
        print("Obteniendo información del dispositivo...")
        idn = device.send_command("*IDN?")
        if idn:
            f.write("INFORMACIÓN DEL DISPOSITIVO:\n")
            f.write("-"*70 + "\n")
            if isinstance(idn, list):
                for line in idn:
                    f.write(f"{line}\n")
                    print(f"  {line}")
            else:
                f.write(f"{idn}\n")
                print(f"  {idn}")
            f.write("\n")
        
        # Calibration list
        print("\nObteniendo lista de calibraciones...")
        cal_list = device.calibration.list_calibrations()
        
        if not cal_list or len(cal_list) == 0:
            print("⚠ No hay calibraciones guardadas en el dispositivo")
            f.write("No hay calibraciones guardadas.\n")
            return backup_file
        
        f.write("LISTA DE CALIBRACIONES:\n")
        f.write("-"*70 + "\n")
        f.write("Comando ejecutado: calibrate list\n")
        f.write("Respuesta:\n\n")
        
        frequencies = []
        print("\nCalibration disponibles:")
        
        for line in cal_list:
            f.write(f"{line}\n")
            print(f"  {line}")
            
            # Intentar extraer frecuencia
            import re
            freq_match = re.search(r'(\d+)', line)
            if freq_match:
                freq = freq_match.group(1)
                if freq not in frequencies:
                    frequencies.append(freq)
        
        f.write("\n")
        
        # Para cada frecuencia, obtener detalles
        if frequencies:
            print(f"\nEncontraron {len(frequencies)} frecuencias calibradas")
            print("Obteniendo detalles de cada frecuencia...\n")
            
            f.write("="*70 + "\n")
            f.write("DETALLES DE CALIBRACIONES POR FRECUENCIA\n")
            f.write("="*70 + "\n\n")
            
            for freq in frequencies:
                print(f"  Frecuencia: {freq} Hz")
                f.write(f"FRECUENCIA: {freq} Hz\n")
                f.write("-"*70 + "\n")
                f.write(f"Comando ejecutado: calibrate list {freq}\n")
                f.write("Respuesta:\n\n")
                
                try:
                    details = device.send_command(f"calibrate list {freq}")
                    if details:
                        if isinstance(details, list):
                            for line in details:
                                f.write(f"  {line}\n")
                                print(f"    {line}")
                        else:
                            f.write(f"  {details}\n")
                            print(f"    {details}")
                    else:
                        f.write("  (Sin respuesta)\n")
                        print("    (Sin respuesta)")
                except Exception as e:
                    f.write(f"  Error: {e}\n")
                    print(f"    Error: {e}")
                
                f.write("\n")
        else:
            print("⚠ No se pudieron extraer frecuencias del formato de respuesta")
            print("  Los datos crudos están guardados en el archivo")
        
        # Footer
        f.write("="*70 + "\n")
        f.write("FIN DEL RESPALDO\n")
        f.write("="*70 + "\n")
        f.write("\nIMPORTANTE:\n")
        f.write("- Guardar este archivo en lugar seguro\n")
        f.write("- Necesario para restaurar calibraciones después de actualización\n")
        f.write("- Si la actualización borra las calibraciones, será necesario\n")
        f.write("  recalibrar o restaurar manualmente\n")
    
    return backup_file

def main():
    print("="*70)
    print("RESPALDO DE CALIBRACIONES ADMX2001")
    print("="*70)
    print("\n⚠️  IMPORTANTE: Este respaldo es CRÍTICO antes de actualizar firmware")
    print("   La actualización puede borrar todas las calibraciones guardadas\n")
    
    # Buscar dispositivo
    device = find_device()
    if not device:
        print("\n✗ No se puede continuar sin dispositivo conectado")
        sys.exit(1)
    
    try:
        # Hacer respaldo
        backup_file = backup_calibrations(device)
        
        print(f"\n{'='*70}")
        print("✓ RESPALDO COMPLETADO")
        print(f"{'='*70}")
        print(f"\nArchivo guardado: {backup_file}")
        print(f"Ubicación: {Path(backup_file).absolute()}")
        
        # Verificar archivo
        size = Path(backup_file).stat().st_size
        print(f"Tamaño: {size} bytes")
        
        print("\n📋 Próximos pasos:")
        print("  1. Verificar el contenido del archivo de respaldo")
        print("  2. Guardar copia en lugar seguro (USB, cloud, etc.)")
        print("  3. Proceder con obtención de firmware y Quartus")
        print("  4. Cuando tengas todo, ejecutar actualización")
        print("  5. Después de actualizar, verificar si calibraciones se perdieron")
        print("  6. Si es necesario, recalibrar usando este respaldo como referencia")
        
        print("\n✓ Ahora es seguro proceder con la actualización")
        
    except Exception as e:
        print(f"\n✗ Error durante respaldo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        device.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Respaldo cancelado por el usuario")
        sys.exit(1)
