#!/usr/bin/env python3
"""
Prueba de sweep completo de 100 puntos
Este es el caso de uso real que estaba fallando
"""

import sys
import os
import logging
import time

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.admx2001 import ADMX2001
from lib.enums import SweepType, SweepScale

# Configurar logging para ver el progreso
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

print("="*70)
print("PRUEBA: Sweep de 100 puntos (caso de uso real)")
print("="*70)

try:
    # Conectar al dispositivo
    logger.info("Conectando al dispositivo...")
    device = ADMX2001(port='/dev/ttyUSB0')
    logger.info("✓ Dispositivo conectado")
    
    # Configurar un sweep realista: 0.2 Hz a 10 MHz, escala logarítmica
    logger.info("\nConfigurando sweep de 100 puntos...")
    logger.info("Rango: 0.2 Hz a 10 MHz (logarítmico)")
    
    start_time = time.time()
    
    device.configure_sweep(
        sweep_type=SweepType.FREQUENCY,
        start=0.0002,   # 0.2 Hz (en kHz)
        end=10000.0,    # 10 MHz (en kHz)
        count=100,      # 100 puntos
        scale=SweepScale.LOG
    )
    
    config_time = time.time() - start_time
    logger.info(f"✓ Sweep configurado en {config_time:.2f}s")
    
    # Ejecutar sweep
    logger.info("\n" + "="*70)
    logger.info("EJECUTANDO SWEEP DE 100 PUNTOS")
    logger.info("="*70)
    logger.info("Esto tomará aproximadamente 8-10 minutos...")
    logger.info("Progreso se mostrará cada 10 puntos...")
    
    sweep_start = time.time()
    results = device.perform_sweep()
    sweep_time = time.time() - sweep_start
    
    total_time = time.time() - start_time
    
    # Mostrar resultados
    print("\n" + "="*70)
    print("RESULTADOS DEL SWEEP")
    print("="*70)
    
    print(f"\nTiempo total: {total_time:.2f}s ({total_time/60:.2f} minutos)")
    print(f"  - Configuración: {config_time:.2f}s")
    print(f"  - Ejecución sweep: {sweep_time:.2f}s ({sweep_time/60:.2f} minutos)")
    print(f"\nPuntos recibidos: {len(results)}/100")
    
    if results:
        avg_time_per_point = sweep_time / len(results)
        print(f"Tiempo promedio por punto: {avg_time_per_point:.2f}s")
        
        # Mostrar algunos puntos de ejemplo
        print(f"\nPrimeros 5 puntos:")
        for i in range(min(5, len(results))):
            point = results[i]
            freq = point['sweep_value']
            meas = point['measurement']
            print(f"  {i+1}. Frecuencia: {freq:.2e} Hz")
            print(f"     Medición: R={meas[0]:.2e} Ω, X={meas[1]:.2e} Ω")
        
        if len(results) >= 10:
            print(f"\nÚltimos 5 puntos:")
            for i in range(len(results)-5, len(results)):
                point = results[i]
                freq = point['sweep_value']
                meas = point['measurement']
                print(f"  {i+1}. Frecuencia: {freq:.2e} Hz")
                print(f"     Medición: R={meas[0]:.2e} Ω, X={meas[1]:.2e} Ω")
        
        # Estadísticas
        print(f"\n" + "="*70)
        print("ESTADÍSTICAS")
        print("="*70)
        
        if len(results) == 100:
            print("\n✓✓✓ SWEEP COMPLETADO EXITOSAMENTE ✓✓✓")
            print(f"\nTODOS los 100 puntos fueron recibidos correctamente")
            print(f"El problema de timeout está RESUELTO")
        else:
            print(f"\n⚠ Sweep incompleto: {len(results)}/100 puntos ({len(results)}%)")
            print(f"Puntos faltantes: {100 - len(results)}")
        
        # Proyección para diferentes tamaños
        print(f"\nProyecciones de tiempo para otros sweeps:")
        for n in [10, 50, 200, 500]:
            estimated = avg_time_per_point * n
            print(f"  - {n} puntos: ~{estimated:.0f}s ({estimated/60:.1f} minutos)")
    else:
        print("\n✗ No se recibieron datos del sweep")
        print("Esto es inesperado - revisar logs arriba")
    
    # Cerrar conexión
    device.close()
    logger.info("\n✓ Dispositivo desconectado")
    
except KeyboardInterrupt:
    print("\n\n⚠ Sweep interrumpido por el usuario")
    print("Esto es normal si quieres cancelar el sweep largo")
    try:
        device.close()
    except:
        pass
    sys.exit(0)
    
except Exception as e:
    logger.error(f"\n✗ Error durante la prueba: {e}", exc_info=True)
    sys.exit(1)

print("\n" + "="*70)
print("PRUEBA COMPLETADA")
print("="*70)
