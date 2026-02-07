#!/usr/bin/env python3
"""
Simula posibles formatos de salida de 'calibrate list' para identificar
cuál es el formato real que usa el ADMX2001.
"""

def test_format_1():
    """Formato 1: Lista simple de frecuencias"""
    print("\n" + "="*60)
    print("FORMATO 1: Lista simple de frecuencias")
    print("="*60)
    
    simulated_response = [
        "1000",
        "5000",
        "10000",
        "50000",
        "100000"
    ]
    
    print("Respuesta simulada:")
    for line in simulated_response:
        print(f"  {line}")
    
    print("\nParseo:")
    for line in simulated_response:
        try:
            freq = float(line)
            print(f"  Frecuencia: {freq} Hz")
        except:
            print(f"  Error: '{line}' no es un número")
    
    return simulated_response

def test_format_2():
    """Formato 2: Frecuencias con unidades"""
    print("\n" + "="*60)
    print("FORMATO 2: Frecuencias con unidades")
    print("="*60)
    
    simulated_response = [
        "1000 Hz",
        "5000 Hz",
        "10000 Hz",
        "50000 Hz",
        "100000 Hz"
    ]
    
    print("Respuesta simulada:")
    for line in simulated_response:
        print(f"  {line}")
    
    print("\nParseo:")
    for line in simulated_response:
        try:
            parts = line.split()
            freq = float(parts[0])
            unit = parts[1] if len(parts) > 1 else "Hz"
            print(f"  Frecuencia: {freq} {unit}")
        except:
            print(f"  Error parseando: '{line}'")
    
    return simulated_response

def test_format_3():
    """Formato 3: Formato estructurado con etiquetas"""
    print("\n" + "="*60)
    print("FORMATO 3: Formato con etiquetas")
    print("="*60)
    
    simulated_response = [
        "Freq: 1000 Hz",
        "Freq: 5000 Hz",
        "Freq: 10000 Hz",
        "Freq: 50000 Hz",
        "Freq: 100000 Hz"
    ]
    
    print("Respuesta simulada:")
    for line in simulated_response:
        print(f"  {line}")
    
    print("\nParseo:")
    import re
    for line in simulated_response:
        match = re.search(r'Freq:\s*(\d+)\s*(Hz|kHz)?', line)
        if match:
            freq = float(match.group(1))
            unit = match.group(2) if match.group(2) else "Hz"
            print(f"  Frecuencia: {freq} {unit}")
        else:
            print(f"  Error parseando: '{line}'")
    
    return simulated_response

def test_format_4():
    """Formato 4: Formato con configuraciones de ganancia (calibrate list <freq>)"""
    print("\n" + "="*60)
    print("FORMATO 4: Con configuraciones de ganancia")
    print("="*60)
    print("(Este es probablemente el formato de 'calibrate list <freq>')")
    print("="*60)
    
    simulated_response = [
        "CH0=0 CH1=0",
        "CH0=0 CH1=1",
        "CH0=1 CH1=0",
        "CH0=1 CH1=1",
        "CH0=2 CH1=2",
        "CH0=3 CH1=3"
    ]
    
    print("Respuesta simulada:")
    for line in simulated_response:
        print(f"  {line}")
    
    print("\nParseo:")
    for line in simulated_response:
        try:
            parts = line.strip().split()
            gain_config = {}
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    gain_config[key] = value
            
            ch0 = gain_config.get('CH0', '?')
            ch1 = gain_config.get('CH1', '?')
            print(f"  Ganancia CH0={ch0}, CH1={ch1}")
        except:
            print(f"  Error parseando: '{line}'")
    
    return simulated_response

def test_format_5():
    """Formato 5: Formato completo con frecuencia y ganancias"""
    print("\n" + "="*60)
    print("FORMATO 5: Frecuencia + Ganancias")
    print("="*60)
    
    simulated_response = [
        "FREQ=1000 CH0=0 CH1=0",
        "FREQ=1000 CH0=0 CH1=1",
        "FREQ=5000 CH0=1 CH1=0",
        "FREQ=10000 CH0=2 CH1=2",
        "FREQ=50000 CH0=3 CH1=3"
    ]
    
    print("Respuesta simulada:")
    for line in simulated_response:
        print(f"  {line}")
    
    print("\nParseo:")
    calibrations = {}
    for line in simulated_response:
        try:
            parts = line.strip().split()
            data = {}
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    data[key.upper()] = value
            
            freq = data.get('FREQ', '?')
            ch0 = data.get('CH0', '?')
            ch1 = data.get('CH1', '?')
            
            if freq not in calibrations:
                calibrations[freq] = []
            calibrations[freq].append({'CH0': ch0, 'CH1': ch1})
            
            print(f"  Frecuencia: {freq} Hz, Ganancia CH0={ch0}, CH1={ch1}")
        except:
            print(f"  Error parseando: '{line}'")
    
    print("\nResumen por frecuencia:")
    for freq, configs in calibrations.items():
        print(f"  {freq} Hz: {len(configs)} configuraciones calibradas")
    
    return simulated_response

def recommend_implementation():
    """Recomienda cómo implementar el parseo"""
    print("\n" + "="*60)
    print("RECOMENDACIÓN DE IMPLEMENTACIÓN")
    print("="*60)
    
    print("""
Basándome en la documentación oficial:

1. 'calibrate list' → Lista FRECUENCIAS con calibración guardada
   Formato esperado: Probablemente FORMATO 1, 2 o 3
   Ejemplos: "1000", "1000 Hz", o "Freq: 1000 Hz"
   
2. 'calibrate list <freq>' → Lista CONFIGURACIONES DE GANANCIA a esa frecuencia
   Formato esperado: FORMATO 4
   Ejemplo: "CH0=0 CH1=0"

SOLUCIÓN PROPUESTA:
--------------------
Implementar un parseo robusto que:

a) Primero intente detectar si la línea tiene formato de ganancia (CH0=, CH1=)
   → Si SÍ: es respuesta de 'calibrate list <freq>'
   → Si NO: es respuesta de 'calibrate list' (solo frecuencias)

b) Para frecuencias solamente:
   - Extraer cualquier número que parezca frecuencia
   - Ignorar unidades si están presentes
   - Usar regex: r'(\\d+)\\s*(Hz|kHz)?'

c) Para combinaciones frecuencia + ganancia:
   - Parsear como diccionario clave=valor
   - Agrupar por frecuencia
   - Mostrar configuraciones disponibles

d) Fallback:
   - Si el parseo falla, mostrar línea completa como texto crudo
   - Marcar con advertencia para debugging
""")

if __name__ == "__main__":
    print("="*60)
    print("ANÁLISIS DE FORMATOS POSIBLES: 'calibrate list'")
    print("="*60)
    
    test_format_1()
    test_format_2()
    test_format_3()
    test_format_4()
    test_format_5()
    recommend_implementation()
    
    print("\n" + "="*60)
    print("SIGUIENTE PASO:")
    print("="*60)
    print("""
1. Conectar el ADMX2001 real
2. Ejecutar 'calibrate list' desde el terminal CLI del Dashboard
3. Observar el formato real de salida
4. Actualizar el callback en pages/calibration/calibration_page.py
   con el formato correcto
""")
