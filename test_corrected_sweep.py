#!/usr/bin/env python3
"""
Prueba del método perform_sweep corregido
"""

import sys
import os
import logging

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.admx2001 import ADMX2001
from lib.enums import SweepType, SweepScale

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

print("="*70)
print("PRUEBA: Sweep con método corregido (comando 'z' por cada punto)")
print("="*70)

try:
    # Conectar al dispositivo (el constructor conecta automáticamente)
    logger.info("Conectando al dispositivo...")
    device = ADMX2001(port='/dev/ttyUSB0')
    logger.info("✓ Dispositivo conectado")
    
    # Configurar un sweep pequeño de prueba
    logger.info("\nConfigurando sweep de prueba...")
    device.configure_sweep(
        sweep_type=SweepType.FREQUENCY,
        start=1.0,      # 1 kHz
        end=100.0,      # 100 kHz
        count=5,        # Solo 5 puntos para probar
        scale=SweepScale.LINEAR
    )
    logger.info("✓ Sweep configurado")
    
    # Ejecutar sweep
    logger.info("\nEjecutando sweep...")
    results = device.perform_sweep()
    
    # Mostrar resultados
    print("\n" + "="*70)
    print(f"RESULTADOS: {len(results)} puntos recibidos")
    print("="*70)
    
    if results:
        print("\nDatos del sweep:")
        for i, point in enumerate(results, 1):
            sweep_val = point['sweep_value']
            meas = point['measurement']
            print(f"  {i}. Frecuencia: {sweep_val:.2f} Hz")
            print(f"     Medición: {meas}")
        
        if len(results) == 5:
            print("\n✓✓✓ SWEEP COMPLETADO EXITOSAMENTE ✓✓✓")
        else:
            print(f"\n⚠ Sweep incompleto: {len(results)}/5 puntos")
    else:
        print("\n✗ No se recibieron datos del sweep")
    
    # Cerrar conexión
    device.close()
    logger.info("\n✓ Dispositivo desconectado")
    
except Exception as e:
    logger.error(f"\n✗ Error durante la prueba: {e}", exc_info=True)
    sys.exit(1)

print("\n" + "="*70)
print("PRUEBA COMPLETADA")
print("="*70)
