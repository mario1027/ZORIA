#!/usr/bin/env python3
"""
Prueba de sweep de 20 puntos con progreso visible
"""

import sys
import os
import logging
import time

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.admx2001 import ADMX2001
from lib.enums import SweepType, SweepScale

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

logger = logging.getLogger(__name__)

print("="*70)
print("PRUEBA: Sweep de 20 puntos con progreso visible")
print("="*70)

try:
    # Conectar
    logger.info("Conectando al dispositivo...")
    device = ADMX2001(port='/dev/ttyUSB0')
    logger.info("✓ Dispositivo conectado")
    
    # Configurar sweep
    logger.info("\nConfigurando sweep de 20 puntos...")
    logger.info("Rango: 1 kHz a 1 MHz (logarítmico)")
    
    start_time = time.time()
    
    device.configure_sweep(
        sweep_type=SweepType.FREQUENCY,
        start=1.0,      # 1 kHz
        end=1000.0,     # 1 MHz
        count=20,       # 20 puntos
        scale=SweepScale.LOG
    )
    
    config_time = time.time() - start_time
    logger.info(f"✓ Configurado en {config_time:.2f}s")
    
    # Ejecutar sweep
    print("\n" + "="*70)
    print("EJECUTANDO SWEEP")
    print("="*70)
    logger.info("Tiempo estimado: ~2 minutos (20 puntos × ~5-6 seg/punto)")
    logger.info("Se mostrará progreso cada punto...")
    
    sweep_start = time.time()
    results = device.perform_sweep()
    sweep_time = time.time() - sweep_start
    
    total_time = time.time() - start_time
    
    # Resultados
    print("\n" + "="*70)
    print("RESULTADOS")
    print("="*70)
    
    print(f"\nTiempo total: {total_time:.2f}s ({total_time/60:.2f} minutos)")
    print(f"Tiempo de sweep: {sweep_time:.2f}s ({sweep_time/60:.2f} minutos)")
    print(f"\nPuntos recibidos: {len(results)}/20")
    
    if results:
        avg_time = sweep_time / len(results)
        print(f"Tiempo promedio por punto: {avg_time:.2f}s")
        
        # Primeros 3 puntos
        print(f"\nPrimeros 3 puntos:")
        for i in range(min(3, len(results))):
            point = results[i]
            freq = point['sweep_value']
            meas = point['measurement']
            print(f"  {i+1}. {freq:.2e} Hz → R={meas[0]:.2e} Ω, X={meas[1]:.2e} Ω")
        
        # Últimos 3 puntos
        if len(results) >= 6:
            print(f"\nÚltimos 3 puntos:")
            for i in range(len(results)-3, len(results)):
                point = results[i]
                freq = point['sweep_value']
                meas = point['measurement']
                print(f"  {i+1}. {freq:.2e} Hz → R={meas[0]:.2e} Ω, X={meas[1]:.2e} Ω")
        
        # Resultado
        print(f"\n" + "="*70)
        if len(results) == 20:
            print("✓✓✓ SWEEP COMPLETO ✓✓✓")
            print(f"\nProyección para 100 puntos: ~{avg_time * 100:.0f}s (~{avg_time * 100 / 60:.1f} min)")
        else:
            print(f"⚠ Incompleto: {len(results)}/20 puntos")
    else:
        print("✗ Sin datos")
    
    device.close()
    logger.info("\n✓ Desconectado")
    
except KeyboardInterrupt:
    print("\n\n⚠ Interrumpido por usuario")
    try:
        device.close()
    except:
        pass
    sys.exit(0)
    
except Exception as e:
    logger.error(f"\n✗ Error: {e}", exc_info=True)
    sys.exit(1)

print("\n" + "="*70)
print("PRUEBA COMPLETADA")
print("="*70)
