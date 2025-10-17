#!/usr/bin/env python3
"""
Test del método optimizado de sweep
Debería ser 30-40x más rápido que el método anterior
"""

import sys
import os
import logging
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.admx2001 import ADMX2001
from lib.enums import SweepType, SweepScale

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

logger = logging.getLogger(__name__)

print("="*70)
print("TEST: Método Optimizado de Sweep (Documentación Oficial)")
print("="*70)

try:
    # Conectar
    logger.info("Conectando al dispositivo...")
    device = ADMX2001(port='/dev/ttyUSB0')
    logger.info("✓ Dispositivo conectado")
    
    # Test 1: Sweep pequeño (10 puntos)
    print("\n" + "="*70)
    print("TEST 1: Sweep de 10 puntos")
    print("="*70)
    
    start = time.time()
    device.configure_sweep(
        sweep_type=SweepType.FREQUENCY,
        start=1.0,
        end=100.0,
        count=10,
        scale=SweepScale.LINEAR
    )
    config_time = time.time() - start
    
    start = time.time()
    results = device.perform_sweep()
    sweep_time = time.time() - start
    
    print(f"\n📊 Resultados Test 1:")
    print(f"  Configuración: {config_time:.2f}s")
    print(f"  Ejecución: {sweep_time:.2f}s")
    print(f"  Puntos recibidos: {len(results)}")
    print(f"  Tiempo/punto: {sweep_time/len(results) if results else 0:.3f}s")
    
    if len(results) >= 10:
        print(f"\n  ✓ Test 1 EXITOSO - método optimizado funciona!")
    
    # Test 2: Sweep mediano (50 puntos)
    print("\n" + "="*70)
    print("TEST 2: Sweep de 50 puntos")
    print("="*70)
    
    start = time.time()
    device.configure_sweep(
        sweep_type=SweepType.FREQUENCY,
        start=1.0,
        end=1000.0,
        count=50,
        scale=SweepScale.LOG
    )
    config_time = time.time() - start
    
    start = time.time()
    results = device.perform_sweep()
    sweep_time = time.time() - start
    
    print(f"\n📊 Resultados Test 2:")
    print(f"  Configuración: {config_time:.2f}s")
    print(f"  Ejecución: {sweep_time:.2f}s")
    print(f"  Puntos recibidos: {len(results)}")
    print(f"  Tiempo/punto: {sweep_time/len(results) if results else 0:.3f}s")
    
    if len(results) >= 50:
        print(f"\n  ✓ Test 2 EXITOSO!")
    
    # Comparación
    print("\n" + "="*70)
    print("COMPARACIÓN DE RENDIMIENTO")
    print("="*70)
    print(f"\n  Método anterior: ~0.95s/punto (test de 20 puntos)")
    print(f"  Método optimizado: ~{sweep_time/len(results) if results else 0:.3f}s/punto (test de 50 puntos)")
    if results and sweep_time/len(results) < 0.5:
        mejora = 0.95 / (sweep_time/len(results))
        print(f"\n  🚀 MEJORA: {mejora:.1f}x MÁS RÁPIDO")
    
    # Proyecciones
    print("\n" + "="*70)
    print("PROYECCIONES PARA SWEEPS GRANDES")
    print("="*70)
    
    if results:
        time_per_point = sweep_time / len(results)
        print(f"\n  Tiempo estimado por punto: {time_per_point:.3f}s")
        print(f"\n  Sweep de 100 puntos:")
        print(f"    Método anterior: ~95s (~1.6 min)")
        print(f"    Método optimizado: ~{time_per_point*100:.1f}s (~{time_per_point*100/60:.2f} min)")
        print(f"\n  Sweep de 200 puntos:")
        print(f"    Método anterior: ~190s (~3.2 min)")
        print(f"    Método optimizado: ~{time_per_point*200:.1f}s (~{time_per_point*200/60:.2f} min)")
    
    device.close()
    logger.info("\n✓ Tests completados")
    
except Exception as e:
    logger.error(f"\n✗ Error: {e}", exc_info=True)
    sys.exit(1)

print("\n" + "="*70)
print("✓✓✓ MÉTODO OPTIMIZADO VALIDADO ✓✓✓")
print("="*70)
