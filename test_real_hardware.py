#!/usr/bin/env python3
"""
Pruebas REALES con hardware ADMX2001
Ejecuta barridos reales y mide tiempos, verifica datos recibidos
"""

import sys
import time
from datetime import datetime
from lib.admx2001 import ADMX2001
from lib.enums import SweepType, SweepScale

def find_device():
    """Intenta encontrar el dispositivo en puertos comunes"""
    common_ports = [
        '/dev/ttyUSB0',
        '/dev/ttyUSB1',
        '/dev/ttyACM0',
        'COM3',
        'COM4',
        'COM5'
    ]
    
    print("🔍 Buscando dispositivo ADMX2001...")
    for port in common_ports:
        try:
            print(f"   Probando {port}...", end=' ')
            device = ADMX2001(port=port, baudrate=115200, timeout=2)
            device.connect()
            identity = device.get_identity()
            print(f"✅ ENCONTRADO: {identity}")
            return device
        except Exception as e:
            print(f"❌")
            continue
    
    return None


def test_real_sweep(device, points, start=100, stop=100000, scale='log'):
    """Ejecuta un barrido real y mide rendimiento"""
    
    print(f"\n{'='*80}")
    print(f"🧪 BARRIDO REAL: {points} puntos, {start}-{stop} Hz, escala {scale}")
    print(f"{'='*80}")
    
    try:
        # Configurar parámetros
        device.set_frequency(1000)  # Frecuencia base
        device.set_magnitude(1.0)   # 1V
        device.set_average(1)       # Sin promediado para rapidez
        
        # Configurar barrido
        sweep_scale = SweepScale.LOG if scale == 'log' else SweepScale.LINEAR
        
        print(f"⚙️  Configurando barrido...")
        print(f"   • Inicio: {start} Hz")
        print(f"   • Fin: {stop} Hz")
        print(f"   • Puntos: {points}")
        print(f"   • Escala: {scale}")
        
        device.configure_sweep(
            SweepType.FREQUENCY,
            start / 1000,  # Hz a kHz
            stop / 1000,
            sweep_scale,
            points
        )
        
        # Ejecutar barrido y medir tiempo
        print(f"\n🚀 Ejecutando barrido...")
        start_time = time.time()
        
        results = device.execute_sweep()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Analizar resultados
        if results and len(results) > 0:
            received_points = len(results)
            time_per_point = elapsed / received_points
            
            print(f"\n✅ BARRIDO COMPLETADO")
            print(f"   • Puntos solicitados: {points}")
            print(f"   • Puntos recibidos: {received_points}")
            print(f"   • Tiempo total: {elapsed:.2f} segundos ({elapsed/60:.2f} min)")
            print(f"   • Tiempo por punto: {time_per_point:.2f} s")
            print(f"   • Estado: {'✅ OK' if received_points == points else '⚠️ DISCREPANCIA'}")
            
            # Verificar calidad de datos
            freqs = [r['frequency'] for r in results]
            mags = [r['magnitude'] for r in results]
            
            print(f"\n📊 Calidad de datos:")
            print(f"   • Rango frecuencias: {min(freqs):.2f} - {max(freqs):.2f} Hz")
            print(f"   • Rango magnitudes: {min(mags):.2e} - {max(mags):.2e} Ω")
            print(f"   • Datos válidos: {len([m for m in mags if m > 0])} / {len(mags)}")
            
            return {
                'success': True,
                'points_requested': points,
                'points_received': received_points,
                'time_total': elapsed,
                'time_per_point': time_per_point,
                'match': received_points == points
            }
        else:
            print(f"\n❌ ERROR: No se recibieron datos")
            return {'success': False, 'error': 'No data received'}
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {'success': False, 'error': str(e)}


def run_comprehensive_test(device):
    """Ejecuta pruebas progresivas con el hardware real"""
    
    print("\n" + "="*80)
    print("🔬 PRUEBAS PROGRESIVAS CON HARDWARE REAL")
    print("="*80)
    
    # Pruebas progresivas - aumentando complejidad
    test_configs = [
        (10, 1000, 10000, 'log', 'Mínimo (verificación rápida)'),
        (50, 100, 100000, 'log', 'Pequeño (screening)'),
        (100, 100, 100000, 'log', 'Rápido (5 min estimados)'),
        (255, 100, 100000, 'log', 'Óptimo 1 segmento (13 min)'),
        (500, 100, 100000, 'log', 'Estándar 2 segmentos (25 min)'),
        # Descomentar para pruebas largas:
        # (1000, 100, 100000, 'log', 'Alta resolución (50 min)'),
        # (2000, 100, 100000, 'log', 'Muy alta (100 min)'),
    ]
    
    results = []
    
    for points, start, stop, scale, description in test_configs:
        print(f"\n{'─'*80}")
        print(f"📋 {description}")
        
        # Preguntar al usuario si continuar con pruebas largas
        if points > 255:
            response = input(f"\n⏱️  Esta prueba tomará ~{points*3/60:.0f} min. ¿Continuar? (s/n): ")
            if response.lower() != 's':
                print("⏭️  Saltando prueba...")
                continue
        
        result = test_real_sweep(device, points, start, stop, scale)
        result['description'] = description
        results.append(result)
        
        # Pausa entre pruebas
        if len(results) < len(test_configs):
            print("\n⏸️  Esperando 3 segundos antes de siguiente prueba...")
            time.sleep(3)
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE PRUEBAS REALES")
    print("="*80)
    
    print(f"\n{'Puntos':<8} {'Estado':<10} {'Tiempo':<12} {'Tiempo/pt':<12} {'Descripción':<30}")
    print("-" * 80)
    
    for r in results:
        if r['success']:
            status = "✅ OK" if r['match'] else "⚠️ Disc"
            print(f"{r['points_requested']:<8} {status:<10} "
                  f"{r['time_total']/60:>5.1f} min    "
                  f"{r['time_per_point']:>5.2f} s/pt    "
                  f"{r['description']:<30}")
        else:
            print(f"{'N/A':<8} {'❌ ERROR':<10} {'N/A':<12} {'N/A':<12} {r['description']:<30}")
    
    # Estadísticas
    successful = [r for r in results if r['success'] and r['match']]
    if successful:
        avg_time_per_point = sum(r['time_per_point'] for r in successful) / len(successful)
        print(f"\n📈 Estadísticas:")
        print(f"   • Pruebas exitosas: {len(successful)} / {len(results)}")
        print(f"   • Tiempo promedio por punto: {avg_time_per_point:.2f} s")
        print(f"   • Estimación para 1000 pts: {avg_time_per_point * 1000 / 60:.1f} min")
        print(f"   • Estimación para 5000 pts: {avg_time_per_point * 5000 / 60:.1f} min")
        print(f"   • Estimación para 10000 pts: {avg_time_per_point * 10000 / 60:.1f} min")
    
    return results


def main():
    print("\n" + "="*80)
    print("🔧 PRUEBA REAL CON HARDWARE ADMX2001")
    print("="*80)
    print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Buscar dispositivo
    device = find_device()
    
    if not device:
        print("\n❌ ERROR: No se pudo encontrar el dispositivo ADMX2001")
        print("\n💡 Sugerencias:")
        print("   1. Verifica que el dispositivo esté conectado")
        print("   2. Verifica permisos del puerto serial (sudo usermod -a -G dialout $USER)")
        print("   3. Verifica que el puerto esté disponible (ls /dev/tty*)")
        sys.exit(1)
    
    print("\n✅ Dispositivo encontrado y conectado")
    
    try:
        # Ejecutar pruebas
        results = run_comprehensive_test(device)
        
        print("\n" + "="*80)
        print("✅ PRUEBAS COMPLETADAS")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por usuario")
    except Exception as e:
        print(f"\n\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔌 Desconectando dispositivo...")
        try:
            device.disconnect()
            print("✅ Desconectado correctamente")
        except:
            pass


if __name__ == "__main__":
    main()
