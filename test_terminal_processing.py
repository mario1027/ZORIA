#!/usr/bin/env python3
"""
Test de procesamiento de respuestas del terminal CLI
Simula la respuesta del dispositivo para calibrate open
"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

from lib.utils import clean_response_line

def test_calibrate_open_processing():
    """
    Simula el procesamiento de la respuesta de 'calibrate open'
    tal como vendría del dispositivo real
    """
    
    print("\n" + "="*70)
    print("TEST: Procesamiento de 'calibrate open'")
    print("="*70 + "\n")
    
    # Simular respuesta cruda como vendría del dispositivo
    # Basado en la salida esperada del usuario
    raw_response = [
        "calibrate open",  # Eco del comando (debería filtrarse)
        "0,-1.117998e-09,1.162904e-06",
        "Frequency = 1.0000kHz",
        "Cal Temp: 41.4 deg C",
        "open:Done",
        "short:Not Done",
        "load:Not Done"
    ]
    
    print(f"📦 RESPUESTA CRUDA ({len(raw_response)} líneas):")
    print("-" * 70)
    for idx, line in enumerate(raw_response):
        print(f"  [{idx}] '{line}'")
    
    print("\n" + "="*70)
    print("🔧 PROCESAMIENTO (simulando código de app.py)")
    print("="*70 + "\n")
    
    command = "calibrate open"
    cmd_lower = command.lower()
    is_calibrate_cmd = cmd_lower.startswith('calibrate')
    
    cleaned_lines = []
    
    for idx, line in enumerate(raw_response):
        line_stripped = line.strip()
        
        print(f"\n[Línea {idx}] Procesando: '{line_stripped}'")
        print(f"  - Vacía: {not line_stripped}")
        
        # Saltar líneas completamente vacías
        if not line_stripped:
            if is_calibrate_cmd and cleaned_lines:
                print(f"  ✓ Agregando como separador (calibrate)")
                cleaned_lines.append("")
            else:
                print(f"  ✗ Saltando (vacía)")
            continue
        
        # Filtrar eco
        is_first_line = idx == 0
        is_last_line = idx == len(raw_response) - 1
        is_echo = line_stripped.lower() == command.lower()
        
        print(f"  - Es primera línea: {is_first_line}")
        print(f"  - Es última línea: {is_last_line}")
        print(f"  - Es eco del comando: {is_echo}")
        
        if is_echo and (is_first_line or is_last_line):
            print(f"  ✗ FILTRADO (eco en primera/última línea)")
            continue
        
        # Para calibración, ser más permisivo
        if is_calibrate_cmd:
            print(f"  ✓ AGREGADO (comando de calibración)")
            cleaned_lines.append(line_stripped)
        else:
            print(f"  ✓ AGREGADO (línea normal)")
            cleaned_lines.append(line_stripped)
    
    print("\n" + "="*70)
    print(f"📋 RESULTADO FINAL ({len(cleaned_lines)} líneas)")
    print("="*70 + "\n")
    
    if cleaned_lines:
        for idx, line in enumerate(cleaned_lines):
            if line:
                print(f"  [{idx}] {line}")
            else:
                print(f"  [{idx}] (separador vacío)")
    else:
        print("  ⚠️  Lista vacía - NO SE MOSTRARÍA NADA EN EL TERMINAL")
    
    print("\n" + "="*70)
    
    # Ahora probar con clean_response_line
    print("\n🧹 TEST: Función clean_response_line()")
    print("="*70 + "\n")
    
    test_lines = [
        "0,-1.117998e-09,1.162904e-06",
        "\x1B[32mFrequency = 1.0000kHz\x1B[0m",  # Con códigos ANSI
        "ADMX2001>Cal Temp: 41.4 deg C",  # Con prompt
        "\x1B7\x1B8open:Done",  # Con VT100 codes
        "  short:Not Done  ",  # Con espacios
    ]
    
    for line in test_lines:
        cleaned = clean_response_line(line)
        print(f"Original: {repr(line)}")
        print(f"Limpia:   '{cleaned}'")
        print()

if __name__ == "__main__":
    test_calibrate_open_processing()
