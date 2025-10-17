#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de sweep
Este script prueba el sweep paso a paso para identificar dónde falla
"""

import sys
import time
from lib import ADMX2001, DisplayMode, SweepType, SweepScale

def test_sweep_diagnostic():
    """Prueba diagnóstica del sweep"""
    
    print("="*70)
    print("DIAGNÓSTICO DE SWEEP - ADMX2001")
    print("="*70)
    
    # 1. Conectar
    print("\n1. Buscando dispositivo...")
    try:
        dev = ADMX2001.find_and_connect()
        print(f"✓ Conectado: {dev.get_idn()}")
    except Exception as e:
        print(f"✗ Error conectando: {e}")
        return
    
    # 2. Configuración básica
    print("\n2. Configurando parámetros básicos...")
    try:
        dev.set_frequency(1000)  # 1 kHz
        dev.set_magnitude(1.0)   # 1V
        dev.set_display_mode(DisplayMode.R_X)
        dev.set_mdelay(1)  # 1ms
        dev.set_tdelay(0)  # 0ms
        print("✓ Configuración aplicada")
    except Exception as e:
        print(f"✗ Error configurando: {e}")
        dev.disconnect()
        return
    
    # 3. Prueba de medición simple
    print("\n3. Probando medición simple...")
    try:
        r, x = dev.measure()
        print(f"✓ Medición OK: R={r:.2f}Ω, X={x:.2f}Ω")
    except Exception as e:
        print(f"✗ Error en medición: {e}")
        dev.disconnect()
        return
    
    # 4. Configurar sweep pequeño
    print("\n4. Configurando sweep pequeño...")
    print("   Parámetros: 1kHz -> 10kHz, lineal, 5 puntos")
    try:
        dev.configure_sweep(
            sweep_type=SweepType.FREQUENCY,
            start=1.0,      # 1 kHz
            end=10.0,       # 10 kHz
            scale=SweepScale.LINEAR,
            count=5
        )
        print("✓ Sweep configurado")
    except Exception as e:
        print(f"✗ Error configurando sweep: {e}")
        dev.disconnect()
        return
    
    # 5. Verificar estado antes del sweep
    print("\n5. Verificando estado del dispositivo...")
    try:
        # Ver si el serial buffer está limpio
        if dev.serial.in_waiting > 0:
            print(f"⚠ Hay {dev.serial.in_waiting} bytes en buffer - limpiando...")
            dev.serial.reset_input_buffer()
        print("✓ Buffer limpio")
    except Exception as e:
        print(f"⚠ Error verificando buffer: {e}")
    
    # 6. Intentar sweep con timeout largo
    print("\n6. Ejecutando sweep (timeout: 60s)...")
    print("   Esperando datos...")
    
    try:
        start_time = time.time()
        results = dev.perform_sweep(timeout=60.0)
        elapsed = time.time() - start_time
        
        print(f"\n✓ Sweep completado en {elapsed:.2f}s")
        print(f"   Puntos recibidos: {len(results)}")
        
        if results:
            print("\n   Primeros 3 puntos:")
            for i, point in enumerate(results[:3]):
                freq = point['sweep_value']
                r, x = point['measurement']
                print(f"   [{i+1}] Freq: {freq:.2f}kHz, R: {r:.2f}Ω, X: {x:.2f}Ω")
        else:
            print("   ⚠ No se recibieron datos")
            
    except TimeoutError as e:
        print(f"\n✗ Timeout: {e}")
        print("   El dispositivo no respondió a tiempo")
    except Exception as e:
        print(f"\n✗ Error en sweep: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Desconectar
    print("\n7. Desconectando...")
    try:
        dev.disconnect()
        print("✓ Desconectado")
    except Exception as e:
        print(f"⚠ Error desconectando: {e}")
    
    print("\n" + "="*70)
    print("DIAGNÓSTICO COMPLETADO")
    print("="*70)

if __name__ == "__main__":
    print("""
    Este script prueba el sweep paso a paso para diagnosticar problemas.
    
    REQUISITOS:
    - Dispositivo ADMX2001 conectado por USB
    - Muestra conectada (puede ser un resistor simple para prueba)
    
    Presione Ctrl+C para cancelar en cualquier momento.
    """)
    
    input("Presione ENTER para comenzar diagnóstico...")
    
    try:
        test_sweep_diagnostic()
    except KeyboardInterrupt:
        print("\n\n⚠ Diagnóstico cancelado por el usuario")
    except Exception as e:
        print(f"\n\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
